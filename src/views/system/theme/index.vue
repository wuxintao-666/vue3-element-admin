<template>
  <div class="app-container">
    <el-card v-loading="loading" shadow="never" class="card-wrapper">
      <template #header>
        <div class="flex justify-between">
          <div>
            <el-button type="primary" @click="handleAdd">
              <el-icon>
                <Plus />
              </el-icon>
              <span>添加主题</span>
            </el-button>
            <el-button type="danger" :disabled="!multipleSelection.length" @click="handleBatchDelete">
              <el-icon>
                <Delete />
              </el-icon>
              <span>批量删除</span>
            </el-button>
          </div>
          <div>
            <el-input
              v-model="queryParams.keywords"
              placeholder="主题名称"
              clearable
              style="width: 200px; margin-right: 10px"
              @keyup.enter="handleQuery"
            />
            <el-button type="primary" @click="handleQuery">
              <el-icon>
                <Search />
              </el-icon>
              <span>搜索</span>
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="themeList"
        row-key="id"
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" fixed="left" />
        <el-table-column prop="id" label="主题ID" width="100" show-overflow-tooltip />
        <el-table-column prop="name" label="主题名称" width="150" show-overflow-tooltip />
        <el-table-column prop="description" label="简介" min-width="200" show-overflow-tooltip />
        <el-table-column prop="tags" label="标签" width="200">
          <template #default="{ row }">
            <el-space wrap>
              <el-tag v-for="tag in row.tags" :key="tag">{{ tag }}</el-tag>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="100">
          <template #default="{ row }">
            <el-tag :type="getDifficultyTagType(row.difficulty)">{{ getDifficultyText(row.difficulty) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="entranceId" label="学习入口节点ID" width="150" show-overflow-tooltip />
        <el-table-column prop="maintainerId" label="维护人ID" width="120" show-overflow-tooltip />
        <el-table-column prop="createTime" label="创建时间" width="150" />
        <el-table-column prop="updateTime" label="更新时间" width="150" />
        <el-table-column fixed="right" label="操作" width="280">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row.id)">编辑</el-button>
            <el-button type="primary" link @click="handlePublish(row.id)">发布</el-button>
            <el-button type="primary" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <Pagination
          v-if="total > 0"
          :total="total"
          v-model:page="queryParams.pageNum"
          v-model:limit="queryParams.pageSize"
          @pagination="getList"
        />
      </template>
    </el-card>

    <!-- 添加/编辑主题对话框 -->
    <el-dialog
      :title="dialog.title"
      v-model="dialog.visible"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="themeFormRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="主题名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入主题名称" />
        </el-form-item>
        <el-form-item label="简介" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入主题简介"
          />
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-select
            v-model="formData.tags"
            multiple
            placeholder="请选择标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in tagOptions"
              :key="tag.value"
              :label="tag.label"
              :value="tag.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="难度" prop="difficulty">
          <el-radio-group v-model="formData.difficulty">
            <el-radio :label="1">初级</el-radio>
            <el-radio :label="2">中级</el-radio>
            <el-radio :label="3">高级</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="学习入口节点ID" prop="entranceId">
          <el-input v-model="formData.entranceId" placeholder="请输入学习入口节点ID" />
        </el-form-item>
        <el-form-item label="维护人ID" prop="maintainerId">
          <el-input v-model="formData.maintainerId" placeholder="请输入维护人ID" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialog.visible = false">取 消</el-button>
          <el-button type="primary" @click="handleSubmit">确 定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, Delete, Search } from "@element-plus/icons-vue";
import ThemeAPI, { type ThemeVO } from "@/api/system/theme-api";
import Pagination from "@/components/Pagination/index.vue";

// 定义响应式数据
const loading = ref(true);
const total = ref(0);
const themeList = ref<ThemeVO[]>([]);
const multipleSelection = ref<ThemeVO[]>([]);

// 查询参数
const queryParams = reactive({
  keywords: undefined,
  status: undefined,
  difficulty: undefined,
  pageNum: 1,
  pageSize: 10
});

// 对话框相关数据
const dialog = reactive({
  visible: false,
  title: "",
  isEdit: false,
  currentId: ""
});

const formData = ref({
  id: undefined,
  name: "",
  description: "",
  tags: [] as string[],
  difficulty: 1,
  status: 1,
  entranceId: "",
  maintainerId: ""
});

const themeFormRef = ref();

// 表单验证规则
const formRules = {
  name: [{ required: true, message: "请输入主题名称", trigger: "blur" }],
  description: [{ required: true, message: "请输入主题简介", trigger: "blur" }],
  tags: [{ required: true, message: "请选择标签", trigger: "change" }],
  difficulty: [{ required: true, message: "请选择难度", trigger: "change" }],
  status: [{ required: true, message: "请选择状态", trigger: "change" }],
  entranceId: [{ required: true, message: "请输入学习入口节点ID", trigger: "blur" }],
  maintainerId: [{ required: true, message: "请输入维护人ID", trigger: "blur" }]
};

// 标签选项
const tagOptions = [
  { label: "前端", value: "frontend" },
  { label: "后端", value: "backend" },
  { label: "全栈", value: "fullstack" },
  { label: "移动端", value: "mobile" },
  { label: "AI", value: "ai" },
  { label: "数据库", value: "database" },
  { label: "云原生", value: "cloud" },
  { label: "微服务", value: "microservice" }
];

// 获取主题列表
const getList = async () => {
  loading.value = true;
  try {
    const response = await ThemeAPI.getPageList(queryParams);
    themeList.value = response.list || [];
    console.log("获取主题列表成功", themeList.value);
    total.value = response.data.total;
  } catch (error) {
    console.error("获取主题列表失败", error);
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
  queryParams.keywords = undefined;
  queryParams.status = undefined;
  queryParams.difficulty = undefined;
  queryParams.pageNum = 1;
  getList();
};

// 处理多选
const handleSelectionChange = (selection: ThemeVO[]) => {
  multipleSelection.value = selection;
};

// 添加主题
const handleAdd = () => {
  dialog.visible = true;
  dialog.title = "添加主题";
  dialog.isEdit = false;
  // 重置表单
  Object.assign(formData.value, {
    id: undefined,
    name: "",
    description: "",
    tags: [],
    difficulty: 1,
    status: 1,
    entranceId: "",
    maintainerId: ""
  });
};

// 编辑主题
const handleEdit = (id: string) => {
  dialog.visible = true;
  dialog.title = "编辑主题";
  dialog.isEdit = true;
  dialog.currentId = id;
  
  // 获取主题详情并填充表单
  ThemeAPI.getFormData(id).then(response => {
    Object.assign(formData.value, response.data);
  }).catch(error => {
    console.error("获取主题详情失败", error);
    ElMessage.error("获取主题详情失败");
  });
};

// 删除主题
const handleDelete = (id: string) => {
  ElMessageBox.confirm("确定要删除这个主题吗？", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning"
  }).then(() => {
    return ThemeAPI.deleteById(id);
  }).then(() => {
    getList();
    ElMessage.success("删除成功");
  }).catch(error => {
    if (error !== "cancel") {
      ElMessage.error("删除失败");
      console.error("删除主题失败", error);
    }
  });
};

// 批量删除
const handleBatchDelete = () => {
  if (!multipleSelection.value.length) {
    ElMessage.warning("请至少选择一项");
    return;
  }

  const ids = multipleSelection.value.map(item => item.id);
  ElMessageBox.confirm("确定要删除选中的主题吗？", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning"
  }).then(() => {
    // 这里应该调用批量删除API，但API中没有提供该功能，暂时循环删除
    const promises = ids.map(id => ThemeAPI.deleteById(id));
    return Promise.all(promises);
  }).then(() => {
    getList();
    ElMessage.success("删除成功");
  }).catch(error => {
    if (error !== "cancel") {
      ElMessage.error("删除失败");
      console.error("批量删除主题失败", error);
    }
  });
};

// 发布主题
const handlePublish = (id: string) => {
  ElMessageBox.confirm("确定要发布这个主题吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "info"
  }).then(() => {
    return ThemeAPI.publish(id);
  }).then(() => {
    getList();
    ElMessage.success("发布成功");
  }).catch(error => {
    if (error !== "cancel") {
      ElMessage.error("发布失败");
      console.error("发布主题失败", error);
    }
  });
};

// 提交表单
const handleSubmit = () => {
  themeFormRef.value.validate((valid: boolean) => {
    if (valid) {
      let promise;
      if (dialog.isEdit) {
        promise = ThemeAPI.update(dialog.currentId, formData.value);
      } else {
        promise = ThemeAPI.create(formData.value);
      }
      
      promise.then(() => {
        getList();
        dialog.visible = false;
        ElMessage.success(dialog.isEdit ? "更新成功" : "创建成功");
      }).catch(error => {
        ElMessage.error(dialog.isEdit ? "更新失败" : "创建失败");
        console.error(dialog.isEdit ? "更新主题失败" : "创建主题失败", error);
      });
    }
  });
};

// 关闭对话框
const handleDialogClose = () => {
  themeFormRef.value?.clearValidate();
};

// 获取难度标签类型
const getDifficultyTagType = (difficulty: number) => {
  switch (difficulty) {
    case 1: return "success"; // 初级
    case 2: return "warning"; // 中级
    case 3: return "danger";  // 高级
    default: return "info";
  }
};

// 获取难度文本
const getDifficultyText = (difficulty: number) => {
  switch (difficulty) {
    case 1: return "初级";
    case 2: return "中级";
    case 3: return "高级";
    default: return "未知";
  }
};

// 获取状态标签类型
const getStatusTagType = (status: number) => {
  return status === 1 ? "success" : "danger";
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
</style>
