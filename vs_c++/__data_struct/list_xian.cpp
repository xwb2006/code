#include <iostream>
using namespace std;
#define LIST_SIZE 100
#define LISTINCREMENT 10 /*设置固定的额外内存开辟量*/

typedef int Elemtype; //定义Elemytpe 的格式为int类（方便修改）
//定义 list 性质
typedef struct{
    Elemtype *elem;
    int length;//目前长度
    int listsize;//开辟长度 -->> MAX
}SqList;
//创造list
Status InitList_Sq(SqList &L)
{
    L.elem = (ElemType*)malloc(LIST_SIZE*sizeof(ElemType))
    if(!L.elem) exit(OVERFLOW);
    L.length = 0;
    L.listsize = LIST_SIZE;
    return OK;
}

Status ListInsert_Sq(Sqlist &L, int i, ElemType e)
{
    if(i<1 || i>L.length+1) return ERROR;
    if(L.length >= L.listsize)//空间不够
    {
        newbase = (ElemType*)realloc(L.elem,
        (L.listsize+LISTINCREMENT)*sizeof(ElemType));
        if(!newbase) exit(OVERFLOW);

        L.elem = newbase;   //拷贝到新内存的区域
        L.listsize += LISTINCREMENT;
    }
    q = &L.elem[i-1];
    for(p = &L.elem[L.length-1]; p>=q; --p)
    {
        *(p+1) = *p;
    }
    *q = e;
    ++L.length; //严谨
    return OK;
}

Status ListDelete_Sq(Sqlist &L, int i, ElemType &e)
{   // 在顺序线性表L中删除第i个元素，并用e返回其值
    if(i<1 || i>L.length) return ERROR;
    p = &L.elem[i-1]; //p为要删除元素的地址
    e = *p; //用e返回其值
    q = L.elem + L.length - 1;
    for(++p; p<=q; ++p)
    {
        *(p-1) = *p;
    }
    --L.length;
    return OK;
}
//指针函数(返回指针类型)
//int *f(int n)
//函数指针(返回函数类型)
//int (*p)(int n);

int LocateElem_L(LinkList L, ElemType e,
Status (*compare)(ElemType, ElemType))
{
    i = 1;
    p = L.elem;
    while(i <= L.length && !(*compare)(*p++, e)) ++i;
    if(i <= L.length) return i;
    else return 0;
}

void Union(List &La, List &Lb)
{
    la_len = ListLength(La);
    lb_len = ListLength(Lb);
    for(i=1; i<=lb_len; i++)
    {
        GetElem_L(Lb, i, e);    //取元素
        if(!LocateElem_L(La, e, equal)) //A中没找到
            ListInsert_L(La, ++la_len, e);
    }
}


typedef struct LNode{
    ElemType data;
    struct LNode *next; //指针域
}LNode, *LinkList;
//创造list
Status InitList_L(LinkList &L)
{
    L = (LinkList)malloc(sizeof(LNode));
}

Status GetElem_L(LinkList L, int i, ElemType &e) //获取第i个元素
{
    p = L; //p为头节点
    j=0; //j为计数器
    while(p && j < i)  
    {
        p = p->next; ++j;
    }
    if(!p || j > i) return ERROR;
    e = p->data;
    return OK;
}

Status ListInsert_L(LinkList &L, int i, ElemType e)
{
    p = L; j=0;
    while(p && j < i)
    {
        p = p->next; ++j;
    }
    if(!p || j > i) return ERROR;
    s = (LinkList)malloc(sizeof(LNode));
    s->data = e;
    s->next = p->next;  //节点S 接上 原来p的下一个节点
    p->next = s;    //p 接上 s
    return OK;
}

Status ListDelete_L(LinkList &L, int i, ElemType &e)
{
    p = L; j=0;
    while(p->next && j < i)
    {
        p = p->next; ++j;
    }
    if(!(p->next) || j > i) return ERROR;
    q = p->next;    //q为要删除的节点
    p->next = q->next; //将q的下一个节点赋值给p的下一个节点
    e = q->data; //将q的值赋值给e
    free(q); //释放q
    return OK;
}

void CreateList_L(LinkList &L, int n)
{ //逆位序输入n个元素的值，建立带表头节点的单链线性表L
    L = (LinkList)malloc(sizeof(LNode));
    L->next = NULL; //头节点
    for(i=n; i>0; --i)
    {
        p = (LinkList)malloc(sizeof(LNode)); //创建新节点
        cin >> p->data; //输入新节点的数据
        p->next = L->next; //将新节点的下一个节点赋值给头节点的下一个节点
        L->next = p; //将新节点赋值给头节点的下一个节点
    }
}

void MergeList_L(LinkList &La, LinkList &Lb, LinkList &Lc)
{ //将A,B合并为一个有序单链表（比较+指针p）
    pa = La->next;
    pb = Lb->next;
    pc = Lc = La;   //分别指向lc链尾
    while(pa && pb)
    {
        if(pa->data <= pb->data)
        {
            pc->next = pa;  //pa储存的地址给pc->next
            pc = pa;    //pc后移
            pa = pa->next;  //pa指针后移
        }
        else{
            pc->next = pb;
            pc = pb;
            pb = pb->next;
        }
        pc->next = pa? pa:pb;   //补充 a/b 没有比较的部分
        free(Lb)
}

/*其他线性链表*/

//静态链表
typedef struct{
       ElemType data;
       int cur; //游标，指示器
}component, SLinkList[MAXSIZE];

//双向链表
typedef struct DuLNode
{
    ElemType data;
    struct  DuLNode *prior;
    struct  DuLNode *next;
} DuLNode, *DuLinkList;

