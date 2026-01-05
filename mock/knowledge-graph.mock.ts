import { defineMock } from "./base";

// 模拟知识图谱数据
const knowledgeGraphs = [
  {
    id: "1",
    name: "HTML基础知识图谱",
    description: "HTML基础知识点的结构化知识图谱",
    tags: ["frontend", "html"],
    status: 1,
    maintainerId: "user-101",
    createTime: "2024-01-15 10:30:00",
    updateTime: "2024-02-20 14:20:00"
  },
  {
    id: "2",
    name: "CSS布局知识图谱",
    description: "CSS布局相关知识点的结构化知识图谱",
    tags: ["frontend", "css"],
    status: 1,
    maintainerId: "user-102",
    createTime: "2024-02-10 09:15:00",
    updateTime: "2024-03-18 16:45:00"
  },
  {
    id: "3",
    name: "JavaScript基础图谱",
    description: "JavaScript基础知识点的结构化知识图谱",
    tags: ["frontend", "javascript"],
    status: 0,
    maintainerId: "user-103",
    createTime: "2024-03-05 11:20:00",
    updateTime: "2024-04-10 13:30:00"
  }
];

// 模拟知识图谱结构数据
const knowledgeGraphData = {
  "1": {
    "nodes": [
      { "data": { "id": "1_end", "label": "模块一:文本与页面结构基础", "type": "chapter" } },
      { "data": { "id": "1_1", "label": "使用h元素和p元素体验标题与段落", "type": "knowledge" } },
      { "data": { "id": "1_2", "label": "应用文本格式(加粗、斜体)", "type": "knowledge" } },
      { "data": { "id": "1_3", "label": "构建页面头部结构", "type": "knowledge" } },

      { "data": { "id": "2_end", "label": "模块二:盒子与列表使用", "type": "chapter" } },
      { "data": { "id": "2_1", "label": "使用盒子元素进行内容划分", "type": "knowledge" } },
      { "data": { "id": "2_2", "label": "创建有序列表", "type": "knowledge" } },
      { "data": { "id": "2_3", "label": "创建无序列表", "type": "knowledge" } },

      { "data": { "id": "3_end", "label": "模块三:表单与交互控件", "type": "chapter" } },
      { "data": { "id": "3_1", "label": "文本框与按钮的使用", "type": "knowledge" } },
      { "data": { "id": "3_2", "label": "复选框与单选框", "type": "knowledge" } },
      { "data": { "id": "3_3", "label": "表单提交机制", "type": "knowledge" } },
      
      { "data": { "id": "4_end", "label": "模块四：样式与布局", "type": "chapter" } },
      { "data": { "id": "4_1", "label": "设置颜色与字体", "type": "knowledge" } },
      { "data": { "id": "4_2", "label": "理解盒模型", "type": "knowledge" } },
      { "data": { "id": "4_3", "label": "使用 Flex 进行布局", "type": "knowledge" } },

      { "data": { "id": "5_end", "label": "模块五：媒体与资源管理", "type": "chapter" } },
      { "data": { "id": "5_1", "label": "插入与管理图片", "type": "knowledge" } },
      { "data": { "id": "5_2", "label": "引入音频文件", "type": "knowledge" } },
      { "data": { "id": "5_3", "label": "嵌入视频内容", "type": "knowledge" } },

      { "data": { "id": "6_end", "label": "模块六：基础交互逻辑", "type": "chapter" } },
      { "data": { "id": "6_1", "label": "按钮点击事件", "type": "knowledge" } },
      { "data": { "id": "6_2", "label": "获取用户输入", "type": "knowledge" } },
      { "data": { "id": "6_3", "label": "修改页面元素（DOM 操作）", "type": "knowledge" } }
    ],
    "edges": [
      { "data": { "source": "1_end", "target": "2_end" } },
      { "data": { "source": "2_end", "target": "3_end" } },
      { "data": { "source": "3_end", "target": "4_end" } },
      { "data": { "source": "4_end", "target": "5_end" } },
      { "data": { "source": "5_end", "target": "6_end" } },

      { "data": { "source": "1_end", "target": "1_1" } },
      { "data": { "source": "1_end", "target": "1_2" } },
      { "data": { "source": "1_end", "target": "1_3" } },

      { "data": { "source": "2_end", "target": "2_1" } },
      { "data": { "source": "2_end", "target": "2_2" } },
      { "data": { "source": "2_end", "target": "2_3" } },

      { "data": { "source": "3_end", "target": "3_1" } },
      { "data": { "source": "3_end", "target": "3_2" } },
      { "data": { "source": "3_end", "target": "3_3" } },

      { "data": { "source": "4_end", "target": "4_1" } },
      { "data": { "source": "4_end", "target": "4_2" } },
      { "data": { "source": "4_end", "target": "4_3" } },

      { "data": { "source": "5_end", "target": "5_1" } },
      { "data": { "source": "5_end", "target": "5_2" } },
      { "data": { "source": "5_end", "target": "5_3" } },

      { "data": { "source": "6_end", "target": "6_1" } },
      { "data": { "source": "6_end", "target": "6_2" } },
      { "data": { "source": "6_end", "target": "6_3" } }
    ],
    "dependent_edges": [
      { "data": { "source": "1_end", "target": "2_end" } },
      { "data": { "source": "2_end", "target": "3_end" } },
      { "data": { "source": "3_end", "target": "4_end" } },
      { "data": { "source": "4_end", "target": "5_end" } },
      { "data": { "source": "5_end", "target": "6_end" } },

      { "data": { "source": "1_end", "target": "1_1" } },
      { "data": { "source": "1_1", "target": "1_2" } },
      { "data": { "source": "1_2", "target": "1_3" } },

      { "data": { "source": "2_end", "target": "2_1" } },
      { "data": { "source": "2_1", "target": "2_2" } },
      { "data": { "source": "2_2", "target": "2_3" } },

      { "data": { "source": "3_end", "target": "3_1" } },
      { "data": { "source": "3_1", "target": "3_2" } },
      { "data": { "source": "3_2", "target": "3_3" } },

      { "data": { "source": "4_end", "target": "4_1" } },
      { "data": { "source": "4_1", "target": "4_2" } },
      { "data": { "source": "4_2", "target": "4_3" } },

      { "data": { "source": "5_end", "target": "5_1" } },
      { "data": { "source": "5_1", "target": "5_2" } },
      { "data": { "source": "5_2", "target": "5_3" } },

      { "data": { "source": "6_end", "target": "6_1" } },
      { "data": { "source": "6_1", "target": "6_2" } },
      { "data": { "source": "6_2", "target": "6_3" } }
    ]
  }
};

export default defineMock([
  // 获取知识图谱分页列表
  {
    url: "knowledge-graph/page",
    method: ["GET"],
    body: ({ params }) => {
      const { keywords, status, pageNum = 1, pageSize = 10 } = params;
      let filteredGraphs = knowledgeGraphs;
      // let filteredGraphs = knowledgeGraphs.filter(graph => {
      //   // 根据关键词过滤
      //   const matchesKeywords = !keywords || 
      //     graph.name.toLowerCase().includes(keywords.toLowerCase()) || 
      //     graph.description.toLowerCase().includes(keywords.toLowerCase());
        
      //   // 根据状态过滤
      //   const matchesStatus = !status || graph.status.toString() === status;
        
      //   return matchesKeywords && matchesStatus;
      // });
      
      // 计算分页数据
      const total = filteredGraphs.length;
      const start = (Number(pageNum) - 1) * Number(pageSize);
      const end = start + Number(pageSize);
      const list = filteredGraphs.slice(start, end);
      
      return {
        code: "00000",
        data: {
          list,
          total
        }
      };
    }
  },
  
  // 获取知识图谱表单数据
  {
    url: "knowledge-graph/([^\\s/]+)/form",
    method: ["GET"],
    body: ({ url }) => {
      const id = url.match(/knowledge-graph\/([^\/]+)\/form/)?.[1];
      const graph = knowledgeGraphs.find(item => item.id === id);
      
      if (graph) {
        return {
          code: "00000",
          data: graph
        };
      } else {
        return {
          code: "A0001",
          message: "知识图谱不存在"
        };
      }
    }
  },
  
  // 创建知识图谱
  {
    url: "knowledge-graph",
    method: ["POST"],
    body: ({ body }) => {
      const newGraph = {
        ...body,
        id: (knowledgeGraphs.length + 1).toString(),
        createTime: new Date().toISOString().slice(0, 19).replace('T', ' '),
        updateTime: new Date().toISOString().slice(0, 19).replace('T', ' ')
      };
      
      knowledgeGraphs.push(newGraph);
      
      return {
        code: "00000",
        message: "创建成功"
      };
    }
  },
  
  // 更新知识图谱
  {
    url: "knowledge-graph/([^\\s/]+)",
    method: ["PUT"],
    body: ({ url, body }) => {
      const id = url.match(/knowledge-graph\/([^\/]+)/)?.[1];
      const index = knowledgeGraphs.findIndex(item => item.id === id);
      
      if (index !== -1) {
        knowledgeGraphs[index] = {
          ...knowledgeGraphs[index],
          ...body,
          updateTime: new Date().toISOString().slice(0, 19).replace('T', ' ')
        };
        
        return {
          code: "00000",
          message: "更新成功"
        };
      } else {
        return {
          code: "A0001",
          message: "知识图谱不存在"
        };
      }
    }
  },
  
  // 删除知识图谱
  {
    url: "knowledge-graph/([^\\s/]+)",
    method: ["DELETE"],
    body: ({ url }) => {
      const id = url.match(/knowledge-graph\/([^\/]+)/)?.[1];
      const index = knowledgeGraphs.findIndex(item => item.id === id);
      
      if (index !== -1) {
        knowledgeGraphs.splice(index, 1);
        
        return {
          code: "00000",
          message: "删除成功"
        };
      } else {
        return {
          code: "A0001",
          message: "知识图谱不存在"
        };
      }
    }
  },
  
  // 发布知识图谱
  {
    url: "knowledge-graph/([^\\s/]+)/publish",
    method: ["POST"],
    body: ({ url }) => {
      const id = url.match(/knowledge-graph\/([^\/]+)\/publish/)?.[1];
      const graph = knowledgeGraphs.find(item => item.id === id);
      
      if (graph) {
        graph.status = 1; // 设置为启用状态
        graph.updateTime = new Date().toISOString().slice(0, 19).replace('T', ' ');
        
        return {
          code: "00000",
          message: "发布成功"
        };
      } else {
        return {
          code: "A0001",
          message: "知识图谱不存在"
        };
      }
    }
  },
  
  // 获取知识图谱数据
  {
    url: "knowledge-graph/([^\\s/]+)/graph",
    method: ["GET"],
    body: ({ url }) => {
      const id = url.match(/knowledge-graph\/([^\/]+)\/graph/)?.[1];
      const graph = knowledgeGraphData[id];
      
      if (graph) {
        return {
          code: "00000",
          data: graph
        };
      } else {
        return {
          code: "A0001",
          message: "知识图谱数据不存在"
        };
      }
    }
  }
]);