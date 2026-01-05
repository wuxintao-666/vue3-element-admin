import request from "@/utils/request";

const KNOWLEDGE_GRAPH_BASE_URL = "/api/v1/knowledge-graph";

const KnowledgeGraphAPI = {
  /** 获取知识图谱列表 */
  getPageList(queryParams: KnowledgeGraphQuery) {
    return request<any, PageResult<KnowledgeGraphVO[]>>({ 
      url: `${KNOWLEDGE_GRAPH_BASE_URL}/page`, 
      method: "get", 
      params: queryParams 
    });
  },

  /** 获取知识图谱表单数据 */
  getFormData(id: string) {
    return request<any, KnowledgeGraphForm>({ 
      url: `${KNOWLEDGE_GRAPH_BASE_URL}/${id}/form`, 
      method: "get" 
    });
  },

  /** 新增知识图谱 */
  create(data: KnowledgeGraphForm) {
    return request({ 
      url: `${KNOWLEDGE_GRAPH_BASE_URL}`, 
      method: "post", 
      data 
    });
  },

  /** 修改知识图谱 */
  update(id: string, data: KnowledgeGraphForm) {
    return request({ 
      url: `${KNOWLEDGE_GRAPH_BASE_URL}/${id}`, 
      method: "put", 
      data 
    });
  },

  /** 删除知识图谱 */
  deleteById(id: string) {
    return request({ 
      url: `${KNOWLEDGE_GRAPH_BASE_URL}/${id}`, 
      method: "delete" 
    });
  },

  /** 发布知识图谱 */
  publish(id: string) {
    return request({ 
      url: `${KNOWLEDGE_GRAPH_BASE_URL}/${id}/publish`, 
      method: "post" 
    });
  },
  
  /** 获取知识图谱详情 */
  getGraphData(id: string) {
    return request<any, KnowledgeGraphData>({ 
      url: `${KNOWLEDGE_GRAPH_BASE_URL}/${id}/graph`, 
      method: "get" 
    });
  }
};

export default KnowledgeGraphAPI;

export interface KnowledgeGraphQuery {
  /** 搜索关键字 */
  keywords?: string;
  /** 状态 */
  status?: number;
  /** 页码 */
  pageNum: number;
  /** 每页大小 */
  pageSize: number;
}

export interface KnowledgeGraphVO {
  /** ID */
  id?: string;
  /** 名称 */
  name: string;
  /** 简介 */
  description: string;
  /** 标签 */
  tags: string[];
  /** 状态 */
  status: number;
  /** 维护人ID */
  maintainerId: string;
  /** 创建时间 */
  createTime?: string;
  /** 更新时间 */
  updateTime?: string;
}

export interface KnowledgeGraphForm {
  /** ID */
  id?: string;
  /** 名称 */
  name: string;
  /** 简介 */
  description: string;
  /** 标签 */
  tags: string[];
  /** 状态 */
  status: number;
  /** 维护人ID */
  maintainerId: string;
}

export interface KnowledgeGraphData {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
  dependent_edges: KnowledgeGraphEdge[];
}

export interface KnowledgeGraphNode {
  data: {
    id: string;
    label: string;
    type: string;
  };
}

export interface KnowledgeGraphEdge {
  data: {
    source: string;
    target: string;
  };
}