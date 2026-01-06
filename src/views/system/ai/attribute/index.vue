<template>
  <div class="ai-base-config">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>AI 属性配置</span>
          <div class="actions">
            <el-button @click="loadConfig" :loading="loading">
              重新加载
            </el-button>
            <el-button
              type="primary"
              @click="saveConfig"
              :loading="saving"
            >
              保存配置
            </el-button>
          </div>
        </div>
      </template>

      <el-form
        :model="form"
        label-width="180px"
        label-position="left"
      >
        <!-- LLM 基础配置 -->
        <el-divider content-position="left">LLM 配置</el-divider>

        <el-form-item label="Tutor OpenAI API Key">
          <el-input
            v-model="form.tutor_openai_api_key"
            type="password"
            show-password
            placeholder="请输入 API Key"
          />
        </el-form-item>

        <el-form-item label="Tutor OpenAI 模型">
          <el-input
            v-model="form.tutor_openai_model"
            placeholder="如：gpt-4 / deepseek-ai/DeepSeek-V3"
          />
        </el-form-item>

        <el-form-item label="Tutor OpenAI API Base">
          <el-input
            v-model="form.tutor_openai_api_base"
            placeholder="https://api.openai.com/v1"
          />
        </el-form-item>

        <!-- Embedding 配置 -->
        <el-divider content-position="left">Embedding 配置</el-divider>

        <el-form-item label="Embedding API Key">
          <el-input
            v-model="form.tutor_embedding_api_key"
            type="password"
            show-password
            placeholder="请输入 Embedding API Key"
          />
        </el-form-item>

        <el-form-item label="Embedding API Base">
          <el-input
            v-model="form.tutor_embedding_api_base"
            placeholder="Embedding API Base URL"
          />
        </el-form-item>

        <el-form-item label="Embedding 模型">
          <el-input
            v-model="form.tutor_embedding_model"
            placeholder="如：Qwen/Qwen3-Embedding-4B"
          />
        </el-form-item>

        <!-- 翻译服务 -->
        <el-divider content-position="left">翻译服务配置</el-divider>

        <el-form-item label="Translation API Key">
          <el-input
            v-model="form.tutor_translation_api_key"
            type="password"
            show-password
            placeholder="请输入 Translation API Key"
          />
        </el-form-item>

        <el-form-item label="Translation API Base">
          <el-input
            v-model="form.tutor_translation_api_base"
            placeholder="Translation API Base URL"
          />
        </el-form-item>

        <el-form-item label="Translation 模型">
          <el-input
            v-model="form.tutor_translation_model"
            placeholder="如：Qwen/Qwen3-30B-A3B"
          />
        </el-form-item>

        <!-- 功能开关 -->
        <el-divider content-position="left">功能开关</el-divider>

        <el-form-item label="启用 RAG 服务">
          <el-switch v-model="form.enable_rag_service" />
        </el-form-item>

        <el-form-item label="启用情感分析">
          <el-switch v-model="form.enable_sentiment_analysis" />
        </el-form-item>

        <el-form-item label="启用聚类服务">
          <el-switch v-model="form.enable_clustering_service" />
        </el-form-item>

        <el-form-item label="启用翻译服务">
          <el-switch v-model="form.enable_translation_service" />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAIConfig, updateAIConfig } from './aiConfig'

const loading = ref(false)
const saving = ref(false)

const form = ref({
  tutor_openai_api_key: '',
  tutor_openai_model: '',
  tutor_openai_api_base: '',

  tutor_embedding_api_key: '',
  tutor_embedding_api_base: '',
  tutor_embedding_model: '',

  tutor_translation_api_key: '',
  tutor_translation_api_base: '',
  tutor_translation_model: '',

  enable_rag_service: false,
  enable_sentiment_analysis: false,
  enable_clustering_service: false,
  enable_translation_service: false
})

const loadConfig = async () => {
  loading.value = true
  try {
    const res = await getAIConfig()
    Object.assign(form.value, res.data)
    ElMessage.success('AI 配置加载成功')
  } catch (err: any) {
    ElMessage.error(err?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    await updateAIConfig(form.value)
    ElMessage.success('AI 配置保存成功')
  } catch (err: any) {
    ElMessage.error(err?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.ai-base-config {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  display: flex;
  gap: 8px;
}
</style>
