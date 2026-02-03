<template>
  <div class="card">
    <h2 class="card-title">设计文档生成</h2>
    
    <div v-if="!prdContent">
      <div v-if="referenceData">
        <div class="alert alert-info">
          <p><strong>参考信息:</strong></p>
          <p>标题: {{ referenceData.title }}</p>
          <p>文本块数量: {{ referenceData.text_blocks?.length || 0 }}</p>
        </div>
        
        <button
          @click="generatePRD"
          class="btn"
        >
          基于参考信息生成设计文档
        </button>

        <button
          @click="generateMockPRD"
          class="btn btn-success ml-2"
        >
          模拟生成PRD
        </button>
      </div>
      
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
          @click="generatePRD"
          :disabled="!referenceUrlInput && !uploadedFileInput"
          class="btn"
        >
          生成设计文档
        </button>

        <button
          @click="generateMockPRD"
          :disabled="!referenceUrlInput && !uploadedFileInput"
          class="btn btn-success ml-2"
        >
          模拟生成PRD
        </button>
      </div>
      
      <div v-if="loading" class="mt-3 text-center">
        <div class="spinner"></div>
        <p class="mt-2">正在生成PRD文档...</p>
      </div>
    </div>
    
    <div v-else>
      <div class="alert alert-success">
        设计文档生成成功！
      </div>
      
      <div class="form-group">
        <label for="prdTitle">设计文档标题:</label>
        <input 
          type="text" 
          id="prdTitle" 
          v-model="prdTitle" 
          class="form-control" 
          placeholder="请输入PRD标题"
        />
      </div>
      
      <div class="form-group">
        <label>设计文档内容:</label>
        <textarea 
          class="form-control" 
          rows="15" 
          v-model="prdContent"
          readonly
        ></textarea>
      </div>
      
      <div class="d-flex justify-content-between">
        <div>
          <button @click="resetPRD" class="btn btn-secondary">重新生成</button>
          <button 
            v-if="savedPRDId" 
            @click="downloadPRD" 
            class="btn btn-info ml-2"
          >
            下载设计文档
          </button>
        </div>
        <button @click="savePRD" class="btn btn-success" :disabled="!prdTitle">保存设计文档</button>
      </div>
    </div>
  </div>
</template>

<script>
import { prdAPI, uploadAPI } from './api/index.js';

export default {
  name: 'PRDPanel',
  props: {
    referenceData: {
      type: Object,
      default: null
    },
    prdData: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      referenceUrlInput: '',
      uploadedFileInput: null,
      prdContent: '',
      prdTitle: '',
      loading: false,
      savedPRDId: null
    };
  },
  watch: {
    prdData: {
      handler(newVal) {
        if (newVal) {
          this.prdContent = newVal.content;
          this.prdTitle = newVal.title;
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
    
    async generatePRD() {
      this.loading = true;
      
      try {
        let prdData;
        
        // 根据参考数据中的type属性调用不同的接口
        if (this.referenceData && this.referenceData.type === 'file') {
          // 通过上传文件生成PRD
          console.log("通过上传文件生成PRD");
          const formData = new FormData();
          formData.append('file', this.referenceData.file);
          const response = await uploadAPI.generatePRDFromFile(formData);
          prdData = response.prd_text;
          this.prdTitle = `PRD: ${this.referenceData.file.name}`;
        } else if (this.referenceData && this.referenceData.type === 'url') {
          // 通过URL生成PRD
          console.log("通过上传的URL生成PRD");
          const requestData = { reference_url: this.referenceData.url };
          const response = await prdAPI.generatePRD(requestData);
          prdData = response.prd_text;
          this.prdTitle = `PRD: ${new URL(this.referenceData.url).hostname}`;
        } else if (this.uploadedFileInput) {
          // 通过当前选择的文件生成PRD
          console.log("通过当前选择的文件生成PRD");
          console.log("uploadedFileInput:", uploadedFileInput);
          const formData = new FormData();
          formData.append('file', this.uploadedFileInput);
          const response = await uploadAPI.generatePRDFromFile(formData);
          prdData = response.prd_text;
          this.prdTitle = `PRD: ${this.uploadedFileInput.name}`;
        } else if (this.referenceUrlInput) {
          // 通过当前输入的URL生成PRD
          console.log("通过当前输入的URL生成PRD");
          console.log("referenceUrlInput:", referenceUrlInput);
          const requestData = { reference_url: this.referenceUrlInput };
          const response = await prdAPI.generatePRD(requestData);
          prdData = response.prd_text;
          this.prdTitle = `PRD: ${new URL(this.referenceUrlInput).hostname}`;
        } else if (this.referenceData) {
          // 基于参考数据生成PRD（当没有明确的上传类型时）
          console.log("基于参考数据生成PRD（没有明确的上传类型）");
          const requestData = { reference_info: this.referenceData };
          const response = await prdAPI.generatePRD(requestData);
          prdData = response.prd_text;
          this.prdTitle = `PRD: ${this.referenceData.title}`;
        } else {
          throw new Error('请选择一个文件或输入一个URL');
        }
        
        this.prdContent = prdData;
        
        // 通知父组件PRD已生成
        this.$emit('prd-generated', {
          content: prdData,
          title: this.prdTitle
        });
      } catch (error) {
        console.error('PRD生成失败:', error);
        if (error.response && error.response.status) {
          alert('PRD生成失败: HTTP错误 ' + error.response.status);
        } else if (error.message) {
          alert('PRD生成失败: ' + error.message);
        } else {
          alert('PRD生成失败: ' + JSON.stringify(error));
        }
      } finally {
        this.loading = false;
      }
    },

    async generateMockPRD() {
      this.loading = true;

      try {
        // 模拟API调用延迟
        await new Promise(resolve => setTimeout(resolve, 2000));

        // 生成模拟的PRD内容
        const mockPRD = this.generateMockPRDContent();
        this.prdContent = mockPRD;

        // 设置标题
        if (this.referenceData) {
          this.prdTitle = `PRD: ${this.referenceData.title}`;
        } else if (this.referenceUrlInput) {
          this.prdTitle = `PRD: ${new URL(this.referenceUrlInput).hostname}`;
        } else if (this.uploadedFileInput) {
          this.prdTitle = `PRD: ${this.uploadedFileInput.name}`;
        } else {
          this.prdTitle = 'PRD: 模拟产品文档';
        }

        // 通知父组件PRD已生成
        this.$emit('prd-generated', {
          content: mockPRD,
          title: this.prdTitle
        });

        console.log('模拟PRD生成成功');
      } catch (error) {
        console.error('模拟PRD生成失败:', error);
        alert('模拟PRD生成失败: ' + error.message);
      } finally {
        this.loading = false;
      }
    },

    generateMockPRDContent() {
      // 生成统一的模拟PRD内容
      let mockContent = `# 产品需求文档 (PRD)

## 1. 产品概述

### 1.1 产品背景
这是一个现代化的Web应用程序，旨在为用户提供高效、直观的学习体验。通过人工智能技术，我们可以自动分析网页内容，生成结构化的学习路径和详细的知识点内容。

### 1.2 产品目标
- 为用户提供个性化的学习体验
- 通过AI技术简化知识获取过程
- 支持多种输入方式（URL、文件上传）
- 生成完整的学习路径和详细内容

### 1.3 目标用户
- 学生和学习者
- 教育工作者
- 专业人士需要快速掌握新知识的用户

## 2. 功能需求

### 2.1 核心功能
#### 2.1.1 内容上传与分析
- 支持URL输入和文件上传
- 自动分析网页内容结构
- 提取关键信息和知识点

#### 2.1.2 学习路径生成
- 基于内容自动生成知识图谱
- 创建逻辑清晰的学习路径
- 支持章节和知识点的层级结构

#### 2.1.3 内容生成
- 自动生成各知识点的详细内容
- 支持分层学习（Level 1-3）
- 提供编辑和修改功能

### 2.2 非功能需求
- 响应式设计，支持多种设备
- 直观的用户界面
- 快速的内容处理能力

## 3. 用户界面设计

### 3.1 整体布局
- 步骤导航界面
- 卡片式布局
- 进度指示器

### 3.2 主要页面
#### 3.2.1 上传页面
- URL输入框
- 文件上传区域
- 格式验证

#### 3.2.2 学习路径页面
- 可视化知识图谱
- 节点交互功能
- 编辑和保存功能

#### 3.2.3 内容生成页面
- 进度显示
- 内容预览
- 编辑功能

## 4. 技术实现

### 4.1 前端技术栈
- Vue.js 3
- Element Plus UI框架
- Markdown编辑器
- 图表可视化

### 4.2 后端技术栈
- Python FastAPI
- AI模型集成
- 文档处理库

## 5. 验收标准

### 5.1 功能验收
- [ ] URL输入功能正常
- [ ] 文件上传功能正常
- [ ] 学习路径生成准确
- [ ] 内容生成质量良好
- [ ] 编辑保存功能正常

### 5.2 性能验收
- [ ] 页面加载时间 < 3秒
- [ ] 内容生成时间 < 30秒
- [ ] 支持并发用户访问

## 6. 风险评估

### 6.1 技术风险
- AI模型准确性
- 内容解析复杂度
- 浏览器兼容性

### 6.2 业务风险
- 内容版权问题
- 用户隐私保护
- 服务稳定性

## 7. 项目计划

### 7.1 里程碑
1. 需求分析完成
2. UI设计完成
3. 前端开发完成
4. 后端开发完成
5. 测试完成
6. 上线部署

### 7.2 时间安排
- 总开发周期：8周
- 前端开发：4周
- 后端开发：4周
- 测试：2周

## 8. 附录

### 8.1 名词解释
- PRD：Product Requirements Document，产品需求文档
- AI：Artificial Intelligence，人工智能
- API：Application Programming Interface，应用程序接口

### 8.2 参考资料
- Vue.js官方文档
- FastAPI官方文档
- Element Plus组件库文档`;

      return mockContent;
    },
    
    async savePRD() {
      if (!this.prdTitle || !this.prdContent) {
        alert('请填写PRD标题和内容');
        return;
      }
      
      try {
        const requestData = {
          title: this.prdTitle,
          content: this.prdContent
        };
        
        const response = await prdAPI.savePRD(requestData);
        this.savedPRDId = response.id;
        alert('PRD保存成功！');
        this.$emit('prd-saved');
      } catch (error) {
        console.error('PRD保存失败:', error);
        alert('PRD保存失败: ' + (error.message || '未知错误'));
      }
    },
    
    async downloadPRD() {
      if (this.savedPRDId) {
        try {
          await prdAPI.downloadPRD(this.savedPRDId);
        } catch (error) {
          console.error('PRD下载失败:', error);
          alert('PRD下载失败: ' + (error.message || '未知错误'));
        }
      }
    },
    
    resetPRD() {
      this.referenceUrlInput = '';
      this.uploadedFileInput = null;
      this.prdContent = '';
      this.prdTitle = '';
      this.savedPRDId = null;
      const fileInput = document.getElementById('uploadedFile');
      if (fileInput) {
        fileInput.value = ''; // 清空文件输入
      }
    }
  }
};
</script>

<style scoped>
/* 组件特定样式 */
textarea {
  font-family: monospace;
  font-size: 14px;
}

.ml-2 {
  margin-left: 0.5rem;
}
</style>