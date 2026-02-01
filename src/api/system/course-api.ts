import request from "@/utils/request";

const COURSE_BASE_URL = "/api/v1/course";

// 课程相关类型定义
export interface CourseForm {
  id?: number;
  courseCode: string;
  courseName: string;
  description?: string;
}

export interface CoursePageQuery {
  pageNum: number;
  pageSize: number;
  courseCode?: string;
  courseName?: string;
}

export interface CoursePageVO {
  id: number;
  courseCode: string;
  courseName: string;
  description?: string;
  createdAt?: string;
  updatedAt?: string;
}

const CourseAPI = {
  /**
   * 获取课程分页列表
   *
   * @param queryParams 查询参数
   */
  getPage(queryParams: CoursePageQuery) {
    return request<any, PageResult<CoursePageVO[]>>({
      url: COURSE_BASE_URL,
      method: "get",
      params: queryParams,
    });
  },

  /**
   * 获取课程详情
   *
   * @param courseId 课程ID
   * @returns 课程详情
   */
  getDetail(courseId: number) {
    return request<any, CourseForm>({
      url: `${COURSE_BASE_URL}/${courseId}`,
      method: "get",
    });
  },

  /**
   * 添加课程
   *
   * @param data 课程表单数据
   */
  create(data: CourseForm) {
    // 将camelCase转换为snake_case
    const requestData = {
      course_code: data.courseCode,
      course_name: data.courseName,
      description: data.description,
    };
    return request({
      url: COURSE_BASE_URL,
      method: "post",
      data: requestData,
    });
  },

  /**
   * 修改课程
   *
   * @param courseId 课程ID
   * @param data 课程表单数据
   */
  update(courseId: number, data: CourseForm) {
    // 将camelCase转换为snake_case
    const requestData = {
      course_code: data.courseCode,
      course_name: data.courseName,
      description: data.description,
    };
    return request({
      url: `${COURSE_BASE_URL}/${courseId}`,
      method: "put",
      data: requestData,
    });
  },

  /**
   * 删除课程
   *
   * @param courseId 课程ID
   */
  delete(courseId: number) {
    return request({
      url: `${COURSE_BASE_URL}/${courseId}`,
      method: "delete",
    });
  },

  /**
   * 批量删除课程
   *
   * @param courseIds 课程ID数组
   */
  batchDelete(courseIds: number[]) {
    return Promise.all(courseIds.map(id => this.delete(id)));
  },
};

export default CourseAPI;