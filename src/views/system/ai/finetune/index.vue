<template>
  <el-card shadow="never">
    <template #header>
      <span>AI 模型基础配置</span>
    </template>

    <el-form label-width="160px">
      <el-form-item label="模型名称">
        <el-select v-model="form.model" style="width: 300px">
          <el-option label="GPT-4o" value="gpt-4o" />
          <el-option label="Qwen-30B" value="qwen-30b" />
          <el-option label="DeepSeek-R1" value="deepseek-coder" />
        </el-select>
      </el-form-item>

      <el-form-item label="Temperature">
        <el-slider v-model="form.temperature" :min="0" :max="1" :step="0.1" show-input />
      </el-form-item>

      <el-form-item label="Top P">
        <el-slider v-model="form.top_p" :min="0" :max="1" :step="0.05" show-input />
      </el-form-item>

      <el-form-item label="Max Tokens">
        <el-input-number v-model="form.max_tokens" :min="128" :max="4096" />
      </el-form-item>

      <el-form-item label="Presence Penalty">
        <el-slider v-model="form.presence_penalty" :min="-2" :max="2" :step="0.1" show-input />
      </el-form-item>

      <el-form-item label="Frequency Penalty">
        <el-slider v-model="form.frequency_penalty" :min="-2" :max="2" :step="0.1" show-input />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="save">保存配置</el-button>
        <el-button @click="reset">恢复默认</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const defaultConfig = {
  model: 'gpt-4o',
  temperature: 0.7,
  top_p: 0.9,
  max_tokens: 1024,
  presence_penalty: 0,
  frequency_penalty: 0
}

const form = reactive({ ...defaultConfig })

const save = () => {
  console.log('保存 AI Base Config:', form)
  ElMessage.success('AI 模型参数已保存（演示）')
}

const reset = () => {
  Object.assign(form, defaultConfig)
  ElMessage.info('已恢复默认配置')
}
</script>
