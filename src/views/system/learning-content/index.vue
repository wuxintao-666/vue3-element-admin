<template>
  <div class="app-container">
    <div class="card-wrapper">
      <el-card shadow="never">
        <template #header>
          <div class="flex justify-between">
            <div>
              <el-button type="primary" @click="handleAdd" :icon="Plus">
                添加知识点
              </el-button>
              <el-button type="danger" @click="handleBatchDelete" :icon="Delete" :disabled="!multipleSelection.length">
                批量删除
              </el-button>
            </div>
            <el-input
              v-model="queryParams.title"
              placeholder="请输入标题"
              clearable
              @keyup.enter="handleQuery"
              @clear="handleQuery"
              style="width: 300px;"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
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

  <!-- 知识图谱 -->
  <el-table-column label="主题" prop="graphId" width="120" />

  <!-- 节点ID -->
  <el-table-column label="结点ID" prop="topic_id" show-overflow-tooltip />

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
  <el-table-column label="创建时间" prop="createTime" width="180" />

  <!-- 更新时间 -->
  <el-table-column label="更新时间" prop="updateTime" width="180" />

  <!-- 操作 -->
  <el-table-column label="操作" width="220" fixed="right">
    <template #default="{ row }">
      <el-button type="primary" @click="handleEdit(row.topic_id)" link>
        编辑
      </el-button>
      <el-button type="primary" @click="handleView(row.topic_id)" link>
        查看
      </el-button>
      <el-divider direction="vertical" />
      <el-button type="danger" @click="handleDelete(row.topic_id)" link>
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
    </div>

    <!-- 添加/编辑知识点对话框 -->
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
        <el-form-item label="主题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入知识点主题" />
        </el-form-item>
        <el-form-item label="ID" prop="title">
          <el-input v-model="formData.title" placeholder="请输入知识点ID" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="4"
            placeholder="请输入知识点内容"
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
        <!-- <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item> -->
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialog.visible = false">取 消</el-button>
          <el-button type="primary" @click="handleSubmit">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 查看知识点对话框 -->
    <el-dialog
      title="查看知识点"
      v-model="viewDialog.visible"
      width="600px"
    >
      <div v-if="viewData">
        <h3>{{ viewData.title }}</h3>
        <p><strong>难度等级：</strong>
          <el-tag :type="getLevelType(viewData.level)">{{ viewData.level }}级</el-tag>
        </p>
        <p><strong>状态：</strong>
          <el-tag :type="getStatusType(viewData.status)">{{ getStatusText(viewData.status) }}</el-tag>
        </p>
        <p><strong>内容：</strong></p>
        <div class="content-view">{{ viewData.content }}</div>
        <p><strong>创建时间：</strong>{{ viewData.createTime }}</p>
        <p><strong>更新时间：</strong>{{ viewData.updateTime }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, Delete, Search } from "@element-plus/icons-vue";
import Pagination from "@/components/Pagination/index.vue";
import {
  listKnowledgeContent,
  getKnowledgeContent,
  addKnowledgeContent,
  updateKnowledgeContent,
  deleteKnowledgeContent,
} from "@/api/system/learning-content-api";
import type { KnowledgeContentVO, KnowledgeContentForm, KnowledgeContentQuery } from "@/api/system/learning-content-api";
import { computed } from "vue";
// 定义响应式数据
const loading = ref(true);
const total = ref(0);
const contentList = ref<KnowledgeContentVO[]>([]);
const multipleSelection = ref<KnowledgeContentVO[]>([]);

const flatContentList = computed(() =>
  contentList.value.flatMap(topic =>
    topic.levels.map(level => ({
      topic_id: topic.topic_id,
      title: topic.title,
      graphId: topic.graphId,
      level: level.level,
      description: level.description,
      createTime: topic.createTime,
      updateTime: topic.updateTime
    }))
  )
);

// 查询参数
const queryParams = reactive<KnowledgeContentQuery>({
  title: undefined,
  level: undefined,
  pageNum: 1,
  pageSize: 10,
});

// 对话框相关数据
const dialog = reactive({
  visible: false,
  title: "",
  isEdit: false,
  currentId: 0,
});

const formData = ref<KnowledgeContentForm>({
  id: 0,
  title: "",
  content: "",
  level: 1,
  status: 1,
});

const viewDialog = reactive({
  visible: false,
});

const viewData = ref<KnowledgeContentVO | null>(null);

const contentFormRef = ref();

// 表单验证规则
const formRules = {
  title: [{ required: true, message: "请输入知识点标题", trigger: "blur" }],
  content: [{ required: true, message: "请输入知识点内容", trigger: "blur" }],
  level: [{ required: true, message: "请选择难度等级", trigger: "change" }],
  status: [{ required: true, message: "请选择状态", trigger: "change" }],
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
  queryParams.title = undefined;
  queryParams.level = undefined;
  queryParams.pageNum = 1;
  getList();
};

// 处理多选
const handleSelectionChange = (selection: KnowledgeContentVO[]) => {
  multipleSelection.value = selection;
};

// 添加知识点
const handleAdd = () => {
  dialog.visible = true;
  dialog.title = "添加知识点";
  dialog.isEdit = false;
  // 重置表单
  Object.assign(formData.value, {
    id: 0,
    title: "",
    content: "",
    level: 1,
    status: 1,
  });
};

// 编辑知识点
const handleEdit = async (id: number) => {
  dialog.visible = true;
  dialog.title = "编辑知识点";
  dialog.isEdit = true;
  dialog.currentId = id;

  try {
    const response = await getKnowledgeContent(id);
    console.log("获取知识点详情成功", response);
    Object.assign(formData.value, response.data);
  } catch (error) {
    console.error("获取知识点详情失败", error);
    ElMessage.error("获取知识点详情失败");
  }
};

// 查看知识点
const handleView = async (id: number) => {
  try {
    const response = await getKnowledgeContent(id);
    viewData.value = response.data;
    viewDialog.visible = true;
  } catch (error) {
    console.error("获取知识点详情失败", error);
    ElMessage.error("获取知识点详情失败");
  }
};

// 删除知识点
const handleDelete = (id: number) => {
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
      } catch (error) {
        const message = dialog.isEdit ? "更新失败" : "创建失败";
        ElMessage.error(message);
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

onMounted(() => {
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
