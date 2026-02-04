<template>
  <div class="app-container">
    <div class="card-wrapper">
      <el-card shadow="never">
        <template #header>
          <div class="flex justify-between">
            <div>
              <el-button type="primary" @click="handleAdd" :icon="Plus">
                添加知识内容
              </el-button>
              <el-button type="danger" @click="handleBatchDelete" :icon="Delete" :disabled="!multipleSelection.length">
                批量删除
              </el-button>
              <el-button type="success" @click="handleExportXlsx">
                <el-icon><Download /></el-icon>
                <span>导出XLSX</span>
              </el-button>
              <el-button type="warning" @click="handleImportJson">
                <el-icon><Upload /></el-icon>
                <span>导入JSON</span>
              </el-button>
            </div>
            <div class="flex">
              <el-select
                v-model="queryParams.level"
                placeholder="请选择难度等级"
                clearable
                style="width: 150px; margin-right: 10px"
                @change="handleQuery"
              >
                <el-option label="全部" :value="undefined" />
                <el-option label="1级（入门）" :value="1" />
                <el-option label="2级（基础）" :value="2" />
                <el-option label="3级（进阶）" :value="3" />
                <el-option label="4级（高级）" :value="4" />
              </el-select>
              <el-input
                v-model="queryParams.nodeId"
                placeholder="请输入节点ID"
                clearable
                @keyup.enter="handleQuery"
                @clear="handleQuery"
                style="width: 250px;"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>
        </template>

        <!-- <el-table
          :data="contentList"
          v-loading="loading"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" align="center" />
          <el-table-column label="主题" prop="graphId" width="80" />
          <el-table-column label="结点ID" prop="topic_id" show-overflow-tooltip />
          <el-table-column label="内容" prop="content" show-overflow-tooltip />
          <el-table-column label="难度等级" prop="level" width="100">
            <template #default="{ row }">
              <el-tag :type="getLevelType(row.level)">
                {{ row.level }}级
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" prop="createTime" width="180" />
          <el-table-column label="更新时间" prop="updateTime" width="180" />
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" @click="handleEdit(row.id)" link>
                编辑
              </el-button>
              <el-button type="primary" @click="handleView(row.id)" link>
                查看
              </el-button>
              <el-divider direction="vertical" />
              <el-button type="danger" @click="handleDelete(row.id)" link>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table> -->

       <el-table
  :data="flatContentList"
  v-loading="loading"
  @selection-change="handleSelectionChange"
>
  <!-- 多选 -->
  <el-table-column type="selection" width="55" align="center" />

  <!-- 课程编码 -->
  <el-table-column label="课程编码" width="120">
    <template #default="{ row }">
      {{ row.course_code || TEST_COURSE_ID }}
    </template>
  </el-table-column>

  <!-- 节点ID -->
  <el-table-column label="节点ID" prop="node_id" show-overflow-tooltip />

  <!-- 标题 -->
  <el-table-column label="标题" prop="title" show-overflow-tooltip />

  <!-- 内容 -->
  <el-table-column label="内容" prop="description" show-overflow-tooltip />

  <!-- 难度等级 -->
  <el-table-column label="难度等级" width="100">
    <template #default="{ row }">
      <el-tag :type="getLevelType(row.level)">
        {{ row.level }}级
      </el-tag>
    </template>
  </el-table-column>

  <!-- 创建时间 -->
  <el-table-column label="创建时间" prop="created_at" width="180" />

  <!-- 更新时间 -->
  <el-table-column label="更新时间" prop="updated_at" width="180" />

  <!-- 操作 -->
  <el-table-column label="操作" width="220" fixed="right">
    <template #default="{ row }">
      <el-button type="primary" @click="handleEdit(row.id)" link>
        编辑
      </el-button>
      <el-button type="primary" @click="handleView(row.id)" link>
        查看
      </el-button>
      <el-divider direction="vertical" />
      <el-button type="danger" @click="handleDelete(row.id)" link>
        删除
      </el-button>
    </template>
  </el-table-column>
</el-table>

        <Pagination
          v-show="total > 0"
          :total="total"
          v-model:page="queryParams.pageNum"
          v-model:limit="queryParams.pageSize"
          @pagination="getList"
        />
      </el-card>

      <!-- 隐藏的文件输入 -->
      <input
        ref="fileInputRef"
        type="file"
        accept=".json"
        style="display: none"
        @change="handleFileSelect"
      />
    </div>

    <!-- 添加/编辑知识内容对话框 -->
    <el-dialog
      :title="dialog.title"
      v-model="dialog.visible"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="contentFormRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="节点ID" prop="node_id">
          <el-input v-model="formData.node_id" placeholder="请输入节点ID" />
        </el-form-item>
        <el-form-item label="标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入内容标题" />
        </el-form-item>
        <el-form-item label="内容" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入内容描述"
          />
        </el-form-item>
        <el-form-item label="难度等级" prop="level">
          <el-select
            v-model="formData.level"
            placeholder="请选择难度等级"
            style="width: 100%"
          >
            <el-option label="1级（入门）" :value="1" />
            <el-option label="2级（基础）" :value="2" />
            <el-option label="3级（进阶）" :value="3" />
            <el-option label="4级（高级）" :value="4" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialog.visible = false">取 消</el-button>
          <el-button type="primary" @click="handleSubmit">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 查看知识内容对话框 -->
    <el-dialog
      title="查看知识内容"
      v-model="viewDialog.visible"
      width="600px"
    >
      <div v-if="viewData">
        <p><strong>课程编码：</strong>{{ viewData.course_code || TEST_COURSE_ID }}</p>
        <p><strong>节点ID：</strong>{{ viewData.node_id }}</p>
        <p><strong>标题：</strong>{{ viewData.title }}</p>
        <p><strong>难度等级：</strong>
          <el-tag :type="getLevelType(viewData.level)">{{ viewData.level }}级</el-tag>
        </p>
        <p><strong>内容：</strong></p>
        <div class="content-view">{{ viewData.description }}</div>
        <p><strong>创建时间：</strong>{{ viewData.created_at }}</p>
        <p><strong>更新时间：</strong>{{ viewData.updated_at }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, Delete, Search, Download, Upload } from "@element-plus/icons-vue";
import Pagination from "@/components/Pagination/index.vue";
import {
  listKnowledgeContent,
  getKnowledgeContent,
  addKnowledgeContent,
  updateKnowledgeContent,
  deleteKnowledgeContent,
  batchAddKnowledgeContent,
} from "@/api/system/learning-content-api";
import type { KnowledgeContentVO, KnowledgeContentForm, KnowledgeContentQuery } from "@/api/system/learning-content-api";
import { TEST_COURSE_ID } from '@/constants';
// 定义响应式数据
const loading = ref(true);
const total = ref(0);
const contentList = ref<KnowledgeContentVO[]>([]);
const multipleSelection = ref<KnowledgeContentVO[]>([]);
const fileInputRef = ref<HTMLInputElement>();

const flatContentList = computed(() => contentList.value);

// 查询参数
const queryParams = reactive<KnowledgeContentQuery>({
  level: undefined,
  nodeId: undefined,
  courseId: TEST_COURSE_ID,
  pageNum: 1,
  pageSize: 10,
});

// 对话框相关数据
const dialog = reactive({
  visible: false,
  title: "",
  isEdit: false,
  currentId: "",
});

const formData = ref<KnowledgeContentForm>({
  id: undefined,
  course_id: TEST_COURSE_ID,
  node_id: "",
  title: "",
  description: "",
  level: 1,
});

const viewDialog = reactive({
  visible: false,
});

const viewData = ref<KnowledgeContentVO | null>(null);

const contentFormRef = ref();

// 表单验证规则
const formRules = {
  node_id: [{ required: true, message: "请输入节点ID", trigger: "blur" }],
  title: [{ required: true, message: "请输入标题", trigger: "blur" }],
  description: [{ required: true, message: "请输入内容", trigger: "blur" }],
  level: [{ required: true, message: "请选择难度等级", trigger: "change" }],
};

// 初始化数据
const initData = async () => {
  // 设置默认的课程ID
  queryParams.courseId = TEST_COURSE_ID;
};

// 获取知识点列表
const getList = async () => {
  loading.value = true;
  try {
    const response = await listKnowledgeContent(queryParams);
    contentList.value = response.list || [];
    console.log("获取知识点列表成功", contentList.value);
    total.value = response.total;
  } catch (error) {
    console.error("获取知识点列表失败", error);
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleQuery = () => {
  queryParams.pageNum = 1;
  getList();
};

// 重置搜索
const resetQuery = () => {
  queryParams.nodeId = undefined;
  queryParams.level = undefined;
  queryParams.pageNum = 1;
  getList();
};

// 处理多选
const handleSelectionChange = (selection: KnowledgeContentVO[]) => {
  multipleSelection.value = selection;
};

// 添加知识内容
const handleAdd = () => {
  dialog.visible = true;
  dialog.title = "添加知识内容";
  dialog.isEdit = false;
  // 重置表单
  Object.assign(formData.value, {
    id: undefined,
    course_id: TEST_COURSE_ID,
    node_id: "",
    title: "",
    description: "",
    level: 1,
  });
};

// 编辑知识点
const handleEdit = async (id: string) => {
  dialog.visible = true;
  dialog.title = "编辑知识点";
  dialog.isEdit = true;
  dialog.currentId = id;

  try {
    const response = await getKnowledgeContent(id);
    Object.assign(formData.value, response);
  } catch (error) {
    console.error("获取知识点详情失败", error);
    ElMessage.error("获取知识点详情失败");
  }
};

// 查看知识点
const handleView = async (id: string) => {
  try {
    const response = await getKnowledgeContent(id);
    viewData.value = response;
    viewDialog.visible = true;
  } catch (error) {
    console.error("获取知识点详情失败", error);
    ElMessage.error("获取知识点详情失败");
  }
};

// 删除知识点
const handleDelete = (id: string) => {
  ElMessageBox.confirm("确定要删除这个知识点吗？", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      return deleteKnowledgeContent(id);
    })
    .then(() => {
      getList();
      ElMessage.success("删除成功");
    })
    .catch((error) => {
      if (error !== "cancel") {
        ElMessage.error("删除失败");
        console.error("删除知识点失败", error);
      }
    });
};

// 批量删除
const handleBatchDelete = () => {
  if (!multipleSelection.value.length) {
    ElMessage.warning("请至少选择一项");
    return;
  }

  const ids = multipleSelection.value.map((item) => item.id);
  ElMessageBox.confirm("确定要删除选中的知识点吗？", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      return deleteKnowledgeContent(ids); // 修改为批量删除接口
    })
    .then(() => {
      getList();
      ElMessage.success("删除成功");
    })
    .catch((error) => {
      if (error !== "cancel") {
        ElMessage.error("删除失败");
        console.error("批量删除知识点失败", error);
      }
    });
};

// 提交表单
const handleSubmit = () => {
  contentFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        if (dialog.isEdit) {
          await updateKnowledgeContent(formData.value);
          ElMessage.success("更新成功");
        } else {
          await addKnowledgeContent(formData.value);
          ElMessage.success("创建成功");
        }
        dialog.visible = false;
        getList();
      } catch (error: any) {
        const message = dialog.isEdit ? "更新失败" : "创建失败";
        // 显示后端返回的详细错误信息
        const errorMessage = error?.response?.data?.message || error?.message || message;
        ElMessage.error(errorMessage);
        console.error(message, error);
      }
    }
  });
};

// 关闭对话框
const handleDialogClose = () => {
  contentFormRef.value?.clearValidate();
};

// 获取难度等级类型
const getLevelType = (level: number) => {
  switch (level) {
    case 1:
      return "success";
    case 2:
      return "primary";
    case 3:
      return "info";
    case 4:
      return "warning";
    case 5:
      return "danger";
    case 6:
      return "default"; // 修改为空字符串为default
    default:
      return "default";
  }
};

// 获取状态类型
const getStatusType = (status: number) => {
  return status === 1 ? "success" : "info"; // 修改禁用状态为info
};

// 获取状态文本
const getStatusText = (status: number) => {
  return status === 1 ? "启用" : "禁用";
};

// 导出XLSX
const handleExportXlsx = () => {
  if (!contentList.value || contentList.value.length === 0) {
    ElMessage.warning('没有数据可导出');
    return;
  }

  try {
    // 动态导入exceljs库
    import('exceljs').then(async ExcelJS => {
      const Excel = ExcelJS.default;

      // 创建工作簿
      const workbook = new Excel.Workbook();

      // 添加知识内容工作表
      const sheet = workbook.addWorksheet('知识内容');
      sheet.columns = [
        { header: '序号', key: 'index', width: 10 },
        { header: '课程编码', key: 'course_code', width: 15 },
        { header: '节点ID', key: 'node_id', width: 20 },
        { header: '标题', key: 'title', width: 30 },
        { header: '描述', key: 'description', width: 50 },
        { header: '难度等级', key: 'level', width: 15 },
        { header: '创建时间', key: 'created_at', width: 20 },
        { header: '更新时间', key: 'updated_at', width: 20 }
      ];

      contentList.value.forEach((item, index) => {
        sheet.addRow({
          index: index + 1,
          course_code: item.course_code,
          node_id: item.node_id,
          title: item.title,
          description: item.description,
          level: item.level,
          created_at: item.created_at,
          updated_at: item.updated_at
        });
      });

      // 生成文件名
      const fileName = `知识内容_${new Date().toISOString().split('T')[0]}.xlsx`;

      // 保存文件
      const buffer = await workbook.xlsx.writeBuffer();
      const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      ElMessage.success('导出成功');
    }).catch(error => {
      console.error('导出失败:', error);
      ElMessage.error('导出失败: ' + error.message);
    });
  } catch (error) {
    console.error('导出失败:', error);
    ElMessage.error('导出失败: ' + error.message);
  }
};

// 导入JSON
const handleImportJson = () => {
  fileInputRef.value?.click();
};

// 文件选择处理
const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];

  if (!file) return;

  if (!file.name.endsWith('.json')) {
    ElMessage.error('请选择JSON格式的文件');
    return;
  }

  try {
    const text = await file.text();
    const importData = JSON.parse(text);

    // 验证数据格式
    if (!Array.isArray(importData)) {
      throw new Error('数据格式错误：应为知识内容数组');
    }

    // 检查是否有必要的字段
    const requiredFields = ['course_id', 'node_id', 'title', 'description', 'level'];
    const sampleItem = importData[0];
    if (!sampleItem || requiredFields.some(field => !(field in sampleItem))) {
      throw new Error(`数据格式错误：缺少必要字段 ${requiredFields.join(', ')}`);
    }

    // 确认导入
    await ElMessageBox.confirm(
      `确定要导入这些知识内容吗？\n数据条数：${importData.length}`,
      '导入确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );

    // 调用批量保存API
    const response = await batchAddKnowledgeContent(importData);

    if (response.code === "00000") {
      ElMessage.success(`导入成功，共导入 ${response.data?.saved_count || importData.length} 条记录`);
      getList(); // 刷新列表
    } else {
      throw new Error(response.message || '导入失败');
    }

  } catch (error) {
    console.error('导入失败:', error);
    ElMessage.error('导入失败: ' + (error.message || '未知错误'));
  } finally {
    // 清空文件输入
    if (target) {
      target.value = '';
    }
  }
};

onMounted(() => {
  initData();
  getList();
});
</script>

<style lang="scss" scoped>
.card-wrapper {
  min-height: calc(100vh - 200px);
}

.content-view {
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border-left: 4px solid #409eff;
  margin: 10px 0;
  white-space: pre-wrap;
}
</style>
