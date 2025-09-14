
'''三元组储存'''
#define  MAXSIZE  12500
typedef struct {
    int  i, j;        	  // 非零元的行、列下标
    ElemType  e;  // 非零元的值
} Triple;  // 三元组类型

typedef struct {
    Triple  data[MAXSIZE + 1]; 
     int     mu, nu, tu; 
} TSMatrix;  // 稀疏矩阵类型

Status FastTransposeSMatrix(TSMatrix M, TSMatrix &T)
{  // 采用三元组顺序表存储，求稀疏矩阵M的转置矩阵T，
//时间复杂度为: O(M.nu+M.tu)
    T.mu = M.nu;  T.nu = M.mu;  T.tu = M.tu;
    if (T.tu) {
        for (col=1; col<=M.nu; ++col)  num[col] = 0;
        for (t=1; t<=M.tu; ++t)  // M中每列非零元个数
            ++num[M.data[t].j];
            
        // 求第col列中第一个非零元在T.data中的序号，即转置矩阵中第 col 列的非零元素起始位置
        cpot[1] = 1;
        for (col=2; col<=M.nu; ++col)
        cpot[col] = cpot[col-1] + num[col-1];

        for (p=1; p<=M.tu; ++p) {    
            /* 转置矩阵元素 */     
            col = M.data[p].j;
            q = cpot[col];
            T.data[q].i = M.data[p].j;
            T.data[q].j = M.data[p].i;
            T.data[q].e = M.data[p].e;
            ++cpot[col];
        }
    } // if
    return OK;
} // FastTransposeSMatrix


'''行逻辑链接顺序表'''
#define  MAXMN  500  
typedef struct{
    Triple  data[MAXSIZE + 1]; 
    int     rpos[MAXMN + 1]; //M.rpos 是行指针数组，rpos[r] 存储第 r 行第一个非零元素在 M.data 中的下标
    int     mu, nu, tu;              
} RLSMatrix;   // 行逻辑链接顺序表类型

ElemType value(RLSMatrix M, int r, int c) 
{
    p = M.rpos[r];  //p 是第 r 行第一个非零元素在 M.data 中的下标
    while (M.data[p].i==r &&M.data[p].j < c) //找到第 r 行第 c 列的非零元素
        p++;
    if (M.data[p].i==r && M.data[p].j==c) //如果找到，返回其值
        return M.data[p].e;
    else
        return 0;
    } // value

Status MultSMatrix(RLSMatrix M, RLSMatrix N, RLSMatrix &Q) {
    // 检查矩阵乘法合法性：M的列数必须等于N的行数
    if (M.nu != N.mu) {
        return ERROR;
    }
    // 初始化结果矩阵Q的基本信息
    Q.mu = M.mu;    // Q的行数 = M的行数
    Q.nu = N.nu;    // Q的列数 = N的列数
    Q.tu = 0;       // 初始化非零元素个数为0
        
    // 当M和N均含非零元素时，才进行乘法运算
    if (M.tu * N.tu != 0) {
        int arow, p, q, tp, t, brow, ccol;
        ElemType ctemp[MAXCOL] = {0};  // 累加器数组（需定义MAXCOL为最大列数）
        // 遍历M的每一行（arow为M的行号）
        for (arow = 1; arow <= M.mu; ++arow) {
            // 累加器清零（当前行各元素初始化为0）
            memset(ctemp, 0, sizeof(ctemp));
            // 记录Q中当前行非零元素的起始位置
            Q.rpos[arow] = Q.tu + 1;
            // 确定M中当前行非零元素的终止位置
            if (arow < M.mu) {
                tp = M.rpos[arow + 1];  // 下一行的起始位置即当前行的终止位置
            } else {
                tp = M.tu + 1;  // 最后一行的终止位置为总非零元素数+1
            }
            // 遍历M中当前行的所有非零元素
            for (p = M.rpos[arow]; p < tp; ++p) {
                brow = M.data[p].j;  // M中元素的列号 = N中元素的行号
                 
                // 确定N中第brow行非零元素的终止位置
                if (brow < N.nu) {
                    t = N.rpos[brow + 1];  // 下一行的起始位置即当前行的终止位置
                } else {
                    t = N.tu + 1;  // 最后一行的终止位置为总非零元素数+1
                }
                // 遍历N中第brow行的所有非零元素，计算乘积并累加
                for (q = N.rpos[brow]; q < t; ++q) {
                    ccol = N.data[q].j;  // 乘积结果在Q中的列号
                    ctemp[ccol] += M.data[p].e * N.data[q].e;  // 累加计算
                }
            }
            // 将当前行的非零元素压缩存储到Q中
            for (ccol = 1; ccol <= Q.nu; ++ccol) {
                if (ctemp[ccol] != 0) {  // 只存储非零元素
                    if (++Q.tu > MAXSIZE) {  // 检查是否超过最大容量
                        return ERROR;
                    }
                    // 存储三元组信息（行号、列号、值）
                    Q.data[Q.tu].i = arow;
                    Q.data[Q.tu].j = ccol;
                    Q.data[Q.tu].e = ctemp[ccol];
                }
            }
        }
    }    
    return OK;
}

'''十字链表'''
typedef struct OLNode{
    int  i, j;      		//非零元的行和列下标
    ElemType  e;
    struct OLNode *right, *down;// 行表和列表后继链
}OLNode, *OLink;
  
typedef struct {
    OLink *rhead, *chead; // 行和列链表头指针数组， OLink * 形成指向OLNode的二级指针
    int mu, nu, tu; 	// 行数、列数和非零元个数
} CrossList;
  
Status CreateSMatrix_OL(CrossList &M){ //创建稀疏矩阵M。采用十字链存储
    if(M) free(M);	// 实现时需要建立DestroyCL()来释放空间！
    scanf(&m, &n, &t);	// 输入M的行数、列数和非零元的个数
    M.mu=m; M.nu=n; M.tu=t;// 任意行、列数

    if(!(M.rhead=(OLink *)malloc((m+1)*sizeof(OLink))))) exit(OVERFLOW);
    if(!(M.chead=(OLink *)malloc((n+1)*sizeof(OLink))))) exit(OVERFLOW);

    M.rhead[]=M.chead[]=NULL; // 初始化行列头指针向量，设为空链表

    for(scanf(&i,&j,&e); i!=0; scanf(&i,&j,&e)){// 按任意次序输入非零元
        if (!(p=(OLNode *) malloc(sizeof(OLNode)))) exit(OVERFLOW);
        p->i=i; p->j=j; p->e=e; p->down=NULL; p->right=NULL; // 新结点
        if (M.rhead[i] == NULL || M.rhead[i]->j > j)
            { p->right = M.rhead[i]; M.rhead[i]= p;} 
        else {  // 寻查在行表中的插入位置
            for(q=M.rhead[i]; (q->right)&&(q->right->j<j); q=q->right);
                p->right = q->right;  q ->right = p;  }  // 完成行插入
        if (M.chead[j] == NULL || M.chead[j]->i > i)
            { p->down = M.chead[j]; M.chead[j]= p; }
        else {  // 寻查在列表中的插入位置
            for ( q=M.chead[j]; (q->down)&&(q->down->i<i);  q=q->down );
                p->down     = q->down;  q->down = p; }  // 完成列插入
    } // for
    return OK;
}// CreateSMatrix_OL

'''广义链表'''
typedef enum {ATOM, LIST} ElemTag;
          // ATOM==0:原子, LIST==1:子表
typedef struct GLNode {
    ElemTag  tag;   // 标志域
    union{
        AtomType  atom;      // 原子结点的数据域
        struct {struct GLNode *hp, *tp;} ptr;
    };
} *GList

typedef enum {ATOM, LIST} ElemTag;
          // ATOM==0:原子, LIST==1:子表
typedef struct GLNode {
    ElemTag  tag;   // 标志域，指示union域
    union{
        AtomType  atom;      // 原子结点的数据域
        struct GLNode *hp;
    };
    struct GLNode *tp;
} *GList





