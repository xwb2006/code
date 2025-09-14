'''假设数据类型是 int'''
typedef int TElemType;

'''顺序存储结构'''
# define MAX_TREE_SIZE 100
typedef TElemType SqBiTree[MAX_TREE_SIZE]

'''链式存储结构'''
struct BitNode {
    TElemType data;
    struct BitNode *lchild, *rchild;
};

'''先序遍历函数'''
Status PreOrderTraverse(BitTree T) {
    if (T) {
        // 访问根节点（这里用 printf 输出数据示例）
        printf("%d ", T->data); 
        PreOrderTraverse(T->lchild); 
        PreOrderTraverse(T->rchild); 
    }
    // 空树返回 OK（需提前定义 Status、OK，如 #define OK 1 ）
    return OK; 
}

'''中序遍历递归算法'''
Status InOrderTraverse(BiTree T, printf(e)) {
    // visit(e) 函数可以看作 printf(e)
    if (T) {
        InOrderTraverse(T->lchild, printf);
        printf(T->data);
        InOrderTraverse(T->rchild, printf);
    } else 
        return OK;
}

'''后序遍历递归算法'''
Status PostOrderTraverse(BiTree T, printf(e)) {
    // visit(e) 函数可以看作 printf(e)
    if (T) {
        PostOrderTraverse(T->lchild, printf);
        PostOrderTraverse(T->rchild, printf);
        printf(T->data);
    } else 
        return OK;
}

'''中序遍历非递归实现'''
void Inorder_Traverse(BiTree T, void (*Visit)(TElemType& e)) {
    InitStack(S); 
    Push(S, T);
    while (!StackEmpty(S)) {
        // 向左走到尽头
        while (GetTop(S, p) && p) 
            Push(S, p->lchild);
        Pop(S, p); // 空指针退栈
        if (!StackEmpty(S)) { 
            Pop(S, p);
            if (!Visit(p->data)) return ERROR;
            Push(S, p->rchild);
        }
    }
    return OK;
}

'''定义指针标记枚举'''
'''线索二叉'''
typedef enum PointerTag {
    Link,  // 0，表示指向孩子节点
    Thread // 1，表示是线索
} PointerTag;

// 定义二叉线索树节点结构体
typedef struct BiThrNode {
    TElemType data;               // 节点数据，TElemType需提前typedef
    struct BiThrNode *lchild;     // 左孩子/前驱线索
    struct BiThrNode *rchild;     // 右孩子/后继线索
    PointerTag LTag;              // 左指针类型标记
    PointerTag RTag;              // 右指针类型标记
} BiThrNode;

'''二叉线索树的中序遍历算法'''
// 假设已定义 BiThrTree、TElemType、Link/Thread 等类型
void InOrderTraverse_Thr(BiThrTree T, void (*Visit)(TElemType e)) {
    BiThrTree p = T->lchild;  // p 指向根节点
    while (p != T) {          // 遍历未结束（p 未回到头结点 T）
        // 找到最左节点（左子树为空的节点）
        while (p->LTag == Link) p = p->lchild; 
        if (!Visit(p->data)) return ERROR;     // 访问当前节点
        // 沿右线索遍历后继节点
        while (p->RTag == Thread && p->rchild != T) { 
            p = p->rchild; 
            Visit(p->data); 
        }
        p = p->rchild;  // 进入右子树（或线索）
    }
}

'''二叉树中序线索化构建线索链表'''
// 假设已定义 BiThrTree、BiThrNode、Status、Link、Thread、OVERFLOW 等
Status InOrderThreading(BiThrTree &Thrt, BiThrTree T) {
    // 1. 分配头结点内存
    if (!(Thrt = (BiThrTree)malloc(sizeof(BiThrNode)))) {
        exit(OVERFLOW); // 内存不足，退出
    }
    // 2. 初始化头结点
    Thrt->LTag = Link;   // 左标记：Link（指向原树根）
    Thrt->RTag = Thread; // 右标记：Thread（指向中序最后节点）
    Thrt->rchild = Thrt; // 右指针回指自身（临时）
    
    // 3. 处理空树
    if (!T) {
        Thrt->lchild = Thrt; // 树空，左指针也回指自身
    } else {
        // 4. 非空树：头结点左指针指向原树根，pre 初始化为头结点
        Thrt->lchild = T; 
        BiThrTree pre = Thrt; 
        
        // 5. 中序遍历 + 线索化（需实现 InThreading 函数）
        InThreading(T); 
        
        // 6. 处理最后一个节点：让其右线索指向头结点
        pre->rchild = Thrt; 
        pre->RTag = Thread; 
        
        // 7. 头结点右指针指向最后一个节点
        Thrt->rchild = pre; 
    }
    return OK;
}
// 需补充 InThreading 函数（递归中序线索化逻辑）：
void InThreading(BiThrTree T) {
    if (T) {
        InThreading(T->lchild); // 左子树线索化
        // 处理当前节点线索（需结合 pre 记录前驱，实际实现要传 pre 指针）
        // 省略：判断 lchild/rchild 是否为空，设置 LTag/RTag 及线索
        
        InThreading(T->rchild); // 右子树线索化
    }
}

#define MAX_TREE_SIZE  100

'''双亲'''
typedef struct PTNode {
    Elem  data;
    int    parent;   // 双亲位置域
} PTNode; 
'''树结构'''
typedef struct {
    PTNode  nodes[MAX_TREE_SIZE];
    int   r, n; // 根结点的位置和结点个数
} PTree;

'''孩子链'''
typedef struct CTNode {
    int          child;
    struct CTNode *next;
} *ChildPtr;
typedef struct {
    TElemType    data;
    ChildPtr  firstchild; 
                      // 孩子链表头指针
 } CTBox;
 
 '''孩子兄弟'''
 typedef struct CSNode{
    ElemType          data;
    struct CSNode  *firstchild, 
                               *nextsibling;
} CSNode, *CSTree;
