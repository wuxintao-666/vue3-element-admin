<template>
  <div class="markdown-editor">
    <!-- 工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <button
          :class="{ active: mode === 'edit' }"
          @click="mode = 'edit'"
          class="btn btn-sm"
        >
          ✏️ 编辑
        </button>
        <button
          :class="{ active: mode === 'preview' }"
          @click="mode = 'preview'"
          class="btn btn-sm ml-1"
        >
          👁️ 预览
        </button>
        <button
          :class="{ active: mode === 'split' }"
          @click="mode = 'split'"
          class="btn btn-sm ml-1"
        >
          ⫘ 分栏
        </button>
      </div>
      <div class="toolbar-right">
        <span class="word-count">字符: {{ value.length }}</span>
      </div>
    </div>

    <!-- 编辑器内容 -->
    <div class="editor-content">
      <!-- 编辑模式 -->
      <div v-if="mode === 'edit'" class="edit-mode">
        <textarea
          ref="textarea"
          v-model="value"
          class="markdown-textarea"
          :placeholder="placeholder"
          @input="handleInput"
          @keydown="handleKeydown"
          autocomplete="off"
          autocorrect="off"
          autocapitalize="off"
          spellcheck="false"
          data-gramm="false"
          data-gramm_editor="false"
          data-enable-grammarly="false"
        ></textarea>
      </div>

      <!-- 预览模式 -->
      <div v-else-if="mode === 'preview'" class="preview-mode">
        <div class="markdown-preview" v-html="renderedMarkdown"></div>
      </div>

      <!-- 分栏模式 -->
      <div v-else-if="mode === 'split'" class="split-mode">
        <div class="split-left">
          <textarea
            ref="textarea"
            v-model="value"
            class="markdown-textarea split-textarea"
            :placeholder="placeholder"
            @input="handleInput"
          ></textarea>
        </div>
        <div class="split-divider"></div>
        <div class="split-right">
          <div class="markdown-preview split-preview" v-html="renderedMarkdown"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
// @ts-ignore
import MarkdownIt from 'markdown-it'

// Props
interface Props {
  modelValue: string
  placeholder?: string
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请输入Markdown内容...',
  height: '400px'
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

// 响应式数据
const value = ref(props.modelValue)
const mode = ref<'edit' | 'preview' | 'split'>('split') // 默认分栏模式
const textarea = ref<HTMLTextAreaElement>()

// Markdown 渲染器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

// 渲染后的HTML
const renderedMarkdown = computed(() => {
  return md.render(value.value || '')
})

// 监听外部值变化
watch(() => props.modelValue, (newValue) => {
  value.value = newValue
})

// 监听内部值变化，发出事件
watch(value, (newValue) => {
  emit('update:modelValue', newValue)
})

// 处理输入事件
const handleInput = (event: Event) => {
  // 检查是否包含连续的反引号，如果有则进行特殊处理
  const target = event.target as HTMLTextAreaElement
  const currentValue = target.value

  // 如果检测到可能的问题模式，可以在这里进行处理
  // 比如移除某些自动插入的内容

  value.value = currentValue
  emit('update:modelValue', currentValue)
}

// 处理键盘事件，防止自动折叠等行为
const handleKeydown = (event: KeyboardEvent) => {
  // 防止某些编辑器的自动折叠行为
  // 特别是处理连续的反引号输入

  // 如果需要，可以在这里添加更具体的逻辑
  // 比如检测特定的按键组合并阻止默认行为
}

// 自动调整高度
const adjustHeight = () => {
  if (textarea.value) {
    textarea.value.style.height = 'auto'
    textarea.value.style.height = textarea.value.scrollHeight + 'px'
  }
}

// 禁用自动行为
const disableAutoBehaviors = () => {
  if (textarea.value) {
    // 设置额外的属性来禁用自动行为
    textarea.value.setAttribute('data-no-auto-format', 'true')
    textarea.value.setAttribute('data-no-syntax-highlight', 'true')

    // 尝试禁用任何可能的扩展或插件行为
    ;(textarea.value.style as any).webkitUserSelect = 'text'
    ;(textarea.value.style as any).MozUserSelect = 'text'
    ;(textarea.value.style as any).msUserSelect = 'text'
    textarea.value.style.userSelect = 'text'
  }
}

// 监听内容变化，自动调整高度
watch(value, () => {
  nextTick(() => {
    adjustHeight()
  })
})

onMounted(() => {
  nextTick(() => {
    adjustHeight()
    disableAutoBehaviors()
  })
})
</script>

<style scoped>
.markdown-editor {
  border: 1px solid #ddd;
  border-radius: 6px;
  overflow: hidden;
  background: #fff;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.toolbar-left {
  display: flex;
  gap: 4px;
}

.toolbar-right {
  color: #6c757d;
  font-size: 12px;
}

.btn {
  padding: 4px 8px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.btn:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.btn-sm {
  padding: 2px 6px;
  font-size: 11px;
}

.ml-1 {
  margin-left: 4px;
}

.word-count {
  font-size: 11px;
  color: #6c757d;
}

.editor-content {
  height: v-bind(height);
  overflow: hidden;
}

.edit-mode,
.preview-mode {
  height: 100%;
}

.markdown-textarea {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  padding: 12px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  background: transparent;

  /* 禁用所有可能的自动行为 */
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;

  /* 禁用文本转换 */
  text-transform: none;

  /* 确保不触发任何语法高亮或折叠 */
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.markdown-preview {
  height: 100%;
  padding: 12px;
  overflow-y: auto;
  background: #fff;
}

.markdown-preview :deep(h1),
.markdown-preview :deep(h2),
.markdown-preview :deep(h3),
.markdown-preview :deep(h4),
.markdown-preview :deep(h5),
.markdown-preview :deep(h6) {
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: 600;
}

.markdown-preview :deep(p) {
  margin-bottom: 12px;
  line-height: 1.6;
}

.markdown-preview :deep(pre) {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 12px;
  margin: 12px 0;
  overflow-x: auto;
}

.markdown-preview :deep(code) {
  background: #f1f3f4;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-preview :deep(pre code) {
  background: transparent;
  padding: 0;
}

.markdown-preview :deep(blockquote) {
  border-left: 4px solid #ddd;
  margin: 12px 0;
  padding-left: 16px;
  color: #666;
}

.markdown-preview :deep(ul),
.markdown-preview :deep(ol) {
  margin-bottom: 12px;
  padding-left: 24px;
}

.markdown-preview :deep(li) {
  margin-bottom: 4px;
}

/* 分栏模式 */
.split-mode {
  display: flex;
  height: 100%;
  overflow: hidden; /* 防止整体溢出 */
}

.split-left,
.split-right {
  flex: 1;
  height: 100%;
  min-width: 0; /* 允许flex项目缩小到0 */
  overflow: hidden; /* 防止内容溢出容器 */
}

.split-divider {
  width: 1px;
  background: #e9ecef;
  margin: 0 4px;
  flex-shrink: 0; /* 不允许分割线缩小 */
}

.split-textarea {
  height: 100% !important;
  border-right: 1px solid #e9ecef;
  box-sizing: border-box;
}

.split-preview {
  height: 100% !important;
  border-left: 1px solid #e9ecef;
  box-sizing: border-box;
  overflow-y: auto; /* 允许垂直滚动 */
  overflow-x: hidden; /* 隐藏水平滚动 */
}

/* 确保分栏模式下的markdown内容不会溢出 */
.split-mode .markdown-preview {
  max-width: 100%;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.split-mode .markdown-preview :deep(pre) {
  max-width: 100%;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  box-sizing: border-box;
}

.split-mode .markdown-preview :deep(code) {
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
}

/* 确保表格在分栏模式下也能正确显示 */
.split-mode .markdown-preview :deep(table) {
  max-width: 100%;
  overflow-x: auto;
  display: block;
  white-space: nowrap;
}

/* 响应式设计 - 小屏幕设备 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }

  .toolbar-left {
    flex: 1;
    min-width: 200px;
  }

  .toolbar-right {
    flex: 1;
    text-align: right;
  }

  /* 小屏幕下默认使用编辑模式而不是分栏模式 */
  .split-mode {
    flex-direction: column;
  }

  .split-left,
  .split-right {
    flex: none;
    height: 50%;
    min-height: 200px;
  }

  .split-divider {
    width: 100%;
    height: 1px;
    margin: 4px 0;
  }
}
</style>