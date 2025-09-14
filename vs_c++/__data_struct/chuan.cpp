#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 状态码定义
#define OK 1
#define ERROR 0
#define OVERFLOW -1
typedef int Status;

// 块大小定义（用于链式存储）
#define CHUNKSIZE 80

// 定长顺序存储表示
#define MAXSTRLEN 255
typedef unsigned char SString[MAXSTRLEN + 1];  // SString[0]存储串长

// 堆分配存储表示(常用)
typedef struct {
    char *ch;      // 存储串的字符数组，非空串时按长度分配
    int length;    // 串的长度
} HString;

// 链式存储的块结构
typedef struct Chunk {
    char data[CHUNKSIZE];
    struct Chunk *next;
} Chunk;

// 链式存储的串结构
typedef struct LString {
    Chunk *head, *tail;  // 指向链表的头、尾块
    int curlen;          // 串的当前长度
} LString;

// 用T返回由S1和S2连接而成的新串
Status Concat(HString &T, HString S1, HString S2) {
    // 释放T的旧空间
    if (T.ch) free(T.ch);
    
    // 分配新空间
    T.ch = (char *)malloc((S1.length + S2.length) * sizeof(char));
    if (!T.ch) exit(OVERFLOW);
    
    // 复制S1的内容
    memcpy(T.ch, S1.ch, S1.length * sizeof(char));
    // 复制S2的内容
    memcpy(T.ch + S1.length, S2.ch, S2.length * sizeof(char));
    
    // 设置新串长度
    T.length = S1.length + S2.length;
    return OK;
}

// 用Sub返回串S的第pos个字符起长度为len的子串
Status SubString(HString &Sub, HString S, int pos, int len) {
    // 检查参数合法性（pos从1开始）
    if (pos < 1 || pos > S.length || len < 0 || len > S.length - pos + 1) {
        return ERROR;
    }
    
    // 释放Sub的旧空间
    if (Sub.ch) free(Sub.ch);
    
    // 处理空子串情况
    if (len == 0) {
        Sub.ch = NULL;
        Sub.length = 0;
        return OK;
    }
    
    // 分配空间并复制子串
    Sub.ch = (char *)malloc(len * sizeof(char));
    if (!Sub.ch) exit(OVERFLOW);
    
    // 复制从pos-1开始的len个字符（S的字符从0开始存储）
    memcpy(Sub.ch, S.ch + pos - 1, len * sizeof(char));
    Sub.length = len;
    
    return OK;
}

// 朴素模式匹配算法
int INDEX(SString S, SString T, int pos) {
    int i = pos;  // 主串当前位置（从1开始）
    int j = 1;    // 模式串当前位置（从1开始）
    
    // S[0]和T[0]存储串的长度
    while (i <= S[0] && j <= T[0]) {
        if (S[i] == T[j]) {
            i++;  // 继续比较下一个字符
            j++;
        } else {
            // 回溯：主串回到上次匹配开始位置的下一个，模式串回到开头
            i = i - j + 2;
            j = 1;
        }
    }
    
    // 如果模式串匹配完成，返回匹配的起始位置
    if (j > T[0]) {
        return i - T[0];
    } else {
        return 0;  // 匹配失败
    }
}

// 求模式串T的next函数值并存入数组next
void get_next(SString T, int next[]) {
    int j = 1;    // 模式串当前位置
    next[1] = 0;  // 第一个字符的next值为0
    int k = 0;    // k表示当前最长前缀后缀的长度
    
    while (j < T[0]) {  // T[0]是模式串长度
        if (k == 0 || T[j] == T[k]) {
            j++;
            k++;
            next[j] = k;
        } else {
            k = next[k];  // 回溯k
        }
    }
}

// KMP模式匹配算法
int Index_KMP(SString S, SString T, int pos) {
    int i = pos;  // 主串当前位置（从1开始）
    int j = 1;    // 模式串当前位置（从1开始）
    int next[T[0] + 1];  // next数组，存储模式串的部分匹配值
    
    get_next(T, next);  // 计算模式串的next数组
    
    while (i <= S[0] && j <= T[0]) {  // S[0]为主串长度，T[0]为模式串长度
        if (j == 0 || S[i] == T[j]) {
            i++;  // 继续比较下一个字符
            j++;
        } else {
            j = next[j];  // 模式串向右移动，主串不回溯
        }
    }
    
    // 如果模式串匹配完成，返回匹配的起始位置
    if (j > T[0]) {
        return i - T[0];
    } else {
        return 0;  // 匹配失败
    }
}
