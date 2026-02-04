<template>
  <div class="app-container">
    <div class="card-wrapper">
      <el-card shadow="never">
        <template #header>
          <div class="flex justify-between">
            <div>
              <el-button type="primary" @click="handleAdd" :icon="Plus">
                添加测试题
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

        <el-table
          :data="questionList"
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

          <!-- 创建时间 -->
          <el-table-column label="创建时间" prop="createdAt" width="180" />

          <!-- 更新时间 -->
          <el-table-column label="更新时间" prop="updatedAt" width="180" />

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

        <!-- 分页 -->
        <Pagination
          v-show="total > 0"
          :total="total"
          v-model:page="queryParams.pageNum!"
          v-model:limit="queryParams.pageSize!"
          @pagination="getList"
        />

        <!-- 添加/编辑对话框 -->
        <el-dialog
          v-model="dialog.visible"
          :title="dialog.isEdit ? '编辑测试题' : '添加测试题'"
          width="80%"
          :close-on-click-modal="false"
        >
          <el-form
            ref="questionFormRef"
            :model="formData"
            :rules="formRules"
            label-width="120px"
          >
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="节点ID" prop="node_id">
                  <el-input
                    v-model="formData.node_id"
                    placeholder="请输入节点ID"
                    :disabled="dialog.isEdit"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="24">
                <el-form-item label="题目标题" prop="title">
                  <el-input
                    v-model="formData.title"
                    placeholder="请输入题目标题"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="24">
                <el-form-item label="任务描述" prop="description_md">
                  <el-input
                    v-model="formData.description_md"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入任务描述（支持Markdown格式）"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="起始HTML代码">
                  <el-input
                    v-model="formData.start_code_html"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入起始HTML代码"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="起始CSS代码">
                  <el-input
                    v-model="formData.start_code_css"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入起始CSS代码"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="起始JS代码">
                  <el-input
                    v-model="formData.start_code_js"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入起始JavaScript代码"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="检查点配置" prop="checkpoints">
                  <el-input
                    v-model="checkpointsText"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入检查点配置（JSON格式）"
                    @input="parseCheckpoints"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="答案HTML代码" prop="answer_html">
                  <el-input
                    v-model="formData.answer_html"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入答案HTML代码"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="答案CSS代码">
                  <el-input
                    v-model="formData.answer_css"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入答案CSS代码"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="答案JS代码">
                  <el-input
                    v-model="formData.answer_js"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入答案JavaScript代码"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <template #footer>
            <div class="dialog-footer">
              <el-button @click="dialog.visible = false">取消</el-button>
              <el-button type="primary" @click="handleSubmit">确 定</el-button>
            </div>
          </template>
        </el-dialog>

        <!-- 查看对话框 -->
        <el-dialog
          v-model="viewDialog.visible"
          title="查看测试题"
          width="80%"
          :close-on-click-modal="false"
        >
          <div v-if="viewData">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="节点ID">{{ viewData.node_id }}</el-descriptions-item>
              <el-descriptions-item label="题目标题">{{ viewData.title }}</el-descriptions-item>
              <el-descriptions-item label="任务描述" :span="2">
                <div v-html="viewData.description_md" class="markdown-content"></div>
              </el-descriptions-item>
              <el-descriptions-item label="起始HTML代码" :span="2">
                <pre class="code-block">{{ viewData.start_code_html }}</pre>
              </el-descriptions-item>
              <el-descriptions-item label="起始CSS代码" :span="2">
                <pre class="code-block">{{ viewData.start_code_css }}</pre>
              </el-descriptions-item>
              <el-descriptions-item label="起始JS代码" :span="2">
                <pre class="code-block">{{ viewData.start_code_js }}</pre>
              </el-descriptions-item>
              <el-descriptions-item label="检查点配置" :span="2">
                <pre class="code-block">{{ JSON.stringify(viewData.checkpoints, null, 2) }}</pre>
              </el-descriptions-item>
              <el-descriptions-item label="答案HTML代码" :span="2">
                <pre class="code-block">{{ viewData.answer_html }}</pre>
              </el-descriptions-item>
              <el-descriptions-item label="答案CSS代码" :span="2">
                <pre class="code-block">{{ viewData.answer_css }}</pre>
              </el-descriptions-item>
              <el-descriptions-item label="答案JS代码" :span="2">
                <pre class="code-block">{{ viewData.answer_js }}</pre>
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ viewData.createdAt }}</el-descriptions-item>
              <el-descriptions-item label="更新时间">{{ viewData.updatedAt }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <template #footer>
            <div class="dialog-footer">
              <el-button @click="viewDialog.visible = false">关闭</el-button>
            </div>
          </template>
        </el-dialog>

        <!-- 隐藏的文件输入 -->
        <input
          ref="fileInputRef"
          type="file"
          accept=".json"
          style="display: none"
          @change="handleFileSelect"
        />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts" name="TestQuestion">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, Delete, Search, Download, Upload } from "@element-plus/icons-vue";
import {
  listTestQuestion,
  getTestQuestion,
  addTestQuestion,
  updateTestQuestion,
  delTestQuestion,
  batchAddTestQuestion,
  type TestQuestionQuery,
  type TestQuestionVO,
  type TestQuestionForm,
} from "@/api/system/test-question-api";
import { TEST_COURSE_ID } from "@/constants";

// 查询参数
const queryParams = reactive<TestQuestionQuery>({
  pageNum: 1,
  pageSize: 10,
  courseId: TEST_COURSE_ID,
});

// 表格数据
const questionList = ref<TestQuestionVO[]>([]);
const total = ref(0);
const loading = ref(false);

// 多选数组
const multipleSelection = ref<TestQuestionVO[]>([]);
const fileInputRef = ref<HTMLInputElement>();

// 表单数据
const formData = reactive<TestQuestionForm>({
  node_id: "",
  title: "",
  description_md: "",
  start_code_html: "",
  start_code_css: "",
  start_code_js: "",
  checkpoints: [],
  answer_html: "",
  answer_css: "",
  answer_js: "",
});

// 检查点文本（用于编辑）
const checkpointsText = ref("");

// 表单验证规则
const formRules = {
  node_id: [{ required: true, message: "请输入节点ID", trigger: "blur" }],
  title: [{ required: true, message: "请输入题目标题", trigger: "blur" }],
  description_md: [{ required: true, message: "请输入任务描述", trigger: "blur" }],
  checkpoints: [{ required: true, message: "请输入检查点配置", trigger: "blur" }],
  answer_html: [{ required: true, message: "请输入答案HTML代码", trigger: "blur" }],
};

// 表单引用
const questionFormRef = ref();

// 对话框状态
const dialog = reactive({
  visible: false,
  isEdit: false,
  currentId: 0,
});

// 查看对话框状态
const viewDialog = reactive({
  visible: false,
});

// 查看数据
const viewData = ref<TestQuestionVO | null>(null);

// 获取列表
const getList = async () => {
  try {
    loading.value = true;
    const response = await listTestQuestion(queryParams) as unknown as { list: TestQuestionVO[], total: number };
    questionList.value = response.list || [];
    total.value = response.total || 0;
  } catch (error: any) {
    const errorMessage = error?.response?.data?.message || error?.message || "获取列表失败";
    ElMessage.error(errorMessage);
    console.error("获取测试题列表失败", error);
  } finally {
    loading.value = false;
  }
};

// 处理查询
const handleQuery = () => {
  queryParams.pageNum = 1;
  getList();
};

// 多选变化
const handleSelectionChange = (selection: TestQuestionVO[]) => {
  multipleSelection.value = selection;
};

// 添加
const handleAdd = () => {
  dialog.visible = true;
  dialog.isEdit = false;
  dialog.currentId = 0;

  // 重置表单
  Object.assign(formData, {
    node_id: "",
    title: "",
    description_md: "",
    start_code_html: "",
    start_code_css: "",
    start_code_js: "",
    checkpoints: [],
    answer_html: "",
    answer_css: "",
    answer_js: "",
  });
  checkpointsText.value = "[]";

  questionFormRef.value?.clearValidate();
};

// 编辑
const handleEdit = async (id: number) => {
  try {
    const response = await getTestQuestion(id) as unknown as TestQuestionVO;
    const data = response;

    dialog.visible = true;
    dialog.isEdit = true;
    dialog.currentId = id;

    // 填充表单
    Object.assign(formData, {
      node_id: data.node_id,
      title: data.title,
      description_md: data.description_md,
      start_code_html: data.start_code_html,
      start_code_css: data.start_code_css,
      start_code_js: data.start_code_js,
      checkpoints: data.checkpoints,
      answer_html: data.answer_html,
      answer_css: data.answer_css,
      answer_js: data.answer_js,
    });

    checkpointsText.value = JSON.stringify(data.checkpoints, null, 2);

    questionFormRef.value?.clearValidate();
  } catch (error: any) {
    const errorMessage = error?.response?.data?.message || error?.message || "获取详情失败";
    ElMessage.error(errorMessage);
    console.error("获取测试题详情失败", error);
  }
};

// 查看
const handleView = async (id: number) => {
  try {
    const response = await getTestQuestion(id) as unknown as TestQuestionVO;
    viewData.value = response;
    viewDialog.visible = true;
  } catch (error: any) {
    const errorMessage = error?.response?.data?.message || error?.message || "获取详情失败";
    ElMessage.error(errorMessage);
    console.error("获取测试题详情失败", error);
  }
};

// 删除
const handleDelete = (id: number) => {
  ElMessageBox.confirm("确定要删除这个测试题吗？", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      return delTestQuestion(id.toString());
    })
    .then(() => {
      getList();
      ElMessage.success("删除成功");
    })
    .catch((error: any) => {
      if (error !== "cancel") {
        const errorMessage = error?.response?.data?.message || error?.message || "删除失败";
        ElMessage.error(errorMessage);
        console.error("删除测试题失败", error);
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
  ElMessageBox.confirm("确定要删除选中的测试题吗？", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      return delTestQuestion(ids.join(","));
    })
    .then(() => {
      getList();
      ElMessage.success("删除成功");
    })
    .catch((error: any) => {
      if (error !== "cancel") {
        const errorMessage = error?.response?.data?.message || error?.message || "删除失败";
        ElMessage.error(errorMessage);
        console.error("批量删除测试题失败", error);
      }
    });
};

// 解析检查点
const parseCheckpoints = () => {
  try {
    formData.checkpoints = JSON.parse(checkpointsText.value || "[]");
  } catch (error) {
    console.warn("检查点JSON格式错误", error);
  }
};

// 提交表单
const handleSubmit = () => {
  questionFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        // 确保检查点是有效的JSON
        if (typeof formData.checkpoints === "string") {
          formData.checkpoints = JSON.parse(formData.checkpoints);
        }

        if (dialog.isEdit) {
          await updateTestQuestion(dialog.currentId, formData);
          ElMessage.success("更新成功");
        } else {
          await addTestQuestion(formData);
          ElMessage.success("创建成功");
        }
        dialog.visible = false;
        getList();
      } catch (error: any) {
        const message = dialog.isEdit ? "更新失败" : "创建失败";
        const errorMessage = error?.response?.data?.message || error?.message || message;
        ElMessage.error(errorMessage);
        console.error(message, error);
      }
    }
  });
};

// 导出XLSX
const handleExportXlsx = () => {
  if (!questionList.value || questionList.value.length === 0) {
    ElMessage.warning('没有数据可导出');
    return;
  }

  try {
    // 动态导入exceljs库
    import('exceljs').then(async ExcelJS => {
      const Excel = ExcelJS.default;

      // 创建工作簿
      const workbook = new Excel.Workbook();

      // 添加测试题工作表
      const sheet = workbook.addWorksheet('测试题');
      sheet.columns = [
        { header: '序号', key: 'index', width: 10 },
        { header: '课程编码', key: 'course_code', width: 15 },
        { header: '节点ID', key: 'node_id', width: 20 },
        { header: '标题', key: 'title', width: 30 },
        { header: '描述(Markdown)', key: 'description_md', width: 50 },
        { header: '开始代码(HTML)', key: 'start_code_html', width: 30 },
        { header: '开始代码(CSS)', key: 'start_code_css', width: 30 },
        { header: '开始代码(JS)', key: 'start_code_js', width: 30 },
        { header: '检查点', key: 'checkpoints', width: 50 },
        { header: '答案代码(HTML)', key: 'answer_html', width: 30 },
        { header: '答案代码(CSS)', key: 'answer_css', width: 30 },
        { header: '答案代码(JS)', key: 'answer_js', width: 30 },
        { header: '创建时间', key: 'createdAt', width: 20 },
        { header: '更新时间', key: 'updatedAt', width: 20 }
      ];

      questionList.value.forEach((item, index) => {
        sheet.addRow({
          index: index + 1,
          course_code: item.course_code,
          node_id: item.node_id,
          title: item.title,
          description_md: item.description_md,
          start_code_html: item.start_code_html,
          start_code_css: item.start_code_css,
          start_code_js: item.start_code_js,
          checkpoints: JSON.stringify(item.checkpoints, null, 2),
          answer_html: item.answer_html,
          answer_css: item.answer_css,
          answer_js: item.answer_js,
          createdAt: item.createdAt,
          updatedAt: item.updatedAt
        });
      });

      // 生成文件名
      const fileName = `测试题_${new Date().toISOString().split('T')[0]}.xlsx`;

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
      throw new Error('数据格式错误：应为测试题数组');
    }

    // 检查是否有必要的字段
    const requiredFields = ['course_id', 'node_id', 'title', 'description_md', 'checkpoints'];
    const sampleItem = importData[0];
    if (!sampleItem || requiredFields.some(field => !(field in sampleItem))) {
      throw new Error(`数据格式错误：缺少必要字段 ${requiredFields.join(', ')}`);
    }

    // 确认导入
    await ElMessageBox.confirm(
      `确定要导入这些测试题吗？\n数据条数：${importData.length}`,
      '导入确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );

    // 调用批量保存API
    const response = await batchAddTestQuestion(importData);

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
  getList();
});
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.card-wrapper {
  margin-bottom: 20px;
}

.flex {
  display: flex;
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.dialog-footer {
  text-align: right;
}

.code-block {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  font-family: "Courier New", monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

.markdown-content {
  max-height: 200px;
  overflow-y: auto;
}
</style>