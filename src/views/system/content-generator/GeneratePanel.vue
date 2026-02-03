<template>
  <div class="card">
    <h2 class="card-title">网页生成</h2>
    
    <div v-if="!userState.taskId">
      <div v-if="!prdData || !knowledgeData">
        <div class="alert alert-warning">
          请先完成PRD文档和知识点图谱的生成与保存
        </div>
      </div>
      
      <div v-else>
        <div class="form-group">
          <label>设计文档:</label>
          <div class="form-control">
            <p><strong>{{ prdData.title }}</strong></p>
            <p class="text-muted">内容长度: {{ prdData.content?.length || 0 }} 字符</p>
          </div>
        </div>
        
        <div class="form-group">
          <label>知识点图谱:</label>
          <div class="form-control">
            <p><strong>{{ knowledgeData.name }}</strong></p>
            <p class="text-muted">知识点数量: {{ knowledgeData.graph?.nodes?.length || 0 }} 个</p>
          </div>
        </div>
        
        <div class="form-group">
          <label for="userNote">用户备注:</label>
          <input 
            type="text" 
            id="userNote" 
            v-model="userNote" 
            class="form-control" 
            placeholder="可选：添加一些备注信息"
          />
        </div>
        
        <button
          @click="generateWebsite"
          class="btn"
        >
          生成网页
        </button>

        <button
          @click="generateMockWebsite"
          class="btn btn-success ml-2"
        >
          模拟生成网页
        </button>
      </div>
      
      <div v-if="loading" class="mt-3 text-center">
        <div class="spinner"></div>
        <p class="mt-2">正在生成网页...</p>
      </div>
    </div>
    
    <div v-else>
      <div class="alert alert-success">
        网页生成成功！
      </div>
      
      <div class="form-group">
        <label>任务ID:</label>
        <div class="form-control">
          {{ userState.taskId }}
        </div>
      </div>
      
      <!-- <div class="form-group">
        <label>生成的文件:</label>
        <ul>
          <li v-for="fileName in getFileNames(userState.files)" :key="fileName">{{ fileName }}</li>
        </ul>
      </div> -->
      
      <div class="d-flex justify-content-between">
        <div>
          <button @click="resetGeneration" class="btn btn-secondary">重新生成</button>
          <button 
            v-if="taskId" 
            @click="downloadGeneratedFiles" 
            class="btn btn-info ml-2"
          >
            下载网页文件
          </button>
        </div>
        <button @click="previewWebsite" class="btn btn-primary">预览网页</button>
      </div>
    </div>
  </div>
</template>

<script>
import { executorAPI } from './api/index.js';

export default {
  name: 'GeneratePanel',
  props: {
    prdData: {
      type: Object,
      default: null
    },
    knowledgeData: {
      type: Object,
      default: null
    },
    userState: {
      type: Object,
      default: () => ({ taskId: '', files: null, userNote: '' })
    }
  },
  data() {
    return {
      userNote: '',
      generatedFiles: null,
      taskId: '',
      loading: false
    };
  },
  methods: {
    updateUserState() {
      // 更新父组件的 userState
      if (this.userState) {
        this.userState.taskId = this.taskId;
        this.userState.files = this.generatedFiles;
        this.userState.userNote = this.userNote;
        console.log('GeneratePanel 已更新 userState:', this.userState);
      }
    },

    getFileNames(files) {
      // 处理不同格式的文件数据
      if (!files) return [];

      // 如果是数组格式（后端API返回）
      if (Array.isArray(files)) {
        return files;
      }

      // 如果是对象格式（前端模拟生成）
      if (typeof files === 'object') {
        return Object.keys(files);
      }

      return [];
    },

    async generateWebsite() {
      this.loading = true;
      
      try {
        const requestData = {
          prd: {
            title: this.prdData.title,
            content: this.prdData.content
          },
          knowledge_graph: {
            name: this.knowledgeData.name,
            graph: this.knowledgeData.graph
          },
          user_note: this.userNote
        };
        
        const response = await executorAPI.executeTask(requestData);
        
        this.generatedFiles = response.files;
        this.taskId = response.task_id;

        // 更新父组件的 userState
        this.updateUserState();

        this.$emit('website-generated', {
          taskId: this.taskId,
          files: this.generatedFiles,
          userNote: this.userNote
        });
      } catch (error) {
        console.error('网页生成失败:', error);
        if (error.response && error.response.status) {
          alert('网页生成失败: HTTP错误 ' + error.response.status);
        } else {
          alert('网页生成失败: ' + (error.message || '未知错误'));
        }
      } finally {
        this.loading = false;
      }
    },

    async generateMockWebsite() {
      this.loading = true;

      try {
        // 模拟API调用延迟
        await new Promise(resolve => setTimeout(resolve, 3000));

        // 使用已有的成功任务ID进行模拟（直接复用现有的HTML内容）
        this.taskId = 'c1dcf247-a3d3-4aff-bab0-7a9af646e7d9'; // 使用已存在的任务ID

        // 模拟生成的文件列表（基于已有的任务数据）
        this.generatedFiles = {
          'index.html': {
            filename: 'index.html',
            content: 'Mock HTML content from existing task',
            type: 'text/html'
          }
        };

        // 更新父组件的 userState
        this.updateUserState();

        // 通知父组件网页已生成
        console.log('GeneratePanel 模拟生成，使用现有任务ID:', this.taskId);
        this.$emit('website-generated', {
          taskId: this.taskId,
          files: this.generatedFiles,
          userNote: this.userNote
        });

        console.log('模拟网页生成成功');
      } catch (error) {
        console.error('模拟网页生成失败:', error);
        alert('模拟网页生成失败: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    previewWebsite() {
      if (this.taskId) {
        // 打开新窗口预览网页
        window.open(`/api/preview/${this.taskId}`, '_blank');
      }
    },
    
    async downloadGeneratedFiles() {
      if (this.taskId) {
        try {
          await executorAPI.downloadGeneratedFiles(this.taskId);
        } catch (error) {
          console.error('网页文件下载失败:', error);
          alert('网页文件下载失败: ' + (error.message || '未知错误'));
        }
      }
    },
    
    resetGeneration() {
      this.userNote = '';
      this.generatedFiles = null;
      this.taskId = '';

      // 同时重置父组件的 userState
      this.updateUserState();
    }
  }
};
</script>

<style scoped>
/* 卡片样式优化 */
.card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.card-title {
  color: #2c3e50;
  font-weight: 600;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

/* 表单组样式 */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.5rem;
  display: block;
  font-size: 0.95rem;
}

.form-control {
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 0.75rem;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.form-control:hover {
  border-color: #dee2e6;
}

.form-control:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  background-color: #ffffff;
}

/* 输入框样式 */
.form-control input {
  border: none;
  background: transparent;
  width: 100%;
  font-size: 0.9rem;
}

.form-control input:focus {
  outline: none;
}

/* 按钮样式优化 */
.btn {
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn:active {
  transform: translateY(0);
}

/* 文件列表样式 */
ul {
  list-style: none;
  padding: 0;
  margin: 0;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #dee2e6;
}

ul li {
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.5rem;
  background: white;
  border-radius: 6px;
  border-left: 4px solid #007bff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.85rem;
  color: #495057;
  display: flex;
  align-items: center;
}

ul li:last-child {
  margin-bottom: 0;
}

ul li:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-left-color: #0056b3;
}

ul li:before {
  content: '📄';
  margin-right: 0.5rem;
  font-size: 1rem;
}

/* 警告和成功提示样式 */
.alert {
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border: none;
}

.alert-warning {
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  color: #856404;
  border-left: 4px solid #ffc107;
}

.alert-success {
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
  color: #155724;
  border-left: 4px solid #28a745;
  animation: successPulse 0.6s ease-in-out;
}

@keyframes successPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

/* 加载状态样式 */
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 按钮组样式 */
.d-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.d-flex > div {
  display: flex;
  gap: 0.5rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card {
    margin: 1rem;
  }

  .btn {
    padding: 0.6rem 1.2rem;
    font-size: 0.9rem;
  }

  .d-flex {
    flex-direction: column;
    align-items: stretch;
  }

  .d-flex > div {
    flex-direction: column;
  }
}

/* 文本颜色优化 */
.text-muted {
  color: #6c757d !important;
  font-size: 0.85rem;
}

.text-center {
  text-align: center;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mt-3 {
  margin-top: 1rem;
}

.ml-2 {
  margin-left: 0.5rem;
}
</style>