import httpRequest from "@/utils/request";
import { TEST_COURSE_ID } from "@/constants";

export interface TestQuestionQuery {
  courseId?: string;
  nodeId?: string;
  pageNum?: number;
  pageSize?: number;
}

export interface TestQuestionVO {
  id: number;
  course_id: number;
  node_id: string;
  title: string;
  description_md: string;
  start_code_html: string;
  start_code_css: string;
  start_code_js: string;
  checkpoints: any[];
  answer_html: string;
  answer_css: string;
  answer_js: string;
  createdAt: string;
  updatedAt: string;
  course_code?: string;
}

export interface TestQuestionForm {
  course_id?: string;
  node_id: string;
  title: string;
  description_md: string;
  start_code_html?: string;
  start_code_css?: string;
  start_code_js?: string;
  checkpoints: any[];
  answer_html: string;
  answer_css?: string;
  answer_js?: string;
}

/**
 * 查询测试题列表
 */
export function listTestQuestion(query: TestQuestionQuery) {
  return httpRequest({
    url: "/api/v1/test-questions/",
    method: "get",
    params: {
      course_id: query.courseId || TEST_COURSE_ID,
      node_id: query.nodeId,
      pageNum: query.pageNum || 1,
      pageSize: query.pageSize || 10,
    },
  });
}

/**
 * 查询测试题详细
 */
export function getTestQuestion(questionId: number) {
  return httpRequest({
    url: `/api/v1/test-questions/${questionId}`,
    method: "get",
  });
}

/**
 * 新增测试题
 */
export function addTestQuestion(data: TestQuestionForm) {
  return httpRequest({
    url: "/api/v1/test-questions/",
    method: "post",
    data: {
      ...data,
      course_id: data.course_id || TEST_COURSE_ID,
    },
  });
}

/**
 * 修改测试题
 */
export function updateTestQuestion(questionId: number, data: Partial<TestQuestionForm>) {
  return httpRequest({
    url: `/api/v1/test-questions/${questionId}`,
    method: "put",
    data,
  });
}

/**
 * 删除测试题
 */
export function delTestQuestion(questionIds: string) {
  return httpRequest({
    url: `/api/v1/test-questions/${questionIds}`,
    method: "delete",
  });
}

/**
 * 批量保存测试题
 */
export function batchAddTestQuestion(data: TestQuestionForm[]) {
  return httpRequest({
    url: "/api/v1/test-questions/batch-save",
    method: "post",
    data,
  });
}