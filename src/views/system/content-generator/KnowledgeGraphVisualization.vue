<template>
  <div class="knowledge-graph-container">
    <div class="graph-info">
          <!-- <h3>知识图谱信息</h3> -->
          <p><strong>节点数量:</strong> {{ graphData.nodes?.length || 0 }} | <strong>边数量:</strong> {{ graphData.edges?.length || 0 }} | <strong>依赖边数量:</strong> {{ graphData.dependent_edges?.length || 0 }}</p>
        </div>
    <!-- <h2 class="card-title">知识点图谱可视化</h2> -->
    
    <div v-if="!graphData" class="no-data">
      暂无知识图谱数据
    </div>
    
    <div v-else>
      <div class="graph-controls">
        <button @click="zoomIn" class="btn btn-small">
          <i class="icon">+</i> 放大
        </button>
        <button @click="zoomOut" class="btn btn-small">
          <i class="icon">-</i> 缩小
        </button>
        <button @click="fitGraph" class="btn btn-small">
          <i class="icon">⨀</i> 适配屏幕
        </button>
        <button @click="saveGraph" class="btn btn-small" :disabled="!isModified">
          <i class="icon">💾</i> 保存修改
        </button>
        <button @click="startCreateEdge" class="btn btn-small" :disabled="createEdgeMode">
          <i class="icon">🔗</i> 新建关系
        </button>
        <button v-if="createEdgeMode" @click="cancelCreateEdge" class="btn btn-small btn-secondary">
          <i class="icon">❌</i> 取消新建
        </button>
      </div>
      
      <!-- 新建边模式提示 -->
      <div v-if="createEdgeMode" class="edge-create-notice">
        <div class="notice-content">
          <span class="notice-icon">🔗</span>
          <span class="notice-text">
            新建关系模式：
            <span v-if="!firstSelectedNode">请点击选择第一个节点</span>
            <span v-else>已选择: {{ firstSelectedNode.data('label') }} - 请点击选择第二个节点</span>
          </span>
          <button @click="cancelCreateEdge" class="notice-close">×</button>
        </div>
      </div>

      <div class="graph-wrapper" style="position: relative;">
        <div id="cy-graph" class="cy-graph"></div>
      </div>
      
      <div class="instructions">
        <p>操作说明:</p>
        <ul>
          <li>拖拽节点可移动位置</li>
          <li>拖拽节点到其他节点上可建立关系（可选择边类型）</li>
          <li>点击"新建关系"按钮可依次选择节点建立关系</li>
          <li>点击章节节点可查看详情</li>
          <li>点击边可删除关系</li>
        </ul>
      </div>

      <!-- 边类型选择弹窗 -->
      <div v-if="showEdgeTypeModal" class="edge-type-modal-overlay" @click="cancelEdgeCreation">
        <div class="edge-type-modal" @click.stop>
          <h3>选择边类型</h3>
          <p class="modal-subtitle">
            从 <strong>{{ pendingEdgeNodes?.source?.data('label') }}</strong>
            到 <strong>{{ pendingEdgeNodes?.target?.data('label') }}</strong>
          </p>

          <div class="edge-type-options">
            <div
              class="edge-type-option"
              :class="{ disabled: existingEdgeTypes.regular }"
              @click="!existingEdgeTypes.regular && createEdgeWithType('regular')"
            >
              <div class="edge-preview regular-edge">
                <div class="edge-line"></div>
              </div>
              <div class="edge-info">
                <h4>普通关系</h4>
                <p>表示知识点间的学习顺序或相关性</p>
                <div class="edge-details">
                  <span class="edge-style">实线</span>
                  <span class="edge-color">蓝色</span>
                </div>
                <div v-if="existingEdgeTypes.regular" class="edge-exists">
                  <span class="exists-text">✓ 已存在</span>
                </div>
              </div>
            </div>

            <div
              class="edge-type-option"
              :class="{ disabled: existingEdgeTypes.dependent }"
              @click="!existingEdgeTypes.dependent && createEdgeWithType('dependent')"
            >
              <div class="edge-preview dependent-edge">
                <div class="edge-line"></div>
              </div>
              <div class="edge-info">
                <h4>依赖关系</h4>
                <p>表示章节间的学习依赖，必须先完成前置章节</p>
                <div class="edge-details">
                  <span class="edge-style">虚线</span>
                  <span class="edge-color">橙色</span>
                </div>
                <div v-if="existingEdgeTypes.dependent" class="edge-exists">
                  <span class="exists-text">✓ 已存在</span>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button @click="cancelEdgeCreation" class="btn btn-secondary">取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import cytoscape from 'cytoscape';

export default {
  name: 'KnowledgeGraphVisualization',
  props: {
    graphData: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      cy: null,
      isModified: false,
      draggedNode: null, // 跟踪被拖拽的节点
      createEdgeMode: false, // 是否处于新建边模式
      firstSelectedNode: null, // 新建边时的第一个选中节点
      showEdgeTypeModal: false, // 是否显示边类型选择弹窗
      pendingEdgeNodes: null, // 等待创建边的节点对
      existingEdgeTypes: { regular: false, dependent: false } // 已存在的边类型
    };
  },
  watch: {
    graphData: {
      handler(newVal) {
        if (newVal) {
          this.$nextTick(() => {
            this.initGraph();
          });
        }
      },
      immediate: true
    }
  },
  mounted() {
    if (this.graphData) {
      this.initGraph();
    }
  },
  methods: {
    initGraph() {
      if (this.cy) {
        this.cy.destroy();
      }
      
      // 转换数据格式以适配Cytoscape.js
      const elements = this.transformGraphData();
      
      this.cy = cytoscape({
        container: document.getElementById('cy-graph'),
        elements: elements,
        style: [
          {
            selector: 'node',
            style: {
              'label': 'data(label)',
              'text-valign': 'center',
              'text-halign': 'center',
              'color': '#000',
              'background-color': '#4a90e2',
              'width': 100,
              'height': 100,
              'font-size': '12px',
              'font-family': 'Arial, sans-serif',
              'shape': 'ellipse',
              'border-width': 2,
              'border-color': '#357abd'
            }
          },
          {
            selector: 'node[type="chapter"]',
            style: {
              'shape': 'round-rectangle',
              'background-color': '#7aaef8',
              'width': 150,
              'height': 60
            }
          },
          {
            selector: 'node[type="knowledge"]',
            style: {
              'shape': 'ellipse',
              'background-color': '#50e3c2'
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 2,
              'line-color': '#9dbaea',
              'target-arrow-color': '#9dbaea',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              'label': 'data(label)',
              'font-size': '10px',
              'text-background-color': '#fff',
              'text-background-opacity': 1
            }
          },
          {
            selector: 'edge:selected',
            style: {
              'line-color': '#ff4136',
              'target-arrow-color': '#ff4136',
              'width': 3
            }
          },
          {
            selector: '.dependent',
            style: {
              'width': 3,
              'line-color': '#ff9800',
              'target-arrow-color': '#ff9800',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              'line-style': 'dashed',
              'label': '依赖',
              'font-size': '10px',
              'text-background-color': '#fff',
              'text-background-opacity': 1,
              'text-border-color': '#ff9800',
              'text-border-width': 1
            }
          },
          {
            selector: '.dependent:selected',
            style: {
              'line-color': '#ff4136',
              'target-arrow-color': '#ff4136',
              'width': 4
            }
          },
          {
            selector: 'node:selected',
            style: {
              'border-width': 3,
              'border-color': '#ff4136'
            }
          }
        ],
        layout: {
          name: 'cose',
          animate: true,
          fit: true,
          padding: 50
        },
        // 解决被动事件监听器问题
        userPanningEnabled: true,
        userZoomingEnabled: true,
        minZoom: 0.1,
        maxZoom: 2.0,
        wheelSensitivity: 0.1, // 降低滚轮灵敏度
        // 禁用一些可能导致问题的交互
        boxSelectionEnabled: false,
        autounselectify: false,
        autoungrabify: false,
        // 禁用视口优化功能，这些可能导致事件处理问题
        textureOnViewport: false,
        motionBlur: false,
        hideEdgesOnViewport: false,
        hideLabelsOnViewport: false,
        // 禁用触摸相关功能
        touchTapThreshold: 8,
        desktopTapThreshold: 4
      });
      
      this.addEventListeners();
    },
    
    transformGraphData() {
      const elements = [];
      
      // 添加节点
      if (this.graphData.nodes) {
        this.graphData.nodes.forEach(node => {
          elements.push({
            data: {
              id: node.data.id,
              label: node.data.label,
              type: node.data.type,
              select_element: node.data.select_element || []
            },
            group: 'nodes'
          });
        });
      }
      
      // 添加边
      if (this.graphData.edges) {
        this.graphData.edges.forEach((edge, index) => {
          elements.push({
            data: {
              id: `edge-${index}`,
              source: edge.data.source,
              target: edge.data.target,
              label: ''
            },
            group: 'edges'
          });
        });
      }
      
      // 添加依赖边（如果存在）
      if (this.graphData.dependent_edges) {
        this.graphData.dependent_edges.forEach((edge, index) => {
          elements.push({
            data: {
              id: `dep-edge-${index}`,
              source: edge.data.source,
              target: edge.data.target,
              label: '依赖',
              type: 'dependent'
            },
            group: 'edges',
            classes: 'dependent'
          });
        });
      }
      
      return elements;
    },
    
    addEventListeners() {
      // 节点点击事件
      this.cy.on('tap', 'node', (evt) => {
        const node = evt.target;
        const nodeType = node.data('type');

        // 如果处于新建边模式
        if (this.createEdgeMode) {
          this.handleCreateEdgeClick(node);
          return;
        }

        // 根据节点类型执行不同操作
        if (nodeType === 'chapter') {
          // 章节节点显示详情
          this.showNodeDetails(node);
        }
        // 知识点节点的点击功能已取消，不再跳转到学习模块
      });
      
      // 边点击事件
      this.cy.on('tap', 'edge', (evt) => {
        const edge = evt.target;
        const edgeType = edge.data('type');

        // 先设置边为选中状态，让它立即变红显示
        edge.select();

        // 区分依赖边和其他边
        if (edgeType === 'dependent') {
          if (confirm('⚠️ 警告：这是一条依赖关系边，删除后可能影响学习顺序！\n\n确定要删除这条依赖关系吗？')) {
            this.removeEdgeAndUpdateData(edge);
          } else {
            // 如果取消删除，则取消选择状态
            edge.unselect();
          }
        } else {
          if (confirm('确定要删除这条关系吗？')) {
            this.removeEdgeAndUpdateData(edge);
          } else {
            // 如果取消删除，则取消选择状态
            edge.unselect();
          }
        }
      });
      
      // 节点拖拽开始
      this.cy.on('dragstart', 'node', (evt) => {
        this.draggedNode = evt.target;
      });

      // 节点拖拽事件
      this.cy.on('drag', 'node', (evt) => {
        this.isModified = true;
      });

      // 节点拖拽到另一个节点上
      this.cy.on('dragover', 'node', (evt) => {
        // 可以添加视觉反馈，比如高亮目标节点
      });

      // 处理节点放置事件 - 建立边关系
      this.cy.on('drop', 'node', (evt) => {
        const targetNode = evt.target;

        // 确保不是拖拽到自己
        if (this.draggedNode && this.draggedNode !== targetNode) {
          // 检查是否普通边和依赖边都已存在
          const existingEdges = this.cy.edges().filter(edge => {
            return (edge.data('source') === this.draggedNode.id() && edge.data('target') === targetNode.id()) ||
                   (edge.data('source') === targetNode.id() && edge.data('target') === this.draggedNode.id());
          });

          // 统计已存在的边类型
          const hasRegularEdge = existingEdges.some(edge => !edge.hasClass('dependent'));
          const hasDependentEdge = existingEdges.some(edge => edge.hasClass('dependent'));

          // 只有当两种类型的边都存在时，才不允许创建
          if (hasRegularEdge && hasDependentEdge) {
            alert('普通边和依赖边都已存在，无法创建更多关系');
          } else {
            // 记录已存在的边类型，用于在弹窗中禁用相应选项
            this.existingEdgeTypes = {
              regular: hasRegularEdge,
              dependent: hasDependentEdge
            };

            // 显示边类型选择弹窗，让用户选择创建哪种类型的边
            this.pendingEdgeNodes = {
              source: this.draggedNode,
              target: targetNode
            };
            this.showEdgeTypeModal = true;
          }
        }

        this.draggedNode = null;
      });
    },
    
    showNodeDetails(node) {
      const id = node.data('id');
      const label = node.data('label');
      const type = node.data('type');
      
      alert(`节点详情:\nID: ${id}\n标签: ${label}\n类型: ${type}`);
    },
    
    learnKnowledge(node) {
      // 提取节点数据并传递给父组件
      const nodeData = {
        id: node.data('id'),
        label: node.data('label'),
        type: node.data('type'),
        select_element: node.data('select_element') || []
      };
      
      // 通知父组件跳转到学习知识点模块
      this.$emit('learn-knowledge', nodeData);
    },
    
    zoomIn() {
      this.cy.zoom({
        level: this.cy.zoom() * 1.2,
        renderedPosition: { 
          x: this.cy.width() / 2, 
          y: this.cy.height() / 2 
        }
      });
    },
    
    zoomOut() {
      this.cy.zoom({
        level: this.cy.zoom() / 1.2,
        renderedPosition: { 
          x: this.cy.width() / 2, 
          y: this.cy.height() / 2 
        }
      });
    },
    
    fitGraph() {
      this.cy.fit();
    },
    
    saveGraph() {
      // 收集当前图谱数据
      const nodes = this.cy.nodes().map(node => ({
        data: {
          id: node.data('id'),
          label: node.data('label'),
          type: node.data('type'),
          select_element: node.data('select_element') || []
        }
      }));

      // 收集所有边（包括普通边和依赖边）
      const allEdges = this.cy.edges();
      const regularEdges = [];
      const dependentEdges = [];

      allEdges.forEach(edge => {
        const edgeData = {
          data: {
            source: edge.data('source'),
            target: edge.data('target')
          }
        };

        // 根据边类型分类
        if (edge.hasClass('dependent')) {
          dependentEdges.push(edgeData);
        } else {
          regularEdges.push(edgeData);
        }
      });

      const graph = {
        nodes,
        edges: regularEdges,
        dependent_edges: dependentEdges
      };

      console.log('保存的图谱数据:', graph);

      // 通知父组件保存数据
      this.$emit('save-graph', graph);
      this.isModified = false;
    },

    // 开始新建边模式
    startCreateEdge() {
      this.createEdgeMode = true;
      this.firstSelectedNode = null;
      // 状态会通过UI提示显示
    },

    // 取消新建边模式
    cancelCreateEdge() {
      this.createEdgeMode = false;
      this.firstSelectedNode = null;
      // 清除所有节点的选中状态
      this.cy.nodes().unselect();
    },

    // 创建指定类型的边
    createEdgeWithType(edgeType) {
      if (!this.pendingEdgeNodes) return;

      const { source, target } = this.pendingEdgeNodes;

      // 检查是否已经存在相同类型的边
      // 允许普通边和依赖边同时存在，只检查同类型边是否重复
      const existingEdgeOfSameType = this.cy.edges().filter(edge => {
        const isSameDirection = (edge.data('source') === source.id() && edge.data('target') === target.id()) ||
                               (edge.data('source') === target.id() && edge.data('target') === source.id());

        if (!isSameDirection) return false;

        // 检查边的类型是否相同
        const isDependent = edge.hasClass('dependent');
        const targetIsDependent = edgeType === 'dependent';

        return isDependent === targetIsDependent;
      });

      if (existingEdgeOfSameType.length === 0) {
        // 创建新边
        const edgeData = {
          data: {
            id: `edge-${Date.now()}`,
            source: source.id(),
            target: target.id(),
            label: edgeType === 'dependent' ? '依赖' : ''
          },
          group: 'edges'
        };

        // 如果是依赖边，添加CSS类
        if (edgeType === 'dependent') {
          edgeData.classes = 'dependent';
        }

        this.cy.add(edgeData);

        this.isModified = true;
        const typeName = edgeType === 'dependent' ? '依赖关系' : '普通关系';
        alert(`✅ 成功建立${typeName}: ${source.data('label')} → ${target.data('label')}`);
        console.log(`建立了${typeName}: 从 ${source.data('label')} 到 ${target.data('label')}`);
      } else {
        const typeName = edgeType === 'dependent' ? '依赖关系' : '普通关系';
        alert(`❌ ${typeName}已存在，无法重复创建相同类型的边`);
      }

      // 关闭弹窗并重置状态
      this.closeEdgeTypeModal();
    },

    // 取消边创建
    cancelEdgeCreation() {
      this.closeEdgeTypeModal();
    },

    // 关闭边类型选择弹窗
    closeEdgeTypeModal() {
      this.showEdgeTypeModal = false;
      this.pendingEdgeNodes = null;
      this.existingEdgeTypes = { regular: false, dependent: false }; // 重置边类型状态
      this.cancelCreateEdge();
    },

    // 删除边（只改变图谱显示，不立即更新数据）
    removeEdgeAndUpdateData(edge) {
      const edgeType = edge.data('type');

      // 1. 从Cytoscape图谱中删除边（只改变前端显示）
      edge.remove();

      // 2. 设置修改标志（保存时才会更新数据）
      this.isModified = true;

      const typeName = edgeType === 'dependent' ? '依赖关系' : '关系';
      alert(`✅ ${typeName}已从图谱中删除！请记得点击"保存修改"按钮保存更改。`);
    },

    // 处理新建边模式下的节点点击
    handleCreateEdgeClick(node) {
      if (!this.firstSelectedNode) {
        // 选择第一个节点（起始节点）
        this.firstSelectedNode = node;
        node.select();
        // 不显示alert，状态会通过UI提示显示
      } else if (this.firstSelectedNode === node) {
        // 点击同一个节点，取消选择
        this.firstSelectedNode.unselect();
        this.firstSelectedNode = null;
      } else {
        // 选择第二个节点，直接显示边类型选择弹窗
        // 检查是否已经存在边
        const existingEdges = this.cy.edges().filter(edge => {
          return (edge.data('source') === this.firstSelectedNode.id() && edge.data('target') === node.id()) ||
                 (edge.data('source') === node.id() && edge.data('target') === this.firstSelectedNode.id());
        });

        // 统计已存在的边类型
        const hasRegularEdge = existingEdges.some(edge => !edge.hasClass('dependent'));
        const hasDependentEdge = existingEdges.some(edge => edge.hasClass('dependent'));

        // 只有当两种类型的边都存在时，才不允许创建
        if (hasRegularEdge && hasDependentEdge) {
          alert('普通边和依赖边都已存在，无法创建更多关系');
          this.cancelCreateEdge();
          return;
        }

        // 记录已存在的边类型，用于在弹窗中禁用相应选项
        this.existingEdgeTypes = {
          regular: hasRegularEdge,
          dependent: hasDependentEdge
        };

        // 设置待创建的边节点
        this.pendingEdgeNodes = {
          source: this.firstSelectedNode,
          target: node
        };

        // 显示边类型选择弹窗
        this.showEdgeTypeModal = true;
      }
    }
  },
  beforeDestroy() {
    if (this.cy) {
      this.cy.destroy();
    }
  }
};
</script>

<style scoped>
.knowledge-graph-container {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.graph-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.btn-small {
  padding: 6px 12px;
  font-size: 14px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-small:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-small:hover:not(:disabled) {
  background-color: #357abd;
}

.cy-graph {
  width: 100%;
  height: 500px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.instructions {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.instructions p {
  font-weight: bold;
  margin-bottom: 10px;
}

.instructions ul {
  margin: 0;
  padding-left: 20px;
}

.instructions li {
  margin-bottom: 5px;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 18px;
}

/* 新建边模式提示样式 */
.edge-create-notice {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
  padding: 12px;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: 2px solid #2196f3;
  border-radius: 8px;
  animation: pulse 2s infinite;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-width: 400px;
}

.notice-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.notice-icon {
  font-size: 20px;
  animation: bounce 1s infinite alternate;
}

.notice-text {
  flex: 1;
  color: #1565c0;
  font-weight: 600;
  font-size: 15px;
}

.notice-close {
  background: none;
  border: none;
  color: #1565c0;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.notice-close:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(33, 150, 243, 0); }
  100% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0); }
}

@keyframes bounce {
  0% { transform: translateY(0); }
  100% { transform: translateY(-2px); }
}

/* 边类型选择弹窗样式 */
.edge-type-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.edge-type-modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modal-appear 0.3s ease-out;
}

.edge-type-modal h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  text-align: center;
}

.modal-subtitle {
  text-align: center;
  color: #666;
  margin: 0 0 20px 0;
  font-size: 14px;
  padding: 0 20px;
}

.edge-type-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 0 20px;
}

.edge-type-option {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edge-type-option:hover:not(.disabled) {
  border-color: #2196f3;
  background-color: #f8f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.15);
}

.edge-type-option.disabled {
  cursor: not-allowed;
  opacity: 0.5;
  background-color: #f5f5f5;
  border-color: #ccc;
}

.edge-exists {
  margin-top: 8px;
}

.exists-text {
  color: #4caf50;
  font-size: 12px;
  font-weight: 600;
  background-color: #e8f5e8;
  padding: 2px 8px;
  border-radius: 12px;
  border: 1px solid #4caf50;
}

.edge-preview {
  width: 60px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.regular-edge .edge-line {
  width: 40px;
  height: 3px;
  background-color: #9dbaea;
  border-radius: 2px;
}

.dependent-edge .edge-line {
  width: 40px;
  height: 3px;
  background-color: transparent;
  border: 2px dashed #ff9800;
  border-radius: 2px;
}

.edge-info {
  flex: 1;
}

.edge-info h4 {
  margin: 0 0 6px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.edge-info p {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
}

.edge-details {
  display: flex;
  gap: 12px;
  align-items: center;
}

.edge-style, .edge-color {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.edge-style {
  background-color: #f0f0f0;
  color: #666;
}

.edge-color {
  background-color: #e3f2fd;
  color: #1565c0;
}

.modal-actions {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: center;
}

@keyframes modal-appear {
  0% {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.icon {
  margin-right: 5px;
}
</style>