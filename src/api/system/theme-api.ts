import request from "@/utils/request";

const THEME_BASE_URL = "/api/v1/themes";

const ThemeAPI = {
  /** 获取主题列表 */
  getPageList(queryParams: ThemeQuery) {
    return request<any, PageResult<ThemeVO[]>>({ url: `${THEME_BASE_URL}/page`, method: "get", params: queryParams });
  },

  /** 获取主题表单数据 */
  getFormData(id: string) {
    return request<any, ThemeForm>({ url: `${THEME_BASE_URL}/${id}/form`, method: "get" });
  },

  /** 新增主题 */
  create(data: ThemeForm) {
    return request({ url: `${THEME_BASE_URL}`, method: "post", data });
  },

  /** 修改主题 */
  update(id: string, data: ThemeForm) {
    return request({ url: `${THEME_BASE_URL}/${id}`, method: "put", data });
  },

  /** 删除主题 */
  deleteById(id: string) {
    return request({ url: `${THEME_BASE_URL}/${id}`, method: "delete" });
  },

  /** 发布主题 */
  publish(id: string) {
    return request({ url: `${THEME_BASE_URL}/${id}/publish`, method: "post" });
  },

  /** 停用主题 */
  disable(id: string) {
    return request({ url: `${THEME_BASE_URL}/${id}/disable`, method: "post" });
  },
};

export default ThemeAPI;

export interface ThemeQuery {
  /** 搜索关键字 */
  keywords?: string;
  /** 主题状态 */
  status?: number;
  /** 主题难度 */
  difficulty?: number;
  /** 页码 */
  pageNum: number;
  /** 每页大小 */
  pageSize: number;
}

export interface ThemeVO {
  /** 主题ID */
  id?: string;
  /** 主题名称 */
  name: string;
  /** 简介 */
  description: string;
  /** 标签 */
  tags: string[];
  /** 难度 */
  difficulty: number;
  /** 状态 */
  status: number;
  /** 学习入口节点ID */
  entranceId: string;
  /** 维护人ID */
  maintainerId: string;
  /** 创建时间 */
  createTime?: string;
  /** 更新时间 */
  updateTime?: string;
}

export interface ThemeForm {
  /** 主题ID */
  id?: string;
  /** 主题名称 */
  name: string;
  /** 简介 */
  description: string;
  /** 标签 */
  tags: string[];
  /** 难度 */
  difficulty: number;
  /** 状态 */
  status: number;
  /** 学习入口节点ID */
  entranceId: string;
  /** 维护人ID */
  maintainerId: string;
}