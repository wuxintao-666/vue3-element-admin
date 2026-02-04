<template>
  <div class="dashboard card">
    <!-- <h1 class="text-center mb-4">SCOT-Web 控制面板</h1> -->
    
    <div class="steps-container">
      <div class="step" :class="{ 'active': currentStep === 1 }" @click="goToStep(1)">
        <div class="step-number">1</div>
        <div class="step-title">上传参考网页</div>
      </div>
      
      <div class="step" :class="{ 'active': currentStep === 2 }" @click="goToStep(2)">
        <div class="step-number">2</div>
        <div class="step-title">生成设计文档</div>
      </div>
      
      <div class="step" :class="{ 'active': currentStep === 3 }" @click="goToStep(3)">
        <div class="step-number">3</div>
        <div class="step-title">生成学习路径</div>
      </div>
      
      <div class="step" :class="{ 'active': currentStep === 4 }" @click="goToStep(4)">
        <div class="step-number">4</div>
        <div class="step-title">生成知识点内容</div>
      </div>
      
      <div class="step" :class="{ 'active': currentStep === 5 }" @click="goToStep(5)">
        <div class="step-number">5</div>
        <div class="step-title">生成实践案例</div>
      </div>
      
      <div class="step" :class="{ 'active': currentStep === 6 }" @click="goToStep(6)">
        <div class="step-number">6</div>
        <div class="step-title">生成网页</div>
      </div>

      <div class="step" :class="{ 'active': currentStep === 7 }" @click="goToStep(7)">
        <div class="step-number">7</div>
        <div class="step-title">预览结果</div>
      </div>
    </div>
    
    <div class="panels-container mt-4">
      <UploadPanel 
        v-if="currentStep === 1" 
        :initial-data="uploadData"
        @upload-complete="onUploadComplete"
        @proceed-to-prd="proceedToPRD"
        @proceed-to-knowledge="proceedToKnowledge"
        @upload-cleared="onUploadCleared"
      />
      
      <PRDPanel 
        v-if="currentStep === 2" 
        ref="prdPanel"
        :reference-data="referenceData"
        :upload-type="uploadType"
        :prd-data="prdData"
        @prd-saved="onPRDSaved"
        @prd-generated="onPRDGenerated"
      />
      
      <KnowledgeGraph
        v-if="currentStep === 3"
        ref="knowledgeGraph"
        :reference-data="referenceData"
        :upload-type="uploadType"
        :knowledge-data="knowledgeData"
        @knowledge-saved="onKnowledgeSaved"
        @knowledge-extracted="onKnowledgeExtracted"
        @knowledge-updated="onKnowledgeUpdated"
        @learn-knowledge="onLearnKnowledge"
      />
      
      <KnowledgeGenerationList
        v-else-if="currentStep === 4"
        :knowledge-data="knowledgeData"
        :generated-contents="generatedContents"
        :generation-progress="generationProgress"
        @generation-completed="onGenerationCompleted"
        @generated-contents-updated="onGeneratedContentsUpdated"
        @generation-progress-updated="onGenerationProgressUpdated"
        @go-to-step="goToStep"
      />
      
      <TestTaskDisplay
        v-if="currentStep === 5"
        :knowledge-graph="knowledgeData"
        :generated-contents="generatedContents"
        :show-prerequisites-warning="!knowledgeData || !generatedContents || Object.keys(generatedContents).length === 0"
        @generation-completed="onTestTasksSaved"
      />

      <!-- <TestTaskDisplay
        v-else-if="currentStep === 5"
        :knowledge-graph="knowledgeData"
        :generated-contents="generatedContents"
      /> -->
      
      <!-- <KnowledgeGenerationList
        v-else-if="currentStep === 4"
        :knowledge-data="knowledgeData"
        @generation-completed="onGenerationCompleted"
        @go-to-step="goToStep"
      /> -->

      <GeneratePanel
        v-else-if="currentStep === 6"
        ref="generatePanel"
        :prd-data="prdData"
        :knowledge-data="knowledgeData"
        :user-state="userState"
        @website-generated="onWebsiteGenerated"
      />

      <PreviewPane
        ref="previewPane"
        v-if="currentStep === 7"
        :initial-task-id="generatedTaskId"
        :generated-files="generatedFiles"
        :auto-refresh="currentStep === 7"
      />
    </div>
    
    <div class="navigation mt-4" v-if="currentStep > 1 && currentStep !== 3.7">
      <button @click="prevStep" class="btn btn-secondary">上一步</button>
      <button
        v-if="currentStep < 7"
        @click="nextStep"
        class="btn btn-primary ml-2"
        :disabled="!canProceed"
      >
        下一步
      </button>
    </div>

    <div class="navigation mt-4" v-else-if="currentStep === 3.7">
      <button @click="backToLearningContent" class="btn btn-secondary">返回学习内容</button>
    </div>
    
    <div class="navigation mt-4" v-else-if="currentStep === 3.7">
      <button @click="backToLearningContent" class="btn btn-secondary">返回学习内容</button>
    </div>
  </div>
</template>

<script>
import UploadPanel from './UploadPanel.vue';
import PRDPanel from './PRDPanel.vue';
import KnowledgeGraph from './KnowledgeGraph.vue';
import KnowledgeGenerationList from './KnowledgeGenerationList.vue';
import TestTaskDisplay from './TestTaskDisplay.vue';
import GeneratePanel from './GeneratePanel.vue';
import PreviewPane from './PreviewPane.vue';
import { testGenerationAPI } from './api/index.js';
import './css/style.css';
export default {
  name: 'Dashboard',
  components: {
    UploadPanel,
    PRDPanel,
    KnowledgeGraph,
    KnowledgeGenerationList,
    TestTaskDisplay,
    GeneratePanel,
    PreviewPane
  },
  data() {
    return {
      currentStep: 1,
      uploadData: null,       // 上传的数据
      referenceData: null,    // 参考数据（用于PRD和知识点提取）
      prdData: null,          // PRD数据
      knowledgeData: null,    // 知识点数据
      generatedTaskId: '',    // 生成任务ID
      canProceed: false,
      showLearningStep: false, // 是否显示学习步骤
      showTestTaskStep: false, // 是否显示测试题步骤
      learningNode: null,     // 当前学习的知识点节点
      testTask: null,         // 当前测试题
      testTaskLoading: false, // 测试题加载状态
      prdSaved: false,        // PRD是否已保存
      knowledgeSaved: false,   // 知识图谱是否已保存
      knowledgeContentSaved: false, // 知识点内容是否已保存
      testTaskSaved: false,    // 测试题是否已保存到数据库
      websiteGenerated: false, // 网页是否已生成
      generatedContents: {},     // 生成的知识点内容
      generationProgress: {      // 生成进度
        total: 0,
        completed: 0,
        failed: 0
      },
      generatedFiles: null,       // 生成的网页文件
      userState: {               // 用户状态
        taskId: '',
        files: null,
        userNote: ''
      }
    };
  },
  methods: {
    goToStep(step) {
      console.log('Dashboard: goToStep called', {
        requestedStep: step,
        currentStep: this.currentStep,
        generatedTaskId: this.generatedTaskId,
        currentTime: new Date().toISOString()
      });

      // 允许用户点击步骤标题导航到对应步骤
      if (step >= 1 && step <= 7) {
        console.log('Dashboard: Step validation passed, updating currentStep');
        this.currentStep = step;
        // 根据步骤检查相应数据来设置canProceed
        this.updateCanProceed();

        console.log('Dashboard: Step change completed', {
          newCurrentStep: this.currentStep,
          canProceed: this.canProceed,
          isStep7: step === 7,
          autoRefreshProp: step === 7
        });
      } else {
        console.log('Dashboard: Step validation failed, step out of range', step);
      }
    },

    updateCanProceed() {
      // 根据当前步骤检查相应数据和保存状态
      switch (this.currentStep) {
        case 1:
          // 步骤1：有上传数据就可以前进
          this.canProceed = !!this.uploadData;
          break;
        case 2:
          // 步骤2：PRD已保存才能前进
          this.canProceed = this.prdSaved;
          break;
        case 3:
          // 步骤3：知识图谱已保存才能前进
          this.canProceed = this.knowledgeSaved;
          break;
        case 4:
          // 步骤4：知识点内容生成完成后可以前进
          this.canProceed = this.knowledgeContentSaved;
          break;
        case 5:
          // 步骤5：测试题保存到数据库后才能前进
          this.canProceed = this.testTaskSaved;
          break;
        case 6:
          // 步骤6：网页生成完成后才能前进
          this.canProceed = this.websiteGenerated;
          break;
        default:
          // 其他步骤暂时保持false，需要手动设置
          this.canProceed = false;
      }
    },
    
    onUploadComplete(data) {
      this.uploadData = data.data;
      this.referenceData = data.data;
      this.uploadType = data.type;
      this.updateCanProceed();
      console.log('上传完成，可以进行下一步');
    },
    
    proceedToPRD(data) {
      this.uploadData = data.data;
      this.referenceData = data.data;
      this.currentStep = 2;
      console.log('进入PRD生成步骤');
    },

    proceedToKnowledge(data) {
      this.uploadData = data.data;
      this.referenceData = data.data;
      this.currentStep = 3;
    
      console.log('进入知识点提取步骤');
    },
    
    onPRDGenerated(data) {
      this.prdData = data;
      // 生成PRD后不自动允许前进，需要保存后才能前进
      console.log('PRD已生成，需保存后才能进行下一步');
    },
    
    onPRDSaved() {
      this.prdSaved = true;
      this.updateCanProceed();
      console.log('PRD已保存，可以进行下一步');
    },
    
    onKnowledgeExtracted(data) {
      this.knowledgeData = data;
      // 提取知识点后不自动允许前进，需要保存后才能前进
      console.log('知识点已提取，需保存后才能进行下一步');
    },

    onKnowledgeSaved() {
      // 知识点图谱保存成功后，设置保存状态并跳转到生成知识点内容步骤
      this.knowledgeSaved = true;
      this.updateCanProceed();
      console.log('知识点图谱已保存，跳转到生成知识点内容步骤');
    },

    onKnowledgeUpdated(data) {
      // 更新knowledgeData，保持与子组件数据同步
      this.knowledgeData = {
        graph: data.graph,
        name: data.name
      };
      // 更新数据后不自动允许前进，需要保存后才能前进
      console.log('index.vue的knowledgeData已更新');
    },
    
    onLearnKnowledge(nodeData) {
      this.learningNode = nodeData;
      this.showLearningStep = true;
      this.currentStep = 3.5; // 跳转到学习知识点模块
      console.log('进入学习知识点模块');
    },
    
    onViewTestTask(data) {
      // 生成测试题并跳转到测试题显示模块
      this.showTestTaskStep = true;
      this.currentStep = 3.7;
      this.testTask = null;
      this.testTaskLoading = true;
      
      // 调用后端API生成测试题
      this.generateTestTask(data);
    },
    
    async generateTestTask(data) {
      try {
        const requestData = {
          topic_id: data.knowledgeNode.id,
          knowledge_node: data.knowledgeNode,
          learning_content: data.learningContent
        };
        
        const response = await testGenerationAPI.generateTestTask(requestData);
        this.testTask = response;
      } catch (error) {
        console.error('生成测试题失败:', error);
        alert('生成测试题失败: ' + (error.message || '未知错误'));
      } finally {
        this.testTaskLoading = false;
      }
    },
    
    backToKnowledgeGraph() {
      this.currentStep = 3;
      this.learningNode = null;
      this.showLearningStep = false;
      console.log('返回知识点图谱');
    },
    
    backToLearningContent() {
      this.currentStep = 3.5;
      this.testTask = null;
      this.showTestTaskStep = false;
      console.log('返回学习内容');
    },
    
    onGenerationCompleted(data) {
      // 知识点内容生成完成，可以进行下一步（生成网页）
      this.knowledgeContentSaved = true;
      this.updateCanProceed();
      console.log('知识点内容生成完成，可以进行下一步');
    },

    onGeneratedContentsUpdated(contents) {
      // 更新生成的知识点内容
      this.generatedContents = { ...contents };
      console.log('generatedContents 已更新:', this.generatedContents);
    },

    onGenerationProgressUpdated(progress) {
      // 更新生成进度
      this.generationProgress = { ...progress };
      console.log('generationProgress 已更新:', this.generationProgress);
    },

    onWebsiteGenerated(data) {
      this.generatedTaskId = data.taskId;
      this.generatedFiles = data.files;
      this.websiteGenerated = true; // 网页生成完成
      this.updateCanProceed();
      console.log('网页生成完成，可以进行下一步');
      console.log('接收到的数据:', {
        taskId: data.taskId,
        files: data.files,
        userNote: data.userNote
      });
      console.log('当前 userState:', this.userState);
    },
    
    nextStep() {
      if (this.currentStep < 7) {
        this.currentStep++;
        this.updateCanProceed();
        console.log('进入步骤:', this.currentStep);
      }
    },

    prevStep() {
      if (this.currentStep > 1) {
        this.currentStep--;
        this.updateCanProceed();
        console.log('返回步骤:', this.currentStep);
      }
    },

    getKnowledgeGraph() {
      // 返回完整的知识图谱数据
      if (this.knowledgeData && this.knowledgeData.graph) {
        return this.knowledgeData.graph;
      }
      return { nodes: [], edges: [] };
    },

    onGeneratedTestTasksUpdated(testTasks) {
      // 处理测试题生成更新
      console.log('测试题生成状态已更新:', testTasks);
    },

    onTestTasksSaved(data) {
      // 测试题保存到数据库完成，可以进行下一步
      this.testTaskSaved = true;
      this.updateCanProceed();
      console.log('测试题已保存到数据库，可以进行下一步');
    }

  }
};
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-top: 20px;
}

.steps-container {
  display: flex;
  justify-content: space-between;
  position: relative;
  cursor: pointer;
}

.steps-container::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #e0e0e0;
  z-index: 1;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 2;
  flex: 1;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e0e0e0;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 5px;
}

.step-title {
  font-size: 14px;
  color: #666;
  text-align: center;
}

.step.active .step-number {
  background-color: #4a90e2;
  color: white;
}

.step.active .step-title {
  color: #4a90e2;
  font-weight: bold;
}

.panels-container {
  min-height: 400px;
}

.navigation {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.ml-2 {
  margin-left: 0.5rem;
}
</style>