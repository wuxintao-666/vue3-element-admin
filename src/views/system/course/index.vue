<!-- 课程管理 -->
<template>
  <div class="app-container">
    <el-row :gutter="20">
      <!-- 课程列表 -->
      <el-col :lg="24" :xs="24">
        <!-- 搜索区域 -->
        <div class="search-container">
          <el-form ref="queryFormRef" :model="queryParams" :inline="true" label-width="auto">
            <el-form-item label="课程编码" prop="courseCode">
              <el-input
                v-model="queryParams.courseCode"
                placeholder="请输入课程编码"
                clearable
                @keyup.enter="handleQuery"
              />
            </el-form-item>

            <el-form-item label="课程名称" prop="courseName">
              <el-input
                v-model="queryParams.courseName"
                placeholder="请输入课程名称"
                clearable
                @keyup.enter="handleQuery"
              />
            </el-form-item>

            <el-form-item class="search-buttons">
              <el-button type="primary" icon="search" @click="handleQuery">搜索</el-button>
              <el-button icon="refresh" @click="handleResetQuery">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <el-card shadow="hover" class="data-table">
          <div class="data-table__toolbar">
            <div class="data-table__toolbar--actions">
              <el-button
                type="success"
                icon="plus"
                @click="handleOpenDialog()"
              >
                新增
              </el-button>
              <el-button
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete()"
              >
                删除
              </el-button>
            </div>
          </div>

          <el-table
            v-loading="loading"
            :data="pageData"
            border
            stripe
            highlight-current-row
            class="data-table__content"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="50" align="center" />
            <el-table-column label="课程ID" prop="id" width="80" />
            <el-table-column label="课程编码" prop="courseCode" min-width="120" />
            <el-table-column label="课程名称" prop="courseName" min-width="200" />
            <el-table-column label="课程说明" prop="description" min-width="300" />
            <el-table-column label="创建时间" align="center" prop="createdAt" width="180" />
            <el-table-column label="更新时间" align="center" prop="updatedAt" width="180" />
            <el-table-column label="操作" fixed="right" width="150">
              <template #default="scope">
                <el-button
                  type="primary"
                  icon="edit"
                  link
                  size="small"
                  @click="handleOpenDialog(scope.row.id)"
                >
                  编辑
                </el-button>
                <el-button
                  type="danger"
                  icon="delete"
                  link
                  size="small"
                  @click="handleDelete(scope.row.id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="data-table__pagination">
            <el-pagination
              v-model:current-page="queryParams.pageNum"
              v-model:page-size="queryParams.pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 课程表单 -->
    <el-drawer
      v-model="dialog.visible"
      :title="dialog.title"
      append-to-body
      :size="drawerSize"
      @close="handleCloseDialog"
    >
      <el-form ref="courseFormRef" :model="formData" :rules="rules" label-width="80px">
        <el-form-item label="课程编码" prop="courseCode">
          <el-input
            v-model="formData.courseCode"
            :readonly="!!formData.id"
            placeholder="请输入课程编码"
          />
        </el-form-item>

        <el-form-item label="课程名称" prop="courseName">
          <el-input
            v-model="formData.courseName"
            placeholder="请输入课程名称"
          />
        </el-form-item>

        <el-form-item label="课程说明" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入课程说明"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="handleSubmit">确 定</el-button>
          <el-button @click="handleCloseDialog">取 消</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from "@/store/modules/app-store";
import { DeviceEnum } from "@/enums/settings/device-enum";
import { ElMessage, ElMessageBox } from "element-plus";
import CourseAPI, { CourseForm, CoursePageQuery, CoursePageVO } from "@/api/system/course-api";

defineOptions({
  name: "Course",
  inheritAttrs: false,
});

const appStore = useAppStore();

const queryFormRef = ref();
const courseFormRef = ref();

const queryParams = reactive<CoursePageQuery>({
  pageNum: 1,
  pageSize: 10,
  courseCode: "",
  courseName: "",
});

const pageData = ref<CoursePageVO[]>([]);
const total = ref(0);
const loading = ref(false);

const dialog = reactive({
  visible: false,
  title: "新增课程",
});
const drawerSize = computed(() => (appStore.device === DeviceEnum.DESKTOP ? "600px" : "90%"));

const formData = reactive<CourseForm>({
  courseCode: "",
  courseName: "",
  description: "",
});

const rules = reactive({
  courseCode: [
    { required: true, message: "课程编码不能为空", trigger: "blur" },
    { pattern: /^[A-Za-z0-9_-]+$/, message: "课程编码只能包含字母、数字、下划线和连字符", trigger: "blur" }
  ],
  courseName: [{ required: true, message: "课程名称不能为空", trigger: "blur" }],
  description: [{ max: 500, message: "课程说明不能超过500个字符", trigger: "blur" }],
});

// 选中的课程ID
const selectIds = ref<number[]>([]);

// 获取数据
async function fetchData() {
  loading.value = true;
  try {
    const result = await CourseAPI.getPage(queryParams);

    // 将snake_case转换为camelCase
    const transformedList = (result.list || []).map((item: any) => ({
      id: item.id,
      courseCode: item.course_code,
      courseName: item.course_name,
      description: item.description,
      createdAt: item.created_at,
      updatedAt: item.updated_at,
    }));

    pageData.value = transformedList;
    total.value = result.total || 0;
  } catch (error) {
    console.error('获取课程列表失败:', error);
    ElMessage.error('获取课程列表失败');
  } finally {
    loading.value = false;
  }
}

// 搜索
function handleQuery() {
  queryParams.pageNum = 1;
  fetchData();
}

// 重置搜索
function handleResetQuery() {
  queryFormRef.value?.resetFields();
  handleQuery();
}

// 选择改变
function handleSelectionChange(selection: any[]) {
  selectIds.value = selection.map(item => item.id);
}

// 打开对话框
async function handleOpenDialog(id?: number) {
  dialog.visible = true;

  if (id) {
    dialog.title = "编辑课程";
    try {
      const result = await CourseAPI.getDetail(id);
      if (result) {
        // 将snake_case转换为camelCase
        const transformedData = {
          id: result.id,
          courseCode: (result as any).course_code,
          courseName: (result as any).course_name,
          description: result.description,
        };
        Object.assign(formData, transformedData);
      } else {
        ElMessage.error('获取课程详情失败');
        dialog.visible = false;
      }
    } catch (error) {
      console.error('获取课程详情失败:', error);
      ElMessage.error('获取课程详情失败');
      dialog.visible = false;
    }
  } else {
    dialog.title = "新增课程";
    Object.assign(formData, {
      id: undefined,
      courseCode: "",
      courseName: "",
      description: "",
    });
  }
}

// 关闭对话框
function handleCloseDialog() {
  dialog.visible = false;
  courseFormRef.value?.resetFields();
  // 清理表单数据
  Object.assign(formData, {
    id: undefined,
    courseCode: "",
    courseName: "",
    description: "",
  });
}

// 提交表单
async function handleSubmit() {
  try {
    await courseFormRef.value?.validate();

    if (formData.id) {
      await CourseAPI.update(formData.id, formData);
      ElMessage.success('更新课程成功');
    } else {
      await CourseAPI.create(formData);
      ElMessage.success('创建课程成功');
    }

    handleCloseDialog();
    fetchData();
  } catch (error) {
    console.error(formData.id ? '更新课程失败:' : '创建课程失败:', error);
    ElMessage.error(formData.id ? '更新课程失败' : '创建课程失败');
  }
}

// 删除课程
async function handleDelete(id?: number) {
  const ids = id ? [id] : selectIds.value;

  if (ids.length === 0) {
    ElMessage.warning('请选择要删除的课程');
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确定删除${ids.length}个课程吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    if (id) {
      await CourseAPI.delete(id);
    } else {
      await CourseAPI.batchDelete(ids);
    }

    ElMessage.success('删除课程成功');
    selectIds.value = [];
    fetchData();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除课程失败:', error);
      ElMessage.error('删除课程失败');
    }
  }
}

// 分页大小改变
function handleSizeChange(size: number) {
  queryParams.pageSize = size;
  fetchData();
}

// 当前页改变
function handleCurrentChange(page: number) {
  queryParams.pageNum = page;
  fetchData();
}

// 页面加载时获取数据
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.search-container {
  margin-bottom: 20px;
}

.search-buttons {
  margin-left: 10px;
}

.data-table {
  margin-bottom: 20px;
}

.data-table__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.data-table__toolbar--actions {
  display: flex;
  gap: 10px;
}

.data-table__toolbar--tools {
  display: flex;
  gap: 10px;
}

.data-table__content {
  margin-bottom: 16px;
}

.data-table__pagination {
  display: flex;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>