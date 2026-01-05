import { defineMock } from "./base";

// 模拟主题数据
const themes = [
 {
  id: "7",
  name: "萌宠乐园",
  description: "以萌宠乐园为背景场景，逐步完成宠物列表、信息编辑与互动功能，学习完整的前端页面开发流程",
  tags: ["cute", "example", "frontend"],
  difficulty: 1,
  status: 1,
  entranceId: "entrance-007",
  maintainerId: "user-201",
  createTime: "2024-07-15 10:00:00",
  updateTime: "2024-08-01 09:30:00"
},
{
  id: "8",
  name: "校园小助手",
  description: "围绕校园小助手这一场景，逐步实现课程管理、信息展示与基础交互页面",
  tags: ["campus", "scenario", "example"],
  difficulty: 2,
  status: 1,
  entranceId: "entrance-008",
  maintainerId: "user-202",
  createTime: "2024-07-20 14:20:00",
  updateTime: "2024-08-05 16:10:00"
},
{
  id: "9",
  name: "小店铺经营记",
  description: "通过经营一家小店铺的故事背景，逐步完成商品展示、操作交互与数据联动页面",
  tags: ["story", "practice", "frontend"],
  difficulty: 2,
  status: 1,
  entranceId: "entrance-009",
  maintainerId: "user-203",
  createTime: "2024-08-02 11:15:00",
  updateTime: "2024-08-18 15:40:00"
},
{
  id: "10",
  name: "数据星球",
  description: "在数据星球的探索过程中，逐步搭建数据展示与统计分析页面，理解数据可视化的基本思路",
  tags: ["data", "visual", "scenario"],
  difficulty: 2,
  status: 1,
  entranceId: "entrance-010",
  maintainerId: "user-204",
  createTime: "2024-08-10 09:50:00",
  updateTime: "2024-08-25 14:30:00"
},
{
  id: "11",
  name: "智能小管家",
  description: "以智能小管家的应用场景为主线，逐步实现用户信息管理与状态控制相关页面功能",
  tags: ["assistant", "management", "example"],
  difficulty: 3,
  status: 0,
  entranceId: "entrance-011",
  maintainerId: "user-205",
  createTime: "2024-08-18 13:40:00",
  updateTime: "2024-09-01 10:20:00"
},
];

export default defineMock([
  // 获取主题分页列表
  {
    url: "themes/page",
    method: ["GET"],
    body: ({ params }) => {
      const { keywords, status, difficulty, pageNum = 1, pageSize = 10 } = params;
      //console.log(params);
      const filteredThemes = themes;
      // let filteredThemes = themes.filter(theme => {
      //   // 根据关键词过滤
      //   const matchesKeywords = !keywords || 
      //     theme.name.toLowerCase().includes(keywords.toLowerCase()) || 
      //     theme.description.toLowerCase().includes(keywords.toLowerCase());
        
      //   // 根据状态过滤
      //   const matchesStatus = !status || theme.status.toString() === status;
        
      //   // 根据难度过滤
      //   const matchesDifficulty = !difficulty || theme.difficulty === Number(difficulty);
        
      //   return matchesKeywords && matchesStatus && matchesDifficulty;
      // });
      //console.log('Before filtering:', filteredThemes);
      // 计算分页数据
      const total = filteredThemes.length;
      const start = (Number(pageNum) - 1) * Number(pageSize);
      const end = start + Number(pageSize);
      const list = filteredThemes.slice(start, end);
      
      return {
        code: "00000",
        data: {
          list,
          total
        }
      };
    }
  },
  
  // 获取主题表单数据
  {
    url: "themes/([^\\s/]+)/form",
    method: ["GET"],
    body: ({ url }) => {
      const id = url.match(/themes\/([^\/]+)\/form/)?.[1];
      const theme = themes.find(item => item.id === id);
      
      if (theme) {
        return {
          code: "00000",
          data: theme
        };
      } else {
        return {
          code: "A0001",
          message: "主题不存在"
        };
      }
    }
  },
  
  // 创建主题
  {
    url: "themes",
    method: ["POST"],
    body: ({ body }) => {
      const newTheme = {
        ...body,
        id: (themes.length + 1).toString(),
        createTime: new Date().toISOString().slice(0, 19).replace('T', ' '),
        updateTime: new Date().toISOString().slice(0, 19).replace('T', ' ')
      };
      
      themes.push(newTheme);
      
      return {
        code: "00000",
        message: "创建成功"
      };
    }
  },
  
  // 更新主题
  {
    url: "themes/([^\\s/]+)",
    method: ["PUT"],
    body: ({ url, body }) => {
      const id = url.match(/themes\/([^\/]+)/)?.[1];
      const index = themes.findIndex(item => item.id === id);
      
      if (index !== -1) {
        themes[index] = {
          ...themes[index],
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
          message: "主题不存在"
        };
      }
    }
  },
  
  // 删除主题
  {
    url: "themes/([^\\s/]+)",
    method: ["DELETE"],
    body: ({ url }) => {
      const id = url.match(/themes\/([^\/]+)/)?.[1];
      const index = themes.findIndex(item => item.id === id);
      
      if (index !== -1) {
        themes.splice(index, 1);
        
        return {
          code: "00000",
          message: "删除成功"
        };
      } else {
        return {
          code: "A0001",
          message: "主题不存在"
        };
      }
    }
  },
  
  // 发布主题
  {
    url: "themes/([^\\s/]+)/publish",
    method: ["POST"],
    body: ({ url }) => {
      const id = url.match(/themes\/([^\/]+)\/publish/)?.[1];
      const theme = themes.find(item => item.id === id);
      
      if (theme) {
        theme.status = 1; // 设置为启用状态
        theme.updateTime = new Date().toISOString().slice(0, 19).replace('T', ' ');
        
        return {
          code: "00000",
          message: "发布成功"
        };
      } else {
        return {
          code: "A0001",
          message: "主题不存在"
        };
      }
    }
  }
]);