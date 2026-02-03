<template>
  <div class="card">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2 class="card-title">网页预览</h2>
      <button 
        v-if="taskId" 
        @click="refreshPreview" 
        class="btn btn-secondary btn-sm"
      >
        刷新预览
      </button>
    </div>
    
    <div v-if="!taskId">
      <div class="alert alert-warning">
        请先生成网页以进行预览
      </div>
      
      <!-- <div class="form-group">
        <label for="taskIdInput">任务ID:</label>
        <input 
          type="text" 
          id="taskIdInput" 
          v-model="taskIdInput" 
          class="form-control" 
          placeholder="请输入任务ID"
        />
      </div> -->
      
      <!-- <button 
        @click="loadPreview" 
        :disabled="!taskIdInput" 
        class="btn"
      >
        加载预览
      </button> -->
    </div>
    
    <div v-else>
      <div class="preview-container">
        <iframe 
          :src="previewUrl" 
          class="preview-frame"
          frameborder="0"
          @load="onIframeLoad"
        ></iframe>
      </div>
      
      <div class="preview-info mt-2">
        <p>任务ID: {{ taskId }}</p>
      </div>
      
      <div class="mt-3">
        <button @click="resetPreview" class="btn btn-secondary">关闭预览</button>
      </div>
    </div>
  </div>
</template>

<script>
import { previewAPI } from './api/index.js';

export default {
  name: 'PreviewPane',
  data() {
    return {
      taskId: '',
      taskIdInput: '',
      previewUrl: ''
    };
  },
  computed: {
    hasGeneratedFiles() {
      return this.generatedFiles && Object.keys(this.generatedFiles).length > 0;
    }
  },
  methods: {
    loadPreview() {
      if (this.taskIdInput) {
        this.taskId = this.taskIdInput;
        this.previewUrl = `/api/preview/${this.taskId}`;
      }
    },
    
    refreshPreview() {
      // 通过添加时间戳来强制刷新iframe
      this.previewUrl = `/api/preview/${this.taskId}?t=${new Date().getTime()}`;
    },
    
    resetPreview() {
      this.taskId = '';
      this.taskIdInput = '';
      this.previewUrl = '';
    },
    
    onIframeLoad() {
      console.log('预览页面加载完成');
    },

    createLocalPreview(files) {
      try {
        // 查找主要的HTML文件
        const htmlFile = Object.values(files).find(file =>
          file.filename && (
            file.filename.endsWith('.html') ||
            file.filename.endsWith('.htm') ||
            file.filename.includes('index')
          )
        );

        if (htmlFile && htmlFile.content) {
          // 创建blob URL
          const blob = new Blob([htmlFile.content], { type: 'text/html' });
          const url = URL.createObjectURL(blob);

          // 清理之前的URL
          if (this.previewUrl && this.previewUrl.startsWith('blob:')) {
            URL.revokeObjectURL(this.previewUrl);
          }

          this.previewUrl = url;
          console.log('创建本地预览:', htmlFile.filename);
        } else {
          console.warn('未找到可预览的HTML文件');
          // 如果没有HTML文件，回退到API预览
          if (this.taskId) {
            this.previewUrl = `/api/preview/${this.taskId}`;
          }
        }
      } catch (error) {
        console.error('创建本地预览失败:', error);
        // 出错时回退到API预览
        if (this.taskId) {
          this.previewUrl = `/api/preview/${this.taskId}`;
        }
      }
    }
  },
  props: {
    initialTaskId: {
      type: String,
      default: ''
    },
    generatedFiles: {
      type: Object,
      default: null
    }
  },
  watch: {
    initialTaskId: {
      handler(newVal) {
        if (newVal) {
          this.taskId = newVal;
          if (!this.hasGeneratedFiles) {
            this.previewUrl = `/api/preview/${this.taskId}`;
          }
        }
      },
      immediate: true
    },
    generatedFiles: {
      handler(newVal) {
        if (newVal && Object.keys(newVal).length > 0) {
          this.createLocalPreview(newVal);
        }
      },
      immediate: true
    }
  }
};
</script>

<style scoped>
.preview-container {
  width: 100%;
  height: 500px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}

.preview-frame {
  width: 100%;
  height: 100%;
}

.preview-info {
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 14px;
}
</style>