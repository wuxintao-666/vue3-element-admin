<template>
  <div class="knowledge-graph-container">
    <h2 class="card-title">知识点图谱可视化</h2>
    
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
      </div>
      
      <div class="graph-wrapper">
        <div id="cy-graph" class="cy-graph"></div>
      </div>
      
      <div class="instructions">
        <p>操作说明:</p>
        <ul>
          <li>拖拽节点可移动位置</li>
          <li>拖拽节点到其他节点上可建立关系</li>
          <li>点击章节节点可查看详情</li>
          <li>点击知识点节点可学习相关内容</li>
          <li>点击边可删除关系</li>
        </ul>
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
      isModified: false
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
              'color': '#fff',
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
              label: '',
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
        
        // 根据节点类型执行不同操作
        if (nodeType === 'chapter') {
          // 章节节点显示详情
          this.showNodeDetails(node);
        } else {
          // 知识点节点跳转到学习模块
          this.learnKnowledge(node);
        }
      });
      
      // 边点击事件
      this.cy.on('tap', 'edge', (evt) => {
        const edge = evt.target;
        if (confirm('确定要删除这条关系吗？')) {
          edge.remove();
          this.isModified = true;
        }
      });
      
      // 节点拖拽事件
      this.cy.on('drag', 'node', (evt) => {
        this.isModified = true;
      });
      
      // 节点拖拽到另一个节点上
      this.cy.on('dragover', 'node', (evt) => {
        // 拖拽悬停效果
      });
      
      this.cy.on('drop', 'node', (evt) => {
        // 处理节点放置事件
        const draggedNode = evt.target;
        // 这里可以实现节点重新连接的逻辑
        this.isModified = true;
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
      
      const edges = this.cy.edges().map(edge => ({
        data: {
          source: edge.data('source'),
          target: edge.data('target')
        }
      }));
      
      const graph = {
        nodes,
        edges
      };
      
      // 通知父组件保存数据
      this.$emit('save-graph', graph);
      this.isModified = false;
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

.icon {
  margin-right: 5px;
}
</style>