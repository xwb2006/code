typedef struct ArcCell {       // 弧的定义
    VRType adj;               // 顶点关系类型。对无权图，用1或0表示相邻否；对带权图，则为权值类型
    InfoType* info;           // 该弧相关信息的指针
} ArcCell, AdjMatrix[MAX_VERTEX_NUM][MAX_VERTEX_NUM];

typedef struct {               // 图的定义
    VertexType vexs[MAX_VERTEX_NUM];  // 顶点向量
    AdjMatrix arcs;                   // 邻接矩阵
    int vexnum, arcnum;               // 顶点数，弧数
    GraphKind kind;                   // 图的种类标志{DG / DN / UDG / UDN}
} MGraph;

typedef struct Ebox {
    VisitIf mark;                     // 访问标记
    InfoType* info;                   // 边信息指针
    int ivex, jvex;                   // 边依附的两个顶点的位置
    struct EBox* ilink, * jlink;
} EBox;

typedef struct VexBox {
    VertexType data;
    EBox* firstedge; // 指向第一条依附该顶点的边
} VexBox;

typedef struct {                // 邻接多重表
    VexBox adjmulist[MAX_VERTEX_NUM];
    int vexnum, edgenum;
} AMLGraph;

Boolean visited[MAX];
Status (*VisitFunc)(int v);

// 图 G 深度优先遍历
void DFSTraverse(Graph G, Status (*Visit)(int v)) {  
    VisitFunc = Visit;
    for (v = 0; v < G.vexnum; ++v)
        visited[v] = FALSE;    // 访问标志数组初始化
    for (v = 0; v < G.vexnum; ++v)
        if (!visited[v])  
            DFS(G, v);         // 对尚未访问的顶点调用DFS
}

// 从顶点v出发，深度优先搜索遍历连通图 G
void DFS(Graph G, int v) {
    visited[v] = TRUE;   
    VisitFunc(v);
    for (w = FirstAdjVex(G, v); w >= 0; w = NextAdjVex(G, v, w))
        if (!visited[w])  
            DFS(G, w);     // 对v的尚未访问的邻接顶点w，递归调用DFS
}

// 图 G 广度优先遍历
void BFSTraverse(Graph G, Status (*Visit)(int v)) {
    for (v = 0; v < G.vexnum; ++v)   
        visited[v] = FALSE;  // 初始化访问标志
    InitQueue(Q);            // 置空的辅助队列Q
    for (v = 0; v < G.vexnum; ++v) {
        if (!visited[v]) {   // v 尚未访问
            visited[v] = TRUE;  
            Visit(v);        // 访问v
            EnQueue(Q, v);   // v入队列
            while (!QueueEmpty(Q)) {
                DeQueue(Q, u);  // 队头元素出队并置为u
                for (w = FirstAdjVex(G, u); w >= 0; w = NextAdjVex(G, u, w)) {
                    if (!visited[w]) {
                        visited[w] = TRUE;  
                        Visit(w);
                        EnQueue(Q, w);  // 访问的顶点w入队列
                    }
                }
            }
        }
    }
}

// 用普里姆算法从顶点u出发构造网G的最小生成树
void MiniSpanTree_PRIM(MGraph G, VertexType u) {
    // 辅助数组：记录顶点到U集的最短边
    // struct {
    //     VertexType  adjvex;  // U集中的顶点序号
    //     VRType     lowcost;  // 边的权值
    // } closedge[MAX_VERTEX_NUM];  
    
    k = LocateVex(G, u); 
    // 辅助数组初始化
    for (j = 0; j < G.vexnum; ++j)  
        if (j != k)  
            closedge[j] = { u, G.arcs[k][j].adj };  // 图存为邻接矩阵
    
    closedge[k].lowcost = 0;  // 初始，U＝{u}
    
    for (i = 0; i < G.vexnum; ++i) {
        // 求出加入生成树的下一个顶点k (closedge[k].lowcost>0)
        k = minimum(closedge);   
        printf(closedge[k].adjvex, G.vexs[k]);  // 输出生成树上一条边
        closedge[k].lowcost = 0;                // 第k顶点并入U集，距离为0
        
        // 修改其它顶点的最小边
        for (j = 0; j < G.vexnum; ++j)         
            if (G.arcs[k][j].adj < closedge[j].lowcost)
                closedge[j] = { G.vexs[k], G.arcs[k][j].adj }; 
    }
}

// 有向图G采用邻接表存储，进行拓扑排序
Status TopologicalSort(ALGraph G) 
{
    FindInDegree(G, indegree);  // 求各顶点的入度
    InitStack(S);
    
    // 入度为0的顶点入栈
    for (i = 0; i < G.vexnum; ++i)
        if (!indegree[i])     
            Push(S, i);  
    
    count = 0;  // 对输出顶点计数
    
    while (!StackEmpty(S)) {
        Pop(S, i);  
        printf(i, G.vertices[i].data);  
        ++count;  // 输出顶点
        
        // 依次处理邻接顶点，入度减1，入度为0的顶点入栈
        for (p = G.vertices[i].firstarc; p; p = p->nextarc) {
            k = p->adjvex;
            if (!(--indegree[k]))   
                Push(S, k);
        }
    }
    
    if (count < G.vexnum)     
        return ERROR;  // 存在环
    else   
        return OK;     // 拓扑排序成功
}