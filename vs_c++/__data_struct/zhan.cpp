#include <stdio.h>
#include <stdlib.h>
#define MAX_SIZE 100 // 定义栈的最大容量
#include <iostream>
using namespace std;

typedef struct{
    SElemType *base;
    SElemType *top;
    int stacksize;//当前可用量大小
}SqStack;

Status InitStack(SqStack &S)
{// 构造一个空栈S
  S.base=(ElemType*)malloc(STACK_INIT_SIZE*sizeof(ElemType));
   if(!S.base) exit(OVERFLOW); //存储分配失败
   S.top = S.base;
   S.stacksize = STACK_INIT_SIZE;
   return OK;
}

Status Push(SqStack &S, SElemType e)
{
   if (S.top - S.base >= S.stacksize) {//栈满，追加存储空间
      S.base = (ElemType*)realloc(S.base,
                (S.stacksize + STACKINCREMENT) * sizeof(ElemType));
       if (!S.base) exit (OVERFLOW); //存储分配失败
       S.top = S.base + S.stacksize;//该语句是否必要?
       S.stacksize += STACKINCREMENT;
   }
   *S.top++ = e; //入栈后修改栈顶指针
    return OK;
}

Status Pop (SqStack &S, SElemType &e)
{
     // 若栈不空，则删除S的栈顶元素，
     // 用e返回其值，并返回OK；
     // 否则返回ERROR
    if (S.top == S.base) return ERROR;
    e = *--S.top; //退e后修改栈顶
    return OK;
}

//链式栈
typedef struct SNode{
    SElemType data;
    struct SNode *next;
}SNode, *LinkStack;

/*应用*/
//数制转换 10 转 8
void conversation_int()
{
    SqStack S; int N; int e;
    InitStack(S);
    printf("输入N:");
    scanf("%d",&N);
    printf("转换后的值为:")
    while(N)
    {
        Push(S,N % 8);//进栈
        N /= 8;
    }
    while(S.top != S.base)
    {
        Pop(S,e);//出栈
        print("%d",e);
    }
}

void conversation_float()
{
    SqStack S; 
    double N; // 修改为 double 类型以处理小数
    int integerPart;
    double fractionalPart;
    int e;

    InitStack(S);
    printf("输入N:");
    scanf("%lf", &N); // 使用 %lf 读取 double 类型

    // 分离整数部分和小数部分
    integerPart = (int)N; // 整数部分
    fractionalPart = N - integerPart; // 小数部分

    printf("转换后的值为:");

    // 处理整数部分
    while (integerPart)
    {
        Push(S, integerPart % 8);
        integerPart /= 8;
    }
    // 输出整数部分
    while (S.top != S.base)
    {
        Pop(S, e);
        printf("%d", e);
    }
    // 处理小数部分
    if (fractionalPart > 0)
    {
        printf("."); // 输出小数点
        int count = 0; // 控制小数位数
        while (fractionalPart > 0 && count < 5) // 限制小数位数为5位
        {
            fractionalPart *= 8;
            int fractionalDigit = (int)fractionalPart; // 获取八进制位
            printf("%d", fractionalDigit);
            fractionalPart -= fractionalDigit; // 更新小数部分
            count++;
        }
    }
    printf("\n"); // 换行
}

typedef struct {
    char data[MAX_SIZE];
    int top;
} Stack;

// 初始化栈
void initStack(Stack* s) {
    s->top = -1;
}

// 判断栈是否为空
int isEmpty(Stack* s) {
    return s->top == -1;
}

// 入栈
void push(Stack* s, char c) {
    if (s->top < MAX_SIZE - 1) {
        s->data[++(s->top)] = c;
    }
}

// 出栈
char pop(Stack* s) {
    if (!isEmpty(s)) {
        return s->data[(s->top)--];
    }
    return '\0'; // 返回空字符表示栈为空
}

// 检查括号匹配
int isMatching(char left, char right) {
    return (left == '(' && right == ')') ||
           (left == '{' && right == '}') ||
           (left == '[' && right == ']');
}

// 主函数     
int Check() {
    STACK S;        // 定义栈结构 S
    char ch;
    InitStack(&S);  // 初始化栈 S

    while ((ch = getchar()) != '\n') { // 以字符序列的形式输入表达式
        switch (ch) {
            case '(': // 遇左括号入栈
            case '[':
            case '{':
                Push(&S, ch);
                break;
            // 在遇到右括号时，分别检测匹配情况
            case ')':
                if (StackEmpty(S)) return 0;     
                else {
                    Pop(&S, &ch);
                    if (ch != '(') return 0;
                }
                break;
            case ']':
                if (StackEmpty(S)) return 0;    
                else {
                    Pop(&S, &ch);
                    if (ch != '[') return 0;
                }
                break;
            case '}':
                if (StackEmpty(S)) return 0;
                else {
                    Pop(&S, &ch);
                    if (ch != '{') return 0;
                }
                break;
            default:
                break;
        } // switch end
    } // while end

    if (StackEmpty(S)) return 1;    
    else return 0;
}

/*
int main() {
    printf("请输入表达式: ");
    if (Check()) {
        printf("括号匹配\n");
    } else {
        printf("括号不匹配\n");
    }
    return 0;
}
*/
OperandType EvaluateExpression() {
    // 设OPTR和OPND分别为运算符栈和运算数栈，OP为运算符集合。
    InitStack(OPTR); Push(OPTR, '#');
    InitStack(OPND);
    c = getchar();
    while (c != '#' || GetTop(OPTR) != '#') { // 当前符号是#并且栈顶也是#时结束
        if (!In(c, OP)) {Push(OPND, c); c = getchar();} // 是操作数
        else {
            switch (Precede(GetTop(OPTR), c)) //确定运算符的优先级 
            {
                case '<': // 栈顶元素优先权低
                    Push(OPTR, c); 
                    c = getchar();
                    break;
                case '=': // 优先权相等，脱括号并接收下一个字符
                    Pop(OPTR, x); 
                    c = getchar();
                    break;
                case '>': // 栈顶元素优先权高，退栈并将运算结果入栈
                    Pop(OPTR, theta); 
                    Pop(OPND, b); 
                    Pop(OPND, a); 
                    Push(OPND, Operate(a, theta, b));
                    break;
            } // switch
        } // else
    } // while
    return GetTop(OPND); // 操作数栈顶上保存的就是最终结果
}
