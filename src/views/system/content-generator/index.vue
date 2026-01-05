<template>
  <section class="app-interface" id="use">
    <div class="vue-app-container">
      <div class="dashboard card">
        <h1 class="dashboard-title">SCOT-Web 控制面板</h1>

        <!-- 步骤条 -->
        <div class="steps-container">
          <div
            v-for="(step, index) in steps"
            :key="index"
            :class="['step', { active: index === currentStep }]"
          >
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-title">{{ step }}</div>
            <div v-if="index < steps.length - 1" class="step-line"></div>
          </div>
        </div>

        <!-- 面板区域 -->
        <div class="panels-container">
          <div class="card panel-card">
            <h2 class="card-title">网页预览</h2>

            <div class="preview-section">
              <div v-if="!previewLoaded" class="alert alert-warning">
                请先生成网页以进行预览
              </div>

              <div class="form-group">
                <label for="taskIdInput">任务ID:</label>
                <input
                  type="text"
                  id="taskIdInput"
                  class="form-control"
                  placeholder="请输入任务ID"
                  v-model="taskId"
                />
              </div>

              <button
                class="btn btn-primary load-btn"
                :disabled="!taskId"
                @click="loadPreview"
              >
                加载预览
              </button>

              <div v-if="previewLoaded" class="preview-content">
                <iframe
                  v-if="previewUrl"
                  :src="previewUrl"
                  class="preview-iframe"
                ></iframe>
              </div>
            </div>
          </div>
        </div>

        <!-- 导航 -->
        <div class="navigation">
          <button
            class="btn btn-secondary nav-btn"
            :disabled="currentStep === 0"
            @click="prevStep"
          >
            上一步
          </button>
          <button
            v-if="currentStep < steps.length - 1"
            class="btn btn-primary nav-btn"
            @click="nextStep"
          >
            下一步
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// 步骤条
const steps = [
  '上传参考网页',
  '生成设计文档',
  '生成学习路径',
  '生成网页',
  '预览结果'
]

// 当前步骤索引
const currentStep = ref(0)

// 任务ID
const taskId = ref('')

// 预览状态
const previewLoaded = ref(false)
const previewUrl = ref('')

// 加载预览
const loadPreview = () => {
  if (!taskId.value) return
  previewLoaded.value = true
  previewUrl.value = `/preview/${taskId.value}`
}

// 步骤导航
const prevStep = () => {
  if (currentStep.value > 0) currentStep.value--
}

const nextStep = () => {
  if (currentStep.value < steps.length - 1) currentStep.value++
}
</script>

<style scoped>
/* 容器 */
.vue-app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 标题 */
.dashboard-title {
  text-align: center;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
}

/* 步骤条 */
.steps-container {
  display: flex;
  justify-content: space-between;
  position: relative;
  margin-bottom: 40px;
}
.step {
  flex: 1;
  text-align: center;
  position: relative;
}
.step-number {
  width: 36px;
  height: 36px;
  line-height: 36px;
  margin: 0 auto 8px;
  border-radius: 50%;
  background-color: #e0e0e0;
  color: #fff;
  font-weight: bold;
  font-size: 16px;
}
.step.active .step-number {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}
.step-title {
  font-size: 14px;
  color: #606266;
}
.step.active .step-title {
  color: #409eff;
  font-weight: 600;
}
.step-line {
  position: absolute;
  top: 18px;
  right: -50%;
  width: 100%;
  height: 2px;
  background-color: #e0e0e0;
  z-index: -1;
}
.step:last-child .step-line {
  display: none;
}

/* 面板卡片 */
.panel-card {
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}
.card-title {
  font-size: 20px;
  margin-bottom: 20px;
  font-weight: 600;
  color: #2c3e50;
}

/* 预览区域 */
.preview-section {
  display: flex;
  flex-direction: column;
}
.form-group {
  margin-bottom: 15px;
}
.form-control {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
  width: 100%;
}
.load-btn {
  align-self: flex-start;
  margin-bottom: 15px;
}
.preview-content {
  margin-top: 15px;
}
.preview-iframe {
  width: 100%;
  height: 600px;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
}

/* 导航按钮 */
.navigation {
  margin-top: 30px;
  display: flex;
  justify-content: flex-end;
}
.nav-btn {
  padding: 8px 18px;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
}
.nav-btn:hover:not(:disabled) {
  opacity: 0.9;
}
.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 调整间距 */
.navigation .nav-btn + .nav-btn {
  margin-left: 12px;
}

/* 响应式微调 */
@media (max-width: 768px) {
  .steps-container {
    flex-direction: column;
    align-items: flex-start;
  }
  .step {
    margin-bottom: 20px;
  }
  .step-line {
    display: none;
  }
}
</style>
