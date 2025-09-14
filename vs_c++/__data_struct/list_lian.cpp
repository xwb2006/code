#include <iostream>
using namespace std;
#define LIST_SIZE 100
#define LISTINCREMENT 10 /*设置固定的额外内存开辟量*/

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
    s->next = p->next;
    p->next = s;
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