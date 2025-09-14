// ADT Queue的表示与实现
// --- 单链队列 --- 队列的链式存储结构
typedef struct QNode {
	QElemType		data;
	struct QNode	*next;
}QNode, *QueuePtr;

typedef struct {
	QueuePtr	front;	// 队头指针
	QueuePtr	rear;		// 队尾指针
}LinkQueue;

Status  EnQueue ( LinkQueue  &Q, QElemType  e )
{   
    p = ( QueuePtr ) malloc ( sizeof(QNode));
    if ( !p )   exit (OVERFLOW);
    p->data = e;
    p->next = NULL; //申请新结点
    Q.rear->next = p;
    Q.rear = p; //插入在队尾
    return  OK;
}

Status DeQueue(LinkQueue &Q ,QElemType &e)
{
    if ( Q.front == Q.rear )   return  ERROR;
    p = Q.front->next;
    e = p->data;     //取第一个结点
    Q.front->next = p->next;  //删除第一个结点
    if ( Q.rear == p )   Q.rear = Q.front;
            //若需要删除的队头结点就是为结点
    free (p);
    return OK;
}

do{
    DeQueue(Q, s);
    GetHead(Q, e);
    EnQueue(Q, s+e);
    if (e!=0) printf (e);
    else if (s == 1) // a[i+1]=0
	EnQueue(Q, 0);
} while (!QueueOverFlow(Q));
/* 为图示方便，这里令rear==front且元素为0，实际上可定义length更长来解决，比如为10。 */
