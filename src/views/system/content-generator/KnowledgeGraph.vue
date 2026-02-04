<template>
  <div class="card">
    <h2 class="card-title">生成学习路径</h2>
    
    <!-- 当没有知识图谱时，显示输入界面 -->
    <div v-if="!knowledgeGraph">
      <!-- 如果有参考数据，显示参考信息 -->
      <div v-if="referenceData">
        <div class="alert alert-info">
          <p><strong>参考信息:</strong></p>
          <p>标题: {{ referenceData.title }}</p>
          <p>文本块数量: {{ referenceData.text_blocks?.length || 0 }}</p>
        </div>

        <button
          @click="extractKnowledge"
          class="btn"
        >
          基于参考信息生成学习路径
        </button>

        <button
          @click="extractMockKnowledge"
          class="btn btn-success ml-2"
        >
          模拟生成学习路径
        </button>
      </div>

      <!-- 如果没有参考数据，显示输入表单 -->
      <div v-else>
        <div class="form-group">
          <label for="referenceUrl">参考网站URL:</label>
          <input
            type="url"
            id="referenceUrl"
            :value="referenceUrlInput"
            @input="referenceUrlInput = $event.target.value"
            class="form-control"
            placeholder="https://example.com"
          />
        </div>

        <div class="form-group">
          <label for="uploadedFile">或上传HTML文件:</label>
          <input
            type="file"
            id="uploadedFile"
            @change="handleFileUpload"
            class="form-control"
            accept=".html,.htm"
          />
        </div>

        <button
          @click="extractKnowledge"
          :disabled="!referenceUrlInput && !uploadedFileInput"
          class="btn"
        >
          生成学习路径
        </button>

        <button
          @click="extractMockKnowledge"
          :disabled="!referenceUrlInput && !uploadedFileInput"
          class="btn btn-success ml-2"
        >
          模拟生成学习路径
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="mt-3 text-center">
        <div class="spinner"></div>
        <p class="mt-2">正在生成学习路径...</p>
      </div>
    </div>

    <!-- 当有知识图谱时，显示图谱内容 -->
    <div v-else>
      <div class="alert alert-success">
        提取成功！共 {{ knowledgeGraph.nodes.length }} 个学习结点。
      </div>
      
      <div class="form-group">
        <label for="graphName">图谱名称:</label>
        <input 
          type="text" 
          id="graphName" 
          v-model="graphName" 
          class="form-control" 
          placeholder="请输入知识点图谱名称"
        />
      </div>
      
      <!-- 切换视图 -->
      <div class="view-toggle">
        <button 
          @click="currentView = 'list'" 
          :class="['btn', 'btn-small', { 'btn-primary': currentView === 'list' }]"
        >
          列表视图
        </button>
        <button 
          @click="currentView = 'graph'" 
          :class="['btn', 'btn-small', { 'btn-primary': currentView === 'graph' }]"
        >
          图谱视图
        </button>
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
              <span class="knowledge-id">{{ index + 1 }}.</span>
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
      
      <!-- 图谱视图 -->
      <div v-else-if="currentView === 'graph'">
        <KnowledgeGraphVisualization
          :graph-data="knowledgeGraph"
          @save-graph="handleSaveGraph"
          @update-graph-data="handleUpdateGraphData"
          @learn-knowledge="learnKnowledge"
        />
      </div>
      
      <div class="d-flex justify-content-between">
        <div>
          <button @click="resetKnowledge" class="btn btn-secondary">重新生成</button>
          <button 
            v-if="savedKnowledgeId" 
            @click="downloadKnowledgeGraph" 
            class="btn btn-info ml-2"
          >
            下载图谱
          </button>
        </div>
        <div class="save-buttons">
          <!-- <button @click="saveKnowledgeGraph" class="btn btn-success" :disabled="!graphName">保存到文件</button> -->
          <button @click="saveKnowledgeGraphToDatabase" class="btn btn-primary ml-2" :disabled="!graphName">保存</button>
        </div>
      </div>

      <!-- 详情弹窗 -->
      <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
        <div class="modal-content detail-modal" @click.stop>
          <div class="modal-header">
            <h3>知识点详情</h3>
            <button @click="closeDetailModal" class="close-btn">&times;</button>
          </div>

          <div class="modal-body" v-if="detailNode">
            <div class="detail-section">
              <h4>基本信息</h4>
              <div class="info-grid">
                <div class="info-item">
                  <strong>ID:</strong> {{ detailNode.id }}
                </div>
                <div class="info-item">
                  <strong>类型:</strong>
                  <span :class="'type-badge ' + detailNode.type">
                    {{ detailNode.type === 'chapter' ? '章节' : '知识点' }}
                  </span>
                </div>
                <div class="info-item">
                  <strong>标题:</strong> {{ detailNode.label }}
                </div>
              </div>
            </div>

            <!-- AI提取的相关内容 -->
            <div class="detail-section" v-if="detailNode.select_element && detailNode.select_element.length > 0">
              <h4>AI提取的元素抓取元素 ({{ detailNode.select_element.length }} 个)</h4>
              <div class="select-elements">
                <div
                  v-for="(element, idx) in detailNode.select_element"
                  :key="idx"
                  class="element-tag"
                >
                  <code>{{ element }}</code>
                </div>
              </div>
            </div>

            <!-- 如果没有相关内容 -->
            <div class="detail-section" v-else>
              <h4>AI提取的元素抓取元素</h4>
              <div class="no-content">
                <p>暂无相关提取元素</p>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button @click="editNode(detailNode)" class="btn btn-warning">编辑</button>
            <button @click="closeDetailModal" class="btn btn-secondary ml-2">关闭</button>
          </div>
        </div>
      </div>

      <!-- 编辑弹窗 -->
      <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>编辑知识点</h3>
            <button @click="closeEditModal" class="close-btn">&times;</button>
          </div>

          <div class="modal-body" v-if="editingNode">
            <div class="form-row">
              <label>知识点ID:</label>
              <input
                v-model="editingNode.id"
                class="form-control"
                readonly
                disabled
              />
            </div>

            <div class="form-row">
              <label>知识点标题:</label>
              <input
                v-model="editingNode.label"
                class="form-control"
                placeholder="请输入知识点标题"
              />
            </div>

            <div class="form-row">
              <label>相关技术元素 (每行一个):</label>
              <textarea
                v-model="editingNode.select_element_text"
                class="form-control"
                rows="6"
                placeholder="请输入相关的HTML标签、CSS属性等，每行一个&#10;例如:&#10;h1&#10;p&#10;div"
              ></textarea>
              
            </div>
          </div>

          <div class="modal-footer">
            <button @click="saveNodeEdit" class="btn btn-success">保存修改</button>
            <button @click="closeEditModal" class="btn btn-secondary ml-2">取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { knowledgeAPI, uploadAPI } from './api/index.js';
import KnowledgeGraphVisualization from './KnowledgeGraphVisualization.vue';
import { TEST_COURSE_ID } from '@/constants';

export default {
  name: 'KnowledgeGraph',
  components: {
    KnowledgeGraphVisualization
  },
  props: {
    referenceData: {
      type: Object,
      default: null
    },
    knowledgeData: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      referenceUrlInput: '',
      uploadedFileInput: null,
      knowledgeGraph: null,
      graphName: '',
      loading: false,
      savedKnowledgeId: null,
      currentView: 'list', // 'list' 或 'graph'
      detailNode: null, // 当前查看详情的节点
      editingNode: null, // 当前正在编辑的节点
      editNodeBackup: null, // 编辑前的备份数据
      isKnowledgeSaved: false, // 是否已保存知识图谱
      showDetailModal: false, // 是否显示详情弹窗
      showEditModal: false // 是否显示编辑弹窗
    };
  },
  watch: {
    knowledgeData: {
      handler(newVal) {
        if (newVal) {
          this.knowledgeGraph = newVal.graph;
          this.graphName = newVal.name;
        }
      },
      immediate: true
    },
    referenceData: {
      handler(newVal) {
        if (newVal && newVal.url) {
          this.referenceUrlInput = newVal.url;
        }
      },
      immediate: true
    }
  },
  methods: {
    handleFileUpload(event) {
      const files = event.target.files;
      if (files.length > 0) {
        this.uploadedFileInput = files[0];
        this.referenceUrlInput = ''; // 清除URL输入
      }
    },
    
    async extractKnowledge() {
      this.loading = true;
      
      try {
        let knowledgeData;
        
        // 根据参考数据中的type属性调用不同的接口
        if (this.referenceData && this.referenceData.type === 'file') {
          // 通过上传文件提取知识点
          console.log("通过上传文件提取知识点");
          const formData = new FormData();
          formData.append('file', this.referenceData.file);
          const response = await uploadAPI.extractKnowledgeFromFile(formData);
          knowledgeData = response.graph;
          this.graphName = `知识点: ${this.referenceData.file.name}`;
        } else if (this.referenceData && this.referenceData.type === 'url') {
          // 通过URL提取知识点
          console.log("通过上传的URL提取知识点");
          const requestData = { reference_url: this.referenceData.url };
          const response = await knowledgeAPI.extractKnowledge(requestData);
          knowledgeData = response.graph;
          this.graphName = `知识点: ${new URL(this.referenceData.url).hostname}`;
        } else if (this.uploadedFileInput) {
          // 通过当前选择的文件提取知识点
          console.log("通过当前选择的文件提取知识点");
          const formData = new FormData();
          formData.append('file', this.uploadedFileInput);
          const response = await uploadAPI.extractKnowledgeFromFile(formData);
          knowledgeData = response.graph;
          this.graphName = `知识点: ${this.uploadedFileInput.name}`;
        } else if (this.referenceUrlInput) {
          // 通过当前输入的URL提取知识点
          console.log("通过当前输入的URL提取知识点");
          const requestData = { reference_url: this.referenceUrlInput };
          const response = await knowledgeAPI.extractKnowledge(requestData);
          knowledgeData = response.graph;
          this.graphName = `知识点: ${new URL(this.referenceUrlInput).hostname}`;
        } else if (this.referenceData) {
          // 基于参考数据提取知识点（当没有明确的上传类型时）
          console.log("基于参考数据提取知识点（没有明确的上传类型）");
          const requestData = { reference_info: this.referenceData };
          const response = await knowledgeAPI.extractKnowledge(requestData);
          knowledgeData = response.graph;
          this.graphName = `知识点: ${this.referenceData.title}`;
        } else {
          throw new Error('请选择一个文件或输入一个URL');
        }
        
        this.knowledgeGraph = knowledgeData;

        // 调试：打印后端返回的数据结构
        console.log('后端返回的知识图谱数据:', knowledgeData);
        console.log('知识图谱节点数量:', knowledgeData.nodes ? knowledgeData.nodes.length : 0);
        if (knowledgeData.nodes && knowledgeData.nodes.length > 0) {
          console.log('第一个节点的数据结构:', knowledgeData.nodes[0]);
          console.log('第一个节点的所有属性:', Object.keys(knowledgeData.nodes[0].data));
        }

        // 通知父组件知识点已提取
        try {
          this.$emit && this.$emit('knowledge-extracted', {
            graph: knowledgeData,
            name: this.graphName
          });
        } catch (err) {
          console.warn('emit knowledge-extracted failed:', err);
        }
      } catch (error) {
        console.error('知识点提取失败:', error);
        if (error.response && error.response.status) {
          alert('知识点提取失败: HTTP错误 ' + error.response.status);
        } else if (error.message) {
          alert('知识点提取失败: ' + error.message);
        } else {
          alert('知识点提取失败: ' + JSON.stringify(error));
        }
      } finally {
        this.loading = false;
      }
    },

    async extractMockKnowledge() {
      this.loading = true;

      try {
        // 模拟API调用延迟
        await new Promise(resolve => setTimeout(resolve, 2000));

        // 生成模拟的知识图谱
        const mockGraph = this.generateMockKnowledgeGraph();

        this.knowledgeGraph = mockGraph;

        // 设置图谱名称
        if (this.referenceData) {
          this.graphName = this.referenceData.title;
        } else if (this.referenceUrlInput) {
          this.graphName = new URL(this.referenceUrlInput).hostname;
        } else if (this.uploadedFileInput) {
          this.graphName = this.uploadedFileInput.name;
        } else {
          this.graphName = '模拟知识图谱';
        }

        // 通知父组件知识点已提取
        try {
          this.$emit('knowledge-extracted', {
            graph: mockGraph,
            name: this.graphName
          });
        } catch (err) {
          console.warn('emit knowledge-extracted failed:', err);
        }

        console.log('模拟知识图谱生成成功');
      } catch (error) {
        console.error('模拟知识图谱生成失败:', error);
        alert('模拟知识图谱生成失败: ' + error.message);
      } finally {
        this.loading = false;
      }
    },

    generateMockKnowledgeGraph() {
      // 生成两章每章三个小节的模拟知识图谱
      return {
        nodes: [
          {
            data: {
              id: '1_end',
              label: '模块一: HTML基础',
              type: 'chapter'
            }
          },
          {
            data: {
              id: '1_1',
              label: '了解HTML基本结构',
              type: 'knowledge',
              select_element: [
                'html',
                'head',
                'body',
                'title'
              ]
            }
          },
          {
            data: {
              id: '1_2',
              label: '使用标题元素h1-h6',
              type: 'knowledge',
              select_element: [
                'h1',
                'h2',
                'h3',
                'h4',
                'h5',
                'h6'
              ]
            }
          },
          {
            data: {
              id: '1_3',
              label: '创建段落元素p',
              type: 'knowledge',
              select_element: [
                'p',
                'br',
                'hr'
              ]
            }
          },
          {
            data: {
              id: '2_end',
              label: '模块二: CSS样式',
              type: 'chapter'
            }
          },
          {
            data: {
              id: '2_1',
              label: '理解CSS基本语法',
              type: 'knowledge',
              select_element: [
                'style',
                'link',
                'css'
              ]
            }
          },
          {
            data: {
              id: '2_2',
              label: '应用文本样式',
              type: 'knowledge',
              select_element: [
                'color',
                'font-size',
                'font-weight',
                'text-align'
              ]
            }
          },
          {
            data: {
              id: '2_3',
              label: '使用CSS盒模型',
              type: 'knowledge',
              select_element: [
                'margin',
                'padding',
                'border',
                'width',
                'height'
              ]
            }
          }
        ],
        edges: [
          {
            data: {
              source: '1_end',
              target: '1_1'
            }
          },
          {
            data: {
              source: '1_end',
              target: '1_2'
            }
          },
          {
            data: {
              source: '1_end',
              target: '1_3'
            }
          },
          {
            data: {
              source: '2_end',
              target: '2_1'
            }
          },
          {
            data: {
              source: '2_end',
              target: '2_2'
            }
          },
          {
            data: {
              source: '2_end',
              target: '2_3'
            }
          }
        ],
        dependent_edges: [
          {
            data: {
              source: '1_1',
              target: '1_2'
            }
          },
          {
            data: {
              source: '1_2',
              target: '1_3'
            }
          },
          {
            data: {
              source: '2_1',
              target: '2_2'
            }
          },
          {
            data: {
              source: '2_2',
              target: '2_3'
            }
          }
        ]
      };
    },
    
    handleSaveGraph(graph) {
      // 更新当前知识图谱数据
      this.knowledgeGraph = graph;

      // 通知父组件更新knowledgeData
      if (this.$parent && this.$emit) {
        try {
          this.$emit('knowledge-updated', {
            graph: graph,
            name: this.graphName
          });
        } catch (error) {
          console.warn('emit knowledge-updated failed:', error);
        }
      }

      alert('图谱修改已保存到本地');
    },

    handleUpdateGraphData(updatedGraphData) {
      // 更新知识图谱数据
      this.knowledgeGraph = updatedGraphData;
      console.log('知识图谱数据已更新');

      // 确保组件仍然有效且可以emit
      if (this.$parent && this.$emit) {
        try {
          // 通知父组件更新knowledgeData
          this.$emit('knowledge-updated', {
            graph: updatedGraphData,
            name: this.graphName
          });
        } catch (error) {
          console.warn('emit knowledge-updated failed:', error);
        }
      }
    },
    
    async saveKnowledgeGraph() {
      if (!this.graphName || !this.knowledgeGraph) {
        alert('请填写图谱名称并确保已提取知识点');
        return;
      }

      try {
        const requestData = {
          name: this.graphName,
          graph: this.knowledgeGraph
        };

        const response = await knowledgeAPI.saveKnowledgeGraph(requestData);
        this.savedKnowledgeId = response.id;
        this.isKnowledgeSaved = true; // 标记为已保存
        alert('知识点图谱保存成功！现在可以继续下一步了。');
        try {
          this.$emit && this.$emit('knowledge-saved');
        } catch (err) {
          console.warn('emit knowledge-saved failed:', err);
        }
      } catch (error) {
        console.error('知识点图谱保存失败:', error);
        alert('知识点图谱保存失败: ' + (error.message || '未知错误'));
      }
    },

    async saveKnowledgeGraphToDatabase() {
      if (!this.graphName || !this.knowledgeGraph) {
        alert('请填写图谱名称并确保已提取知识点');
        return;
      }

      // 获取course_code（这里假设从某个地方获取，暂时使用默认值）
      const courseCode = TEST_COURSE_ID; // 从环境变量获取测试课程ID

      try {
        const requestData = {
          course_code: courseCode,
          name: this.graphName,
          graph: this.knowledgeGraph
        };
        
        const response = await knowledgeAPI.saveKnowledgeGraphToDatabase(requestData);
        this.isKnowledgeSaved = true; // 标记为已保存
        alert(`知识点图谱保存到数据库成功！\n课程代码: ${response.course_code}\n保存了 ${response.nodes_count} 个节点和 ${response.edges_count} 条边`);
        try {
          this.$emit && this.$emit('knowledge-saved');
        } catch (err) {
          console.warn('emit knowledge-saved failed:', err);
        }
      } catch (error) {
        console.error('知识点图谱保存到数据库失败:', error);
        alert('知识点图谱保存到数据库失败: ' + (error.response?.data?.detail || error.message || '未知错误'));
      }
    },
    
    async downloadKnowledgeGraph() {
      if (this.savedKnowledgeId) {
        try {
          await knowledgeAPI.downloadKnowledgeGraph(this.savedKnowledgeId);
        } catch (error) {
          console.error('知识点图谱下载失败:', error);
          alert('知识点图谱下载失败: ' + (error.message || '未知错误'));
        }
      }
    },
    
    resetKnowledge() {
      this.referenceUrlInput = '';
      this.uploadedFileInput = null;
      this.knowledgeGraph = null;
      this.graphName = '';
      this.savedKnowledgeId = null;
      this.currentView = 'list';
      const fileInput = document.getElementById('uploadedFile');
      if (fileInput) {
        fileInput.value = ''; // 清空文件输入
      }
    },
    
    showNodeDetail(nodeData) {
      this.detailNode = nodeData;
      this.showDetailModal = true;
    },

    editNode(nodeData) {
      // 备份原始数据
      this.editNodeBackup = JSON.parse(JSON.stringify(nodeData));

      // 创建编辑副本
      this.editingNode = {
        id: nodeData.id,
        label: nodeData.label,
        select_element_text: (nodeData.select_element || []).join('\n')
      };

      // 显示编辑弹窗
      this.showEditModal = true;
    },

    saveNodeEdit() {
      if (!this.editingNode) return;

      // 更新原始节点数据
      const nodeIndex = this.knowledgeGraph.nodes.findIndex(node => node.data.id === this.editingNode.id);
      if (nodeIndex > -1) {
        const node = this.knowledgeGraph.nodes[nodeIndex];

        // 更新基本信息
        node.data.label = this.editingNode.label;

        // 更新技术元素数组
        node.data.select_element = this.editingNode.select_element_text
          ? this.editingNode.select_element_text.split('\n').filter(item => item.trim())
          : [];

        alert('知识点修改已保存到本地！请记得点击"保存图谱"按钮保存到服务器。');
      }

      // 关闭弹窗
      this.closeEditModal();
    },

    cancelNodeEdit() {
      // 恢复原始数据
      if (this.editNodeBackup) {
        const nodeIndex = this.knowledgeGraph.nodes.findIndex(node => node.data.id === this.editingNode.id);
        if (nodeIndex > -1) {
          this.knowledgeGraph.nodes[nodeIndex].data = JSON.parse(JSON.stringify(this.editNodeBackup));
        }
      }

      // 关闭弹窗
      this.closeEditModal();
    },

    closeDetailModal() {
      this.showDetailModal = false;
      this.detailNode = null;
    },

    closeEditModal() {
      this.showEditModal = false;
      this.editingNode = null;
      this.editNodeBackup = null;
    },

    learnKnowledge(nodeData) {
      // 通知父组件跳转到学习知识点模块
      try {
        this.$emit && this.$emit('learn-knowledge', nodeData);
      } catch (err) {
        console.warn('emit learn-knowledge failed:', err);
      }
    }
  }
};
</script>

<style scoped>
.knowledge-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 1rem;
}

.knowledge-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.knowledge-item:last-child {
  border-bottom: none;
}

.knowledge-id {
  font-weight: bold;
  color: var(--primary-color);
  margin-right: 0.5rem;
}

.knowledge-label {
  color: var(--dark-color);
  flex: 1;
}

.ml-2 {
  margin-left: 0.5rem;
}

.ml-auto {
  margin-left: auto;
}

.view-toggle {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.btn-small {
  padding: 5px 10px;
  font-size: 14px;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

/* 新增样式 */
.knowledge-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.knowledge-type {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.knowledge-type.chapter {
  background-color: #e3f2fd;
  color: #1976d2;
}

.knowledge-type.knowledge {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.knowledge-actions {
  margin-left: auto;
  display: flex;
  gap: 5px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.info-item {
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  font-size: 13px;
}

.select-elements {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.element-tag {
  background: #e8f5e8;
  border: 1px solid #4caf50;
  border-radius: 16px;
  padding: 4px 12px;
}

.element-tag code {
  color: #2e7d32;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.no-content {
  color: #999;
  font-style: italic;
  margin: 0;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.no-content p {
  margin: 0;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 15px;
}

.form-row label {
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.form-hint {
  color: #666;
  font-size: 12px;
  margin-top: 5px;
}

.save-prompt {
  margin-top: 20px;
  padding: 15px;
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
}

.save-prompt .alert {
  margin: 0;
  padding: 12px 16px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.detail-modal .modal-content {
  max-width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #f0f0f0;
  color: #333;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  background-color: #f8f9fa;
  border-radius: 0 0 8px 8px;
  display: flex;
  justify-content: flex-end;
}

/* 详情弹窗专用样式 */
.detail-section {
  margin-bottom: 20px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 8px;
}

.type-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.type-badge.chapter {
  background-color: #e3f2fd;
  color: #1976d2;
}

.type-badge.knowledge {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.element-description {
  margin-top: 10px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

.element-description p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.save-buttons {
  display: flex;
  gap: 10px;
}
</style>