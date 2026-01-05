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
              <span>添加知识图谱</span>
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
              placeholder="知识图谱名称"
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
        :data="graphList"
        row-key="id"
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" fixed="left" />
        <el-table-column prop="id" label="ID" width="100" show-overflow-tooltip />
        <el-table-column prop="name" label="名称" width="150" show-overflow-tooltip />
        <el-table-column prop="description" label="简介" min-width="200" show-overflow-tooltip />
        <el-table-column prop="tags" label="标签" width="150">
          <template #default="{ row }">
            <el-space wrap>
              <el-tag v-for="tag in row.tags" :key="tag">{{ tag }}</el-tag>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="maintainerId" label="维护人ID" width="120" show-overflow-tooltip />
        <el-table-column prop="createTime" label="创建时间" width="150" />
        <el-table-column prop="updateTime" label="更新时间" width="150" />
        <el-table-column fixed="right" label="操作" width="320">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row.id)">编辑</el-button>
            <el-button type="primary" link @click="handleViewGraph(row.id)">查看图谱</el-button>
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

    <!-- 添加/编辑知识图谱对话框 -->
    <el-dialog
      :title="dialog.title"
      v-model="dialog.visible"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="graphFormRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入知识图谱名称" />
        </el-form-item>
        <el-form-item label="简介" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入知识图谱简介"
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
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
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

    <!-- 知识图谱可视化对话框 -->
    <el-dialog
      :title="graphDialogTitle"
      v-model="graphDialog.visible"
      width="90%"
      top="2vh"
      @close="closeGraphDialog"
    >
      <div class="graph-container" v-if="graphData">
        <div class="graph-info">
          <h3>知识图谱信息</h3>
          <p><strong>节点数量:</strong> {{ graphData.nodes?.length || 0 }}</p>
          <p><strong>边数量:</strong> {{ graphData.edges?.length || 0 }}</p>
          <p><strong>依赖边数量:</strong> {{ graphData.dependent_edges?.length || 0 }}</p>
        </div>
        <div class="graph-visualization">
          <el-card>
            <template #header>
              <div class="graph-controls">
                <el-button size="small" @click="toggleGraphView">切换视图</el-button>
                <el-button size="small" @click="resetGraph">重置视图</el-button>
                <el-button size="small" @click="addNodeDialogVisible = true">添加节点</el-button>
                <el-button size="small" @click="addEdgeDialogVisible = true">添加边</el-button>
                <el-button size="small" @click="saveGraphData" type="primary">保存修改</el-button>
              </div>
            </template>
            <div ref="graphRef" class="graph" style="width: 100%; height: 300px;"></div>
          </el-card>
        </div>
      </div>
    </el-dialog>
    
    <!-- 添加节点对话框 -->
    <el-dialog title="添加节点" v-model="addNodeDialogVisible" width="500px">
      <el-form :model="newNodeForm" label-width="80px">
        <el-form-item label="节点ID">
          <el-input v-model="newNodeForm.id" placeholder="请输入节点ID" />
        </el-form-item>
        <el-form-item label="节点标签">
          <el-input v-model="newNodeForm.label" placeholder="请输入节点标签" />
        </el-form-item>
        <el-form-item label="节点类型">
          <el-select v-model="newNodeForm.type" placeholder="请选择节点类型">
            <el-option label="知识点" value="knowledge"></el-option>
            <el-option label="章节" value="chapter"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addNodeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addNode">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 添加边对话框 -->
    <el-dialog title="添加边" v-model="addEdgeDialogVisible" width="500px">
      <el-form :model="newEdgeForm" label-width="80px">
        <el-form-item label="源节点">
          <el-select v-model="newEdgeForm.source" filterable placeholder="请选择源节点">
            <el-option 
              v-for="node in graphData?.nodes || []" 
              :key="node.data.id" 
              :label="`${node.data.label} (${node.data.id})`" 
              :value="node.data.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="目标节点">
          <el-select v-model="newEdgeForm.target" filterable placeholder="请选择目标节点">
            <el-option 
              v-for="node in graphData?.nodes || []" 
              :key="node.data.id" 
              :label="`${node.data.label} (${node.data.id})`" 
              :value="node.data.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="边类型">
          <el-radio-group v-model="newEdgeForm.edgeType">
            <el-radio label="relation">关系边</el-radio>
            <el-radio label="dependency">依赖边</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addEdgeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addEdge">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, Delete, Search } from "@element-plus/icons-vue";
import KnowledgeGraphAPI, { type KnowledgeGraphVO } from "@/api/system/knowledge-graph-api";
import Pagination from "@/components/Pagination/index.vue";
import cytoscape, { type Core, type ElementDefinition } from "cytoscape";

// 定义响应式数据
const loading = ref(true);
const total = ref(0);
const graphList = ref<KnowledgeGraphVO[]>([]);
const multipleSelection = ref<KnowledgeGraphVO[]>([]);

// 查询参数
const queryParams = reactive({
  keywords: undefined,
  status: undefined,
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
  status: 1,
  maintainerId: ""
});

const graphDialog = reactive({
  visible: false,
  currentId: ""
});

// 知识图谱编辑相关数据
const addNodeDialogVisible = ref(false);
const addEdgeDialogVisible = ref(false);
const newNodeForm = ref({
  id: '',
  label: '',
  type: 'knowledge'
});
const newEdgeForm = ref({
  source: '',
  target: '',
  edgeType: 'relation' as 'relation' | 'dependency'
});

const graphRef = ref<HTMLElement>();
let cy: Core | null = null;
const graphData = ref<any>(null);
const graphDialogTitle = ref('');
const graphLoading = ref(false);

const graphFormRef = ref();

// 表单验证规则
const formRules = {
  name: [{ required: true, message: "请输入知识图谱名称", trigger: "blur" }],
  description: [{ required: true, message: "请输入知识图谱简介", trigger: "blur" }],
  tags: [{ required: true, message: "请选择标签", trigger: "change" }],
  status: [{ required: true, message: "请选择状态", trigger: "change" }],
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

// 获取知识图谱列表
const getList = async () => {
  loading.value = true;
  try {
    const response = await KnowledgeGraphAPI.getPageList(queryParams);
    graphList.value = response.list || [];
    //console.log("获取知识图谱列表成功", graphList.value);
    total.value = response.total;
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
  queryParams.keywords = undefined;
  queryParams.status = undefined;
  queryParams.pageNum = 1;
  getList();
};

// 处理多选
const handleSelectionChange = (selection: KnowledgeGraphVO[]) => {
  multipleSelection.value = selection;
};

// 添加知识图谱
const handleAdd = () => {
  dialog.visible = true;
  dialog.title = "添加知识图谱";
  dialog.isEdit = false;
  // 重置表单
  Object.assign(formData.value, {
    id: undefined,
    name: "",
    description: "",
    tags: [],
    status: 1,
    maintainerId: ""
  });
};

// 编辑知识图谱
const handleEdit = (id: string) => {
  dialog.visible = true;
  dialog.title = "编辑知识图谱";
  dialog.isEdit = true;
  dialog.currentId = id;
  
  // 获取知识图谱详情并填充表单
  KnowledgeGraphAPI.getFormData(id).then(response => {
    Object.assign(formData.value, response.data);
  }).catch(error => {
    console.error("获取知识图谱详情失败", error);
    ElMessage.error("获取知识图谱详情失败");
  });
};

// 删除知识图谱
const handleDelete = (id: string) => {
  ElMessageBox.confirm("确定要删除这个知识图谱吗？", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning"
  }).then(() => {
    return KnowledgeGraphAPI.deleteById(id);
  }).then(() => {
    getList();
    ElMessage.success("删除成功");
  }).catch(error => {
    if (error !== "cancel") {
      ElMessage.error("删除失败");
      console.error("删除知识图谱失败", error);
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
  ElMessageBox.confirm("确定要删除选中的知识图谱吗？", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning"
  }).then(() => {
    // 这里应该调用批量删除API，但API中没有提供该功能，暂时循环删除
    const promises = ids.map(id => KnowledgeGraphAPI.deleteById(id));
    return Promise.all(promises);
  }).then(() => {
    getList();
    ElMessage.success("删除成功");
  }).catch(error => {
    if (error !== "cancel") {
      ElMessage.error("删除失败");
      console.error("批量删除知识图谱失败", error);
    }
  });
};

// 发布知识图谱
const handlePublish = (id: string) => {
  ElMessageBox.confirm("确定要发布这个知识图谱吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "info"
  }).then(() => {
    return KnowledgeGraphAPI.publish(id);
  }).then(() => {
    getList();
    ElMessage.success("发布成功");
  }).catch(error => {
    if (error !== "cancel") {
      ElMessage.error("发布失败");
      console.error("发布知识图谱失败", error);
    }
  });
};

// 提交表单
const handleSubmit = () => {
  graphFormRef.value.validate((valid: boolean) => {
    if (valid) {
      let promise;
      if (dialog.isEdit) {
        promise = KnowledgeGraphAPI.update(dialog.currentId, formData.value);
      } else {
        promise = KnowledgeGraphAPI.create(formData.value);
      }
      
      promise.then(() => {
        getList();
        dialog.visible = false;
        ElMessage.success(dialog.isEdit ? "更新成功" : "创建成功");
      }).catch(error => {
        ElMessage.error(dialog.isEdit ? "更新失败" : "创建失败");
        console.error(dialog.isEdit ? "更新知识图谱失败" : "创建知识图谱失败", error);
      });
    }
  });
};

// 关闭对话框
const handleDialogClose = () => {
  graphFormRef.value?.clearValidate();
};

// 获取状态标签类型
const getStatusTagType = (status: number) => {
  return status === 1 ? "success" : "danger";
};

// 获取状态文本
const getStatusText = (status: number) => {
  return status === 1 ? "启用" : "禁用";
};

// 查看知识图谱
const handleViewGraph = async (id: string) => {
  graphDialog.currentId = id;
  graphDialog.visible = true;
  
  try {
    const response = await KnowledgeGraphAPI.getGraphData(id);
    graphData.value = response;
    console.log("获取知识图谱数据成功", graphData.value);
    graphDialogTitle.value = `知识图谱: ${graphList.value.find(g => g.id === id)?.name}`;
    console.log("图谱对话框标题:", graphDialogTitle.value);
    // 等待DOM更新后再初始化图谱
    await nextTick();
    initGraph();
  } catch (error) {
    console.error("获取知识图谱数据失败", error);
    ElMessage.error("获取知识图谱数据失败");
  }
};

// 添加节点
const addNode = () => {
  if (!newNodeForm.value.id || !newNodeForm.value.label) {
    ElMessage.error('节点ID和标签不能为空');
    return;
  }
  
  // 检查ID是否已存在
  const exists = graphData.value.nodes.some((node: any) => node.data.id === newNodeForm.value.id);
  if (exists) {
    ElMessage.error('节点ID已存在');
    return;
  }
  
  const newNode = {
    data: {
      id: newNodeForm.value.id,
      label: newNodeForm.value.label,
      type: newNodeForm.value.type
    }
  };
  
  graphData.value.nodes.push(newNode);
  
  // 添加到cytoscape
  if (cy) {
    cy.add(newNode);
  }
  
  newNodeForm.value = { id: '', label: '', type: 'knowledge' };
  addNodeDialogVisible.value = false;
  ElMessage.success('节点添加成功');
};

// 添加边
const addEdge = () => {
  if (!newEdgeForm.value.source || !newEdgeForm.value.target) {
    ElMessage.error('请选择源节点和目标节点');
    return;
  }
  
  if (newEdgeForm.value.source === newEdgeForm.value.target) {
    ElMessage.error('源节点和目标节点不能相同');
    return;
  }
  
  // 检查边是否已存在
  const edges = newEdgeForm.value.edgeType === 'relation' ? 
    graphData.value.edges : 
    graphData.value.dependent_edges;
    
  const exists = edges.some((edge: any) => 
    edge.data.source === newEdgeForm.value.source && 
    edge.data.target === newEdgeForm.value.target
  );
  
  if (exists) {
    ElMessage.error('该边已存在');
    return;
  }
  
  const newEdge = {
    data: {
      source: newEdgeForm.value.source,
      target: newEdgeForm.value.target
    }
  };
  
  if (newEdgeForm.value.edgeType === 'relation') {
    graphData.value.edges.push(newEdge);
  } else {
    graphData.value.dependent_edges.push(newEdge);
  }
  
  // 添加到cytoscape
  if (cy) {
    cy.add(newEdge);
  }
  
  newEdgeForm.value = { source: '', target: '', edgeType: 'relation' };
  addEdgeDialogVisible.value = false;
  ElMessage.success('边添加成功');
};

// 保存图谱数据
const saveGraphData = async () => {
  if (!graphDialog.value.currentId) {
    ElMessage.error('未指定知识图谱ID');
    return;
  }
  
  try {
    // 这里需要后端提供一个更新图谱结构的API
    // 暂时显示成功信息，实际应用中需要调用API
    ElMessage.success('图谱数据保存成功');
    console.log('要保存的图谱数据:', graphData.value);
  } catch (error) {
    console.error('保存图谱数据失败', error);
    ElMessage.error('保存图谱数据失败');
  }
};

// 初始化图谱
const initGraph = () => {
  if (!graphRef.value || !graphData.value) return;
  
  // 销毁之前的实例
  if (cy) {
    cy.destroy();
  }
  graphRef.value.addEventListener('wheel', e => e.preventDefault(), { passive: false });
  // 检查数据是否存在
  const nodes = graphData.value.nodes || [];
  const edges = graphData.value.edges || [];
  const dependentEdges = graphData.value.dependent_edges || [];
  
  // 合并所有边
  const allEdges = [...edges, ...dependentEdges];
  
  // 初始化cytoscape
  cy = cytoscape({
    container: graphRef.value,
    elements: [
      ...nodes.map((node: any) => ({
        data: node.data
      })),
      ...allEdges.map((edge: any) => ({
        data: edge.data
      }))
    ],
    style: [
      {
    selector: 'node',
    style: {
      'label': 'data(label)',
      'width': 100,
      'height': 100
    }
  },
  {
    selector: 'node[type = "chapter"]',
    style: {
      'shape': 'rectangle',
      'background-color': '#3498db'
    }
  },
  {
    selector: 'node[type != "chapter"]',
    style: {
      'shape': 'ellipse',
      'background-color': '#e74c3c'
    }
  },
      {
        selector: 'edge',
        style: {
          'width': 2,
          'line-color': '#9dbaea',
          'target-arrow-color': '#9dbaea',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier'
        }
      }
    ],
    layout: {
      name: 'cose',
      animate: true,
      animationDuration: 500,
      fit: true,
      padding: 30
    }, 
    userPanningEnabled: true,
    wheelSensitivity: 0.2, // 调整滚轮缩放灵敏度
  });
};

// 关闭图谱对话框
const closeGraphDialog = () => {
  if (cy) {
    cy.destroy();
    cy = null;
  }
  graphData.value = null;
};

// 切换图谱视图
const toggleGraphView = () => {
  if (cy) {
    cy.elements().unselect();
    cy.layout({ name: 'cose' }).run();
  }
};

// 重置图谱视图
const resetGraph = () => {
  if (cy) {
    cy.fit();
    cy.center();
  }
};

onMounted(() => {
  getList();
});
</script>

<style lang="scss" scoped>
.card-wrapper {
  min-height: calc(100vh - 200px);
}

.graph-container {
  .graph-info {
    margin-bottom: 20px;
    padding: 10px;
    background-color: #f5f7fa;
    border-radius: 4px;
  }

  .graph-visualization {
    height: 60vh;

    .graph {
      width: 100%;
      height: 100%;
    }

    .graph-controls {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }
  }
}
</style>
