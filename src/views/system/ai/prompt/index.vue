<template>
  <el-card shadow="never">
    <template #header>
      <span>AI 场景配置（Prompt Engineering）</span>
    </template>

    <el-tabs v-model="activeScene">
      <el-tab-pane label="学习引导" name="learning" />
      <el-tab-pane label="编程评测" name="coding" />
      <el-tab-pane label="情绪安抚" name="emotion" />
    </el-tabs>

    <el-form label-width="140px" style="margin-top: 20px">
      <el-form-item label="System Prompt">
        <el-input
          v-model="sceneConfig[activeScene]"
          type="textarea"
          :rows="12"
          placeholder="请输入系统提示词"
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="save">保存场景配置</el-button>
        <el-button @click="reset">恢复默认</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const activeScene = ref('learning')

const defaultPrompts = {
  learning: `你是一名循序渐进的 AI 学习导师。
你不会直接给出答案，而是通过提问、提示和引导帮助学生思考。
你的目标是培养学生的独立思考能力和问题拆解能力。`,

  coding: `你是一名严谨的编程助教。
你会从代码逻辑、规范性和复杂度三个方面分析学生代码。
除非明确要求，否则不要直接给出完整答案，而是指出问题方向。`,

  emotion: `你是一名具备同理心的学习助手。
当学生表现出焦虑、困惑或挫败情绪时，
你应优先进行情绪安抚，并给予正向鼓励。`
}

const sceneConfig = reactive({ ...defaultPrompts })

const save = () => {
  console.log('保存 Scene Prompt:', activeScene.value, sceneConfig[activeScene.value])
  ElMessage.success('场景提示词已保存（演示）')
}

const reset = () => {
  sceneConfig[activeScene.value] = defaultPrompts[activeScene.value]
  ElMessage.info('已恢复默认提示词')
}
</script>
