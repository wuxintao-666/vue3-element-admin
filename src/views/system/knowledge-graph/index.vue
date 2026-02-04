<template>
  <div class="app-container">
    <!-- 操作按钮区域 -->
    <div class="action-buttons" style="margin-bottom: 20px;">
      <!-- 视图切换按钮 -->
      <el-button-group>
        <el-button
          type="primary"
          :class="{ active: currentView === 'graph' }"
          @click="currentView = 'graph'"
        >
          <el-icon><Grid /></el-icon>
          <span>图谱视图</span>
        </el-button>
        <el-button
          type="primary"
          :class="{ active: currentView === 'list' }"
          @click="currentView = 'list'"
        >
          <el-icon><List /></el-icon>
          <span>列表视图</span>
        </el-button>
      </el-button-group>

      <el-button type="primary" @click="handleExportXlsx">
        <el-icon><Download /></el-icon>
        <span>导出</span>
      </el-button>
      <el-button type="success" @click="handleImportJson">
        <el-icon><Upload /></el-icon>
        <span>导入</span>
      </el-button>
      <el-button
        type="warning"
        @click="handleSaveToDatabase"
        :disabled="!hasUnsavedChanges"
        :class="{ 'has-changes': hasUnsavedChanges }"
      >
        <el-icon><Check /></el-icon>
        <span>保存到数据库{{ hasUnsavedChanges ? ' (有未保存更改)' : '' }}</span>
      </el-button>
      <input
        ref="fileInputRef"
        type="file"
        accept=".json"
        style="display: none"
        @change="handleFileSelect"
      />
    </div>
    <!-- 列表视图 -->
    <div v-if="currentView === 'list'" class="form-group">
        <label>AI生成的学习路径 (共 {{ knowledgeGraph.nodes.length }} 个节点):</label>
        <div class="knowledge-list">
          <div
            v-for="(node, index) in knowledgeGraph.nodes"
            :key="node.data.id"
            class="knowledge-item"
          >
            <!-- 节点标题栏 -->
            <div class="knowledge-header">
              <span class="knowledge-id">{{ Number(index) + 1 }}.</span>
              <span class="knowledge-label">{{ node.data.label }}</span>
              <span class="knowledge-type" :class="node.data.type">
                {{ node.data.type === 'chapter' ? '章节' : '知识点' }}
              </span>
              <div class="knowledge-actions">
                <button
                  @click="showNodeDetail(node.data)"
                  class="btn btn-small btn-info"
                >
                  详情
                </button>
                <button
                  @click="editNode(node.data)"
                  class="btn btn-small btn-warning ml-1"
                >
                  编辑
                </button>
              </div>
            </div>


          </div>
        </div>

        <!-- 保存提示 -->
        <div v-if="!isKnowledgeSaved" class="save-prompt">
          <div class="alert alert-warning">
            <strong>提示：</strong>请检查并编辑以上AI生成的学习路径内容，确认无误后点击"保存图谱"按钮保存修改。
          </div>
        </div>
      </div>
    <div v-else>  
    <!-- 知识图谱可视化对话框 -->
    <div class="graph-container" v-if="graphData">
      <div class="graph-visualization">
        <KnowledgeGraphVisualization :graphData="graphData" @save-graph="handleSaveGraph" />
      </div>
    </div>
    </div>

    <!-- 编辑节点对话框 -->
    <el-dialog
      title="编辑节点"
      v-model="editDialog.visible"
      width="500px"
      @close="closeEditDialog"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editFormRules"
        label-width="80px"
      >
        <el-form-item label="节点ID" prop="id">
          <el-input v-model="editForm.id" :disabled="true" placeholder="节点ID不可修改" />
        </el-form-item>
        <el-form-item label="节点标签" prop="label">
          <el-input v-model="editForm.label" placeholder="请输入节点标签" />
        </el-form-item>
        <el-form-item label="节点类型" prop="type">
          <el-radio-group v-model="editForm.type">
            <el-radio label="chapter">章节</el-radio>
            <el-radio label="knowledge">知识点</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="关联元素" prop="select_element">
          <el-input
            v-model="editForm.select_element"
            type="textarea"
            :rows="3"
            placeholder="请输入关联的HTML元素，用逗号分隔"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editDialog.visible = false">取消</el-button>
          <el-button type="primary" @click="saveEditedNode">确定</el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, Download, Upload, Check, Grid, List } from "@element-plus/icons-vue";
import KnowledgeGraphAPI, { type KnowledgeGraphVO } from "@/api/system/knowledge-graph-api";
import Pagination from "@/components/Pagination/index.vue";
import KnowledgeGraphVisualization from "@/views/system/content-generator/KnowledgeGraphVisualization.vue";
import { TEST_COURSE_ID } from '@/constants';
// 定义响应式数据
const loading = ref(true);
const total = ref(0);
const graphList = ref<KnowledgeGraphVO[]>([]);


// 查询参数
const queryParams = reactive({
  courseCode: undefined,
  status: undefined,
  pageNum: 1,
  pageSize: 10
});

const graphDialog = reactive({
  visible: true,
  currentId: ""
});

const graphData = ref<any>(null);
const graphDialogTitle = ref('');
const fileInputRef = ref<HTMLInputElement>();
const hasUnsavedChanges = ref(false);

// 视图切换相关
const currentView = ref<'graph' | 'list'>('graph');

// 列表视图相关变量
const knowledgeGraph = computed(() => graphData.value || { nodes: [], edges: [], dependent_edges: [] });
const isKnowledgeSaved = ref(true);

// 编辑节点相关变量
const editDialog = reactive({
  visible: false
});

const editForm = ref({
  id: '',
  label: '',
  type: 'knowledge',
  select_element: ''
});

const editFormRules = {
  label: [{ required: true, message: '请输入节点标签', trigger: 'blur' }],
  type: [{ required: true, message: '请选择节点类型', trigger: 'change' }]
};

const editFormRef = ref();


// 获取知识图谱列表
const getList = async () => {
  loading.value = true;
  try {
    const response = await KnowledgeGraphAPI.getGraphDataByCourse(TEST_COURSE_ID);
    graphData.value = response;
    hasUnsavedChanges.value = false;
    console.log("获取知识图谱列表成功", graphData.value);
  } catch (error) {
    console.error("获取知识图谱列表失败", error);
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
  queryParams.courseCode = undefined;
  queryParams.status = undefined;
  queryParams.pageNum = 1;
  getList();
};


// 删除知识图谱数据
const handleDelete = async (courseId: string) => {
  try {
    await ElMessageBox.confirm("确定要删除这个课程的知识图谱数据吗？删除后无法恢复。", "警告", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });

    // 调用删除课程知识图谱数据的API
    const response = await fetch(`/api/v1/knowledge-graph/course/${courseId}/delete`, {
      method: 'DELETE'
    });

    const result = await response.json();

    if (result.code === "00000") {
      getList();
      ElMessage.success("删除成功");
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("删除失败");
      console.error("删除知识图谱数据失败", error);
    }
  }
};

// 查看知识图谱
const handleViewGraph = async (courseCode: string) => {
  graphDialog.currentId = courseCode;
  graphDialog.visible = true;

  try {
    // 使用新的按课程编码获取图谱数据的API
    const response = await KnowledgeGraphAPI.getGraphDataByCourse(courseCode);
    graphData.value = response;
    console.log("获取知识图谱数据成功", graphData.value);
    graphDialogTitle.value = `知识图谱: ${courseCode}`;
    console.log("图谱对话框标题:", graphDialogTitle.value);
  } catch (error) {
    console.error("获取知识图谱数据失败", error);
    ElMessage.error("获取知识图谱数据失败");
  }
};


// 保存图谱数据到本地变量
const handleSaveGraph = async (graph: any) => {
  // 只更新本地变量，表示有未保存的更改
  graphData.value = graph;
  hasUnsavedChanges.value = true;
  ElMessage.success('图谱修改已保存到本地，可点击"保存到数据库"按钮保存更改');
};

// 导出XLSX
const handleExportXlsx = () => {
  if (!graphData.value) {
    ElMessage.warning('没有图谱数据可导出');
    return;
  }

  try {
    // 动态导入exceljs库
    import('exceljs').then(async ExcelJS => {
      const Excel = ExcelJS.default;

      // 准备数据
      const nodes = graphData.value.nodes || [];
      const edges = graphData.value.edges || [];
      const dependentEdges = graphData.value.dependent_edges || [];

      // 创建工作簿
      const workbook = new Excel.Workbook();

      // 添加节点工作表
      const nodesSheet = workbook.addWorksheet('节点');
      nodesSheet.columns = [
        { header: '序号', key: 'index', width: 10 },
        { header: '节点ID', key: 'id', width: 20 },
        { header: '节点标签', key: 'label', width: 30 },
        { header: '节点类型', key: 'type', width: 15 },
        { header: '关联元素', key: 'elements', width: 30 }
      ];

      nodes.forEach((node: any, index: number) => {
        nodesSheet.addRow({
          index: index + 1,
          id: node.data.id,
          label: node.data.label,
          type: node.data.type,
          elements: (node.data.select_element || []).join(', ')
        });
      });

      // 添加关系边工作表
      const edgesSheet = workbook.addWorksheet('关系边');
      edgesSheet.columns = [
        { header: '序号', key: 'index', width: 10 },
        { header: '起点节点', key: 'source', width: 20 },
        { header: '终点节点', key: 'target', width: 20 },
        { header: '边类型', key: 'type', width: 15 }
      ];

      edges.forEach((edge: any, index: number) => {
        edgesSheet.addRow({
          index: index + 1,
          source: edge.data.source,
          target: edge.data.target,
          type: '普通关系'
        });
      });

      // 添加依赖边工作表
      const dependentEdgesSheet = workbook.addWorksheet('依赖边');
      dependentEdgesSheet.columns = [
        { header: '序号', key: 'index', width: 10 },
        { header: '起点节点', key: 'source', width: 20 },
        { header: '终点节点', key: 'target', width: 20 },
        { header: '边类型', key: 'type', width: 15 }
      ];

      dependentEdges.forEach((edge: any, index: number) => {
        dependentEdgesSheet.addRow({
          index: index + 1,
          source: edge.data.source,
          target: edge.data.target,
          type: '依赖关系'
        });
      });

      // 导出文件
      const buffer = await workbook.xlsx.writeBuffer();
      const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `知识图谱_${TEST_COURSE_ID}_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      ElMessage.success('导出成功');
    }).catch(error => {
      console.error('加载exceljs库失败:', error);
      ElMessage.error('导出失败：无法加载导出库');
    });
  } catch (error) {
    console.error('导出失败:', error);
    ElMessage.error('导出失败');
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
    if (!importData.nodes || !Array.isArray(importData.nodes)) {
      throw new Error('数据格式错误：缺少nodes字段或格式不正确');
    }

    // 确认导入
    await ElMessageBox.confirm(
      `确定要导入这个知识图谱吗？\n节点数量：${importData.nodes.length}\n关系边数量：${importData.edges?.length || 0}\n依赖边数量：${importData.dependent_edges?.length || 0}`,
      '导入确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );

    // 调用导入API
    const response = await fetch(`/api/v1/knowledge-graph/course/${TEST_COURSE_ID}/import`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(importData)
    });

    const result = await response.json();

    if (result.code === "00000") {
      ElMessage.success('导入成功');
      hasUnsavedChanges.value = false;
      // 重新加载数据
      getList();
    } else {
      throw new Error(result.message);
    }

  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('导入失败:', error);
      ElMessage.error(`导入失败：${error.message}`);
    }
  } finally {
    // 清空文件输入
    if (target) {
      target.value = '';
    }
  }
};

// 保存到数据库
const handleSaveToDatabase = async () => {
  if (!graphData.value) {
    ElMessage.error('没有图谱数据可保存');
    return;
  }

  if (!hasUnsavedChanges.value) {
    ElMessage.warning('没有未保存的更改');
    return;
  }

  try {
    // 确认保存
    await ElMessageBox.confirm(
      '确定要将当前图谱数据保存到数据库吗？此操作将覆盖现有的图谱数据。',
      '保存确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );

    // 调用保存API
    const response = await fetch(`/api/knowledge/save_to_database`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        course_code: TEST_COURSE_ID,
        name: `知识图谱_${TEST_COURSE_ID}`,
        graph: graphData.value
      })
    });

    const result = await response.json();

    // save_to_database API 返回的是 KnowledgeSaveToDatabaseResponse，不是标准的 ApiResponse
    if (result && result.course_code) {
      hasUnsavedChanges.value = false;
      ElMessage.success('保存到数据库成功');
    } else {
      throw new Error('保存失败：响应格式不正确');
    }

  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('保存到数据库失败:', error);
      ElMessage.error(`保存到数据库失败：${error.message}`);
    }
  }
};

// 显示节点详情
const showNodeDetail = (nodeData: any) => {
  ElMessageBox.alert(
    `<div class="node-detail">
      <h4>${nodeData.label}</h4>
      <p><strong>类型：</strong>${nodeData.type === 'chapter' ? '章节' : '知识点'}</p>
      <p><strong>ID：</strong>${nodeData.id}</p>
      ${nodeData.select_element && nodeData.select_element.length > 0 ?
        `<p><strong>关联元素：</strong>${nodeData.select_element.join(', ')}</p>` : ''}
    </div>`,
    '节点详情',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '确定'
    }
  );
};

// 编辑节点
const editNode = (nodeData: any) => {
  // 填充编辑表单
  editForm.value = {
    id: nodeData.id,
    label: nodeData.label,
    type: nodeData.type,
    select_element: (nodeData.select_element || []).join(', ')
  };

  // 显示编辑对话框
  editDialog.visible = true;
};

// 保存编辑后的节点
const saveEditedNode = () => {
  editFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        // 处理关联元素字符串为数组
        const selectElementArray = editForm.value.select_element
          .split(',')
          .map(item => item.trim())
          .filter(item => item.length > 0);

        // 更新本地数据中的节点
        if (graphData.value && graphData.value.nodes) {
          const nodeIndex = graphData.value.nodes.findIndex((node: any) => node.data.id === editForm.value.id);
          if (nodeIndex !== -1) {
            // 更新节点数据
            graphData.value.nodes[nodeIndex].data = {
              ...graphData.value.nodes[nodeIndex].data,
              label: editForm.value.label,
              type: editForm.value.type,
              select_element: selectElementArray
            };

            // 标记有未保存更改
            hasUnsavedChanges.value = true;

            // 关闭对话框
            editDialog.visible = false;

            ElMessage.success('节点修改成功，请记得保存到数据库');
          } else {
            ElMessage.error('未找到要编辑的节点');
          }
        } else {
          ElMessage.error('图谱数据不存在');
        }
      } catch (error) {
        console.error('保存节点失败:', error);
        ElMessage.error('保存节点失败');
      }
    }
  });
};

// 关闭编辑对话框
const closeEditDialog = () => {
  editFormRef.value?.clearValidate();
};

// 关闭图谱对话框
const closeGraphDialog = () => {
  graphData.value = null;
};

onMounted(() => {
  getList();
});
</script>

<style lang="scss" scoped>
.app-container {
  min-height: calc(100vh - 200px);
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;

  .el-button-group {
    margin-right: 20px;
  }

  .active {
    background-color: #409eff !important;
    border-color: #409eff !important;
  }

  .has-changes {
    animation: pulse 2s infinite;
    border-color: #e6a23c !important;
    background-color: #fdf6ec !important;
    color: #e6a23c !important;
  }

  @keyframes pulse {
    0% {
      box-shadow: 0 0 0 0 rgba(230, 162, 60, 0.4);
    }
    70% {
      box-shadow: 0 0 0 10px rgba(230, 162, 60, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(230, 162, 60, 0);
    }
  }
}

.form-group {
  margin-bottom: 20px;

  label {
    display: block;
    font-weight: bold;
    margin-bottom: 10px;
    color: #333;
  }
}

.knowledge-list {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.knowledge-item {
  border-bottom: 1px solid #e4e7ed;

  &:last-child {
    border-bottom: none;
  }
}

.knowledge-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background-color: #fafafa;

  &:hover {
    background-color: #f5f7fa;
  }
}

.knowledge-id {
  font-weight: bold;
  color: #409eff;
  margin-right: 12px;
  min-width: 24px;
}

.knowledge-label {
  flex: 1;
  font-weight: 500;
  color: #303133;
}

.knowledge-type {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  margin-right: 12px;

  &.chapter {
    background-color: #e1f3d8;
    color: #67c23a;
  }

  &.knowledge {
    background-color: #fdf6ec;
    color: #e6a23c;
  }
}

.knowledge-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 4px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;

  &:hover {
    border-color: #c0c4cc;
  }

  &.btn-small {
    padding: 2px 8px;
    font-size: 11px;
  }

  &.btn-info {
    background-color: #ecf5ff;
    border-color: #b3d8ff;
    color: #409eff;

    &:hover {
      background-color: #d9ecff;
    }
  }

  &.btn-warning {
    background-color: #fdf6ec;
    border-color: #f5dab1;
    color: #e6a23c;

    &:hover {
      background-color: #f5dab1;
    }
  }
}

.ml-1 {
  margin-left: 4px;
}

.save-prompt {
  margin-top: 16px;
}

.alert {
  padding: 12px 16px;
  border-radius: 4px;
  margin-bottom: 12px;

  &.alert-warning {
    background-color: #fdf6ec;
    border: 1px solid #f5dab1;
    color: #e6a23c;
  }

  strong {
    font-weight: bold;
  }
}

.graph-container {
  .graph-visualization {
    height: 70vh;
  }
}

.dialog-footer {
  text-align: right;
}
</style>
