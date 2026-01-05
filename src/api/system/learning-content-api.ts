import request from '@/utils/request';
const baseUrl = '/api/v1/learning-content';

/**
 * 查询知识点内容列表
 */
export function listKnowledgeContent(query: KnowledgeContentQuery) {
  return request({
    url: baseUrl,
    method: 'get',
    params: query,
  });
}

/**
 * 查询知识点内容详细
 */
export function getKnowledgeContent(id: number) {
  return request({
    url: `${baseUrl}/${id}`,
    method: 'get',
  });
}

/**
 * 新增知识点内容
 */
export function addKnowledgeContent(data: KnowledgeContentForm) {
  return request({
    url: baseUrl,
    method: 'post',
    data,
  });
}

/**
 * 修改知识点内容
 */
export function updateKnowledgeContent(data: KnowledgeContentForm) {
  return request({
    url: `${baseUrl}/${data.id}`,
    method: 'put',
    data,
  });
}

/**
 * 删除知识点内容
 */
export function deleteKnowledgeContent(id: number) {
  return request({
    url: `${baseUrl}/${id}`,
    method: 'delete',
  });
}

/**
 * 批量删除知识点内容
 */
export function batchDeleteKnowledgeContent(ids: number[]) {
  return request({
    url: baseUrl,
    method: 'delete',
    data: { ids },
  });
}
/**
 * 知识内容相关类型定义
 */

// 知识内容查询参数
export interface KnowledgeContentQuery {
  pageNum?: number
  pageSize?: number
  title?: string
  status?: number
  graphId?: string
}

// 知识内容视图对象
export interface KnowledgeContentVO {
  id?: number
  graphId?: string
  title?: string
  description?: string
  status?: number
  maintainerId?: number
  createTime?: string
  updateTime?: string
  topics?: Array<{
    topicId: string
    title: string
    levels: Array<{
      level: number
      description: string
    }>
  }>
}

// 知识内容表单对象
export interface KnowledgeContentForm {
  id?: number
  graphId?: string
  title: string
  description: string
  status: number
  maintainerId?: number
}