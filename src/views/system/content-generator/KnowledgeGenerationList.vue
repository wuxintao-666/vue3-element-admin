<template>
  <div class="card">
    <h2 class="card-title">生成知识点内容</h2>
    <div v-if="knowledgeData">
          <div class="alert alert-info">
            <p><strong>知识图谱信息:</strong></p>
            <p>图谱名称: {{ knowledgeData.name }}</p>
            <p>节点数量: {{ knowledgeData.graph.nodes.length }}</p>
          </div>

          <!-- 生成控制 -->
          <div class="generation-controls mb-4">
            <div class="control-buttons">
              <button
                @click="startGeneration"
                :disabled="isGenerating || isMockGenerating || allGenerated"
                class="btn btn-primary"
              >
                {{ isGenerating ? '生成中...' : allGenerated ? '已全部生成' : '开始生成' }}
              </button>

              <button
                @click="startMockGeneration"
                :disabled="isGenerating || isMockGenerating || allGenerated"
                class="btn btn-success ml-2"
              >
                {{ isMockGenerating ? '生成中...' : allGenerated ? '已全部生成' : '模拟生成' }}
              </button>

              <button
                @click="stopGeneration"
                :disabled="!isGenerating"
                class="btn btn-secondary ml-2"
              >
                停止生成
              </button>

              <button
                @click="resetGeneration"
                class="btn btn-warning ml-2"
              >
                重置
              </button>
            </div>

            <div class="progress-info" v-if="generationProgress.total > 0">
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: progressPercentage + '%' }"
                ></div>
              </div>
              <span class="progress-text">
                {{ generationProgress.completed }}/{{ generationProgress.total }} 已完成
              </span>
            </div>
          </div>

          <!-- 生成结果列表 -->
          <div class="generation-list">
            <div class="list-header">
              <span class="header-item">序号</span>
              <span class="header-item">知识点</span>
              <span class="header-item">类型</span>
              <span class="header-item">状态</span>
              <span class="header-item">操作</span>
            </div>

            <div
              v-for="(node, index) in knowledgeData.graph.nodes"
              :key="node.data.id"
              class="generation-item"
              :class="{ 'generating': (isGenerating || isMockGenerating) && !hasGeneratedContent(node.data.id) }"
            >
              <span class="item-seq">{{ index + 1 }}</span>
              <span class="item-title">{{ node.data.label }}</span>
              <span class="item-type">
                <span class="type-badge" :class="node.data.type">
                  {{ node.data.type === 'chapter' ? '章节' : '知识点' }}
                </span>
              </span>
              <span class="item-status">
                <span class="status-badge" :class="getGenerationStatus(node.data.id)">
                  {{ getGenerationStatusText(node.data.id) }}
                </span>
              </span>
              <span class="item-actions">
                <button
                  v-if="hasGeneratedContent(node.data.id)"
                  @click="editContent(node.data.id)"
                  class="btn btn-small btn-info"
                >
                  编辑
                </button>
                <button
                  v-if="hasGeneratedContent(node.data.id)"
                  @click="viewContent(node.data.id)"
                  class="btn btn-small btn-secondary ml-1"
                >
                  查看
                </button>
                <button
                  v-if="node.data.type === 'knowledge' && (hasGeneratedContent(node.data.id) || getGenerationStatus(node.data.id) === 'failed')"
                  @click="regenerateKnowledgePoint(node)"
                  :disabled="isRegeneratingNode === node.data.id"
                  class="btn btn-small btn-warning ml-1"
                >
                  {{ isRegeneratingNode === node.data.id ? '生成中...' : '重新生成' }}
                </button>
              </span>
            </div>
          </div>

          <!-- 保存到数据库 -->
          <div class="save-section mt-4" v-if="allGenerated">
            <div class="alert alert-success">
              <strong>恭喜！</strong> 所有知识点内容已生成完成。
            </div>

            <div class="save-controls">
              <button
                @click="saveAllToDatabase"
                :disabled="isSaving"
                class="btn btn-success"
              >
                {{ isSaving ? '保存中...' : '保存所有内容到数据库' }}
              </button>
            </div>
          </div>

          <!-- 内容详情弹窗 -->
          <div v-if="showContentModal" class="modal-overlay" @click="closeContentModal">
            <div class="modal-content" @click.stop>
              <div class="modal-header">
                <h3>{{ currentContentNode ? currentContentNode.label : '知识点内容' }}</h3>
                <button @click="closeContentModal" class="close-btn">&times;</button>
              </div>

              <div class="modal-body">
                <div v-if="currentContent" class="markdown-content">
                  <!-- 直接渲染markdown内容 -->
                  <div class="markdown-preview" v-html="renderMarkdown(currentContent)"></div>
                </div>
                <div v-else class="no-content">
                  <p>暂无内容</p>
                </div>
              </div>

              <div class="modal-footer">
                <button @click="editContent(currentContentNodeId)" class="btn btn-warning">编辑内容</button>
                <button @click="closeContentModal" class="btn btn-secondary ml-2">关闭</button>
              </div>
            </div>
          </div>

          <!-- 编辑内容弹窗 -->
          <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
            <div class="modal-content large-modal" @click.stop>
              <div class="modal-header">
                <h3>编辑知识点内容 - {{ currentContentNode ? currentContentNode.label : '' }}</h3>
                <button @click="closeEditModal" class="close-btn">&times;</button>
              </div>

              <div class="modal-body">
              

                <!-- 编辑Levels -->
                <div class="levels-editor">
                  <!-- <label>学习内容 (Levels):</label> -->
                  <div
                    v-for="(level, index) in editingContent.levels"
                    :key="index"
                    class="level-item"
                  >
                    <div class="level-header">
                      <span class="level-label">Level {{ level.level }}</span>
                      
                    </div>
                    <MarkdownEditor
                      v-model="level.description"
                      :placeholder="'请输入Level ' + level.level + ' 的描述...'"
                      height="200px"
                    />
                  </div>

                  
                </div>
              </div>

              <div class="modal-footer">
                <button @click="saveEditedContent" class="btn btn-success">保存修改</button>
                <button @click="closeEditModal" class="btn btn-secondary ml-2">取消</button>
              </div>
            </div>
          </div>
      </div>
      <div v-else>
    <div v-if="!knowledgeData">
        <div class="alert alert-warning">
          请先完成知识点图谱的生成与保存
        </div>
      </div>
  </div>
  </div>
  
</template>

<script>
import { learningAPI } from './api/index.js';
import MarkdownEditor from './MarkdownEditor.vue';
import MarkdownIt from 'markdown-it';

export default {
  name: 'KnowledgeGenerationList',
  components: {
    MarkdownEditor
  },
  props: {
    knowledgeData: {
      type: Object,
      required: true
    },
    generatedContents: {
      type: Object,
      default: () => ({})
    },
    generationProgress: {
      type: Object,
      default: () => ({
        total: 0,
        completed: 0,
        failed: 0
      })
    }
  },
  data() {
    return {
      // 生成状态
      isGenerating: false,
      isMockGenerating: false,
      isRegeneratingNode: null, // 当前正在重新生成的节点ID

      // 生成的内容存储（现在通过 prop 获取）

      // 弹窗状态
      showContentModal: false,
      showEditModal: false,
      currentContentNodeId: null,
      currentContent: null,
      editingContent: {
        title: '',
        levels: []
      },

      // 保存状态
      isSaving: false
    };
  },
  computed: {
    currentContentNode() {
      if (!this.currentContentNodeId) return null;
      return this.knowledgeData.graph.nodes.find(node => node.data.id === this.currentContentNodeId)?.data;
    },

    progressPercentage() {
      if (this.generationProgress.total === 0) return 0;
      return Math.round((this.generationProgress.completed / this.generationProgress.total) * 100);
    },

    allGenerated() {
      return this.generationProgress.total > 0 &&
             this.generationProgress.completed === this.generationProgress.total;
    },

    // 合并父组件传递的内容和本地内容
    currentGeneratedContents() {
      return this.generatedContents;
    }
  },
  methods: {
    async startGeneration() {
      if (this.isGenerating) return;

      this.isGenerating = true;
      this.isMockGenerating = false;
      // 只获取需要生成的知识点节点（排除章节节点）
      const knowledgeNodes = this.knowledgeData.graph.nodes.filter(node => node.data.type === 'knowledge');
      this.updateGenerationProgress({
        total: knowledgeNodes.length,
        completed: 0,
        failed: 0
      });

      // 并行生成所有知识点内容
      await this.generateAllNodes(knowledgeNodes);
    },

    async startMockGeneration() {
      if (this.isMockGenerating) return;

      this.isMockGenerating = true;
      this.isGenerating = false;
      // 只获取需要生成的知识点节点（排除章节节点）
      const knowledgeNodes = this.knowledgeData.graph.nodes.filter(node => node.data.type === 'knowledge');
      this.updateGenerationProgress({
        total: knowledgeNodes.length,
        completed: 0,
        failed: 0
      });

      // 使用模拟数据生成
      await this.generateAllNodesMock(knowledgeNodes);
    },

    async generateAllNodes(knowledgeNodes) {
      if (knowledgeNodes.length === 0) {
        this.isGenerating = false;
        console.log('没有需要生成的知识点节点');
        return;
      }

      console.log(`开始并行生成 ${knowledgeNodes.length} 个知识点内容`);

      // 为每个节点创建生成任务
      const generationPromises = knowledgeNodes.map(async (node, index) => {
        try {
          console.log(`开始生成知识点内容 (${index + 1}/${knowledgeNodes.length}): ${node.data.label}`);

          // 调用API生成内容 - 直接传递知识点数据
          const response = await learningAPI.generateKnowledgeContent(node.data);

          // 存储生成的内容 - 转换为可编辑的字符串格式
          if (response.levels && Array.isArray(response.levels)) {
            // 将分层学习内容转换为可编辑的文本格式
            let contentText = `# ${response.title || ''}\n\n`;
            response.levels.forEach((level) => {
              contentText += `## Level ${level.level}\n\n`;
              contentText += `${level.description || ''}\n\n`;
            });
            this.updateGeneratedContents(node.data.id, contentText.trim());
          } else {
            // 如果没有levels，存储为JSON字符串
            this.updateGeneratedContents(node.data.id, JSON.stringify(response, null, 2));
          }

          const updatedProgress = { ...this.generationProgress };
          updatedProgress.completed++;
          this.updateGenerationProgress(updatedProgress);
          console.log(`知识点内容生成成功 (${updatedProgress.completed}/${updatedProgress.total}): ${node.data.label}`);

        } catch (error) {
          console.error(`生成知识点内容失败: ${node.data.label}`, error);
          this.updateGeneratedContents(node.data.id, null); // 标记为失败
          const updatedProgress = { ...this.generationProgress };
          updatedProgress.failed++;
          this.updateGenerationProgress(updatedProgress);
        }
      });

      try {
        // 并发执行所有生成任务
        await Promise.all(generationPromises);
        console.log(`所有知识点内容生成完成 - 成功: ${this.generationProgress.completed}, 失败: ${this.generationProgress.failed}`);
      } catch (error) {
        console.error('批量生成过程中发生错误:', error);
      } finally {
        // 生成完成
        this.isGenerating = false;
      }
    },

    async generateAllNodesMock(knowledgeNodes) {
      if (knowledgeNodes.length === 0) {
        this.isGenerating = false;
        console.log('没有需要生成的知识点节点');
        return;
      }

      console.log(`开始模拟生成 ${knowledgeNodes.length} 个知识点内容`);

      // 为每个节点创建模拟生成任务
      const generationPromises = knowledgeNodes.map(async (node, index) => {
        try {
          console.log(`模拟生成知识点内容 (${index + 1}/${knowledgeNodes.length}): ${node.data.label}`);

          // 模拟API调用延迟
          await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 700));

          // 生成模拟的markdown内容
          const mockContent = this.generateHTMLBasicContent(node.data.label);

          // 存储模拟生成的内容
          this.updateGeneratedContents(node.data.id, mockContent);

          const updatedProgress = { ...this.generationProgress };
          updatedProgress.completed++;
          this.updateGenerationProgress(updatedProgress);
          console.log(`知识点内容模拟生成成功 (${updatedProgress.completed}/${updatedProgress.total}): ${node.data.label}`);

        } catch (error) {
          console.error(`模拟生成知识点内容失败: ${node.data.label}`, error);
          this.updateGeneratedContents(node.data.id, null); // 标记为失败
          const updatedProgress = { ...this.generationProgress };
          updatedProgress.failed++;
          this.updateGenerationProgress(updatedProgress);
        }
      });

      try {
        // 并发执行所有模拟生成任务
        await Promise.all(generationPromises);
        console.log(`模拟生成完成 - 成功: ${this.generationProgress.completed}, 失败: ${this.generationProgress.failed}`);
      } catch (error) {
        console.error('模拟生成过程中发生错误:', error);
      } finally {
        // 生成完成
        this.isMockGenerating = false;
      }
    },

    generateMockContent(nodeLabel) {
      // 生成包含4个难度等级的学习内容
      let mockContent = `# ${nodeLabel}\n\n`;

      // 根据知识点关键词判断内容类型并生成相应内容
      if (nodeLabel.includes('了解HTML基本结构')) {
        mockContent += this.generateHTMLBasicContent();
      } else if (nodeLabel.includes('使用标题元素')) {
        mockContent += this.generateHTMLElementsContent();
      } else if (nodeLabel.includes('创建段落元素')) {
        mockContent += this.generateParagraphContent();
      } else if (nodeLabel.includes('理解CSS基本语法')) {
        mockContent += this.generateCSSBasicContent();
      } else if (nodeLabel.includes('应用文本样式')) {
        mockContent += this.generateTextStylingContent();
      } else if (nodeLabel.includes('使用CSS盒模型')) {
        mockContent += this.generateBoxModelContent();
      } else {
        mockContent += this.generateGenericContent();
      }

      return mockContent.trim();
    },

    // HTML基础内容 - 4个等级
    generateHTMLBasicContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `HTML（HyperText Markup Language）是网页的骨架，所有网页都是由HTML元素组成的。\n\n`;
      content += `### 核心概念：\n`;
      content += `- HTML是标记语言，不是编程语言\n`;
      content += `- 使用标签来定义网页结构\n`;
      content += `- 浏览器解析HTML显示网页内容\n\n`;

      content += `## Level 2\n\n`;
      content += `HTML文档有标准的结构，每个部分都有特定的作用。\n\n`;
      content += `### 基本结构：\n`;
      content += `- \`<!DOCTYPE html>\`: 声明文档类型\n`;
      content += `- \`<html>\`: 根元素\n`;
      content += `- \`<head>\`: 文档头部，包含元信息\n`;
      content += `- \`<body>\`: 文档主体，显示在浏览器中\n\n`;

      content += `## Level 3\n\n`;
      content += `了解HTML文档的完整结构和最佳实践。\n\n`;
      content += `### 完整结构：\n`;
      content += `- 字符编码：\`<meta charset="UTF-8">\`\n`;
      content += `- 页面标题：\`<title>页面标题</title>\`\n`;
      content += `- 视口设置：响应式网页的基础\n`;
      content += `- 注释：\`<!-- 注释内容 -->\`\n\n`;

      content += `## Level 4\n\n`;
      content += `掌握HTML文档的优化技巧和高级用法。\n\n`;
      content += `### 高级特性：\n`;
      content += `- 语义化HTML：使用正确的标签提升SEO\n`;
      content += `- 无障碍访问：为残障用户提供更好的体验\n`;
      content += `- HTML5新特性：更丰富的媒体和交互元素\n`;
      content += `- 性能优化：减少不必要的标签和嵌套\n\n`;

      return content;
    },

    // HTML元素内容 - 4个等级
    generateHTMLElementsContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `标题元素用于定义文档的层次结构，从最重要的h1到最不重要的h6。\n\n`;
      content += `### 标题层级：\n`;
      content += `- h1: 最重要的标题，通常每个页面只有一个\n`;
      content += `- h2: 二级标题\n`;
      content += `- h3: 三级标题\n`;
      content += `- h4, h5, h6: 更低级别的标题\n\n`;

      content += `## Level 2\n\n`;
      content += `正确使用标题元素可以让文档结构更清晰，也有助于搜索引擎理解内容。\n\n`;
      content += `### 使用原则：\n`;
      content += `- 不要跳过标题层级\n`;
      content += `- 每个页面有且只有一个h1\n`;
      content += `- 标题要简洁明了\n`;
      content += `- 使用标题建立文档大纲\n\n`;

      content += `## Level 3\n\n`;
      content += `了解标题元素的样式控制和无障碍访问。\n\n`;
      content += `### 样式与可访问性：\n`;
      content += `- CSS样式控制标题外观\n`;
      content += `- 屏幕阅读器依赖标题导航\n`;
      content += `- 标题锚点：自动生成页面内链接\n`;
      content += `- 目录生成：基于标题自动创建目录\n\n`;

      content += `## Level 4\n\n`;
      content += `掌握标题元素的高级用法和最佳实践。\n\n`;
      content += `### 高级技巧：\n`;
      content += `- SEO优化：标题中的关键词\n`;
      content += `- 微数据：添加结构化数据\n`;
      content += `- 标题样式系统：建立一致的视觉层次\n`;
      content += `- 响应式标题：根据屏幕调整大小\n\n`;

      return content;
    },

    // 段落内容 - 4个等级
    generateParagraphContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `段落元素p是HTML中最常用的元素之一，用于包裹文本内容。\n\n`;
      content += `### 基本用法：\n`;
      content += `- \`<p>\` 标签定义段落\n`;
      content += `- 浏览器会在段落前后添加空白\n`;
      content += `- 可以包含文本、链接、图片等\n\n`;

      content += `## Level 2\n\n`;
      content += `段落元素在网页排版中扮演重要角色。\n\n`;
      content += `### 排版作用：\n`;
      content += `- 分隔内容：将文本分成逻辑段落\n`;
      content += `- 提高可读性：适当的段落长度\n`;
      content += `- 建立节奏：内容流的控制\n`;
      content += `- 搜索引擎友好：结构化内容\n\n`;

      content += `## Level 3\n\n`;
      content += `了解段落元素的样式控制和语义化使用。\n\n`;
      content += `### 样式控制：\n`;
      content += `- 行高控制：line-height 属性\n`;
      content += `- 缩进设置：text-indent\n`;
      content += `- 对齐方式：text-align\n`;
      content += `- 段落间距：margin 控制\n\n`;

      content += `## Level 4\n\n`;
      content += `掌握段落元素的高级应用和优化技巧。\n\n`;
      content += `### 高级应用：\n`;
      content += `- 语义化段落：article, section 等\n`;
      content += `- 富文本段落：包含格式化文本\n`;
      content += `- 响应式段落：移动端优化\n`;
      content += `- 性能优化：减少DOM节点数量\n\n`;

      return content;
    },

    // CSS基础内容 - 4个等级
    generateCSSBasicContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `CSS（Cascading Style Sheets）是用来控制网页样式和布局的语言。\n\n`;
      content += `### 基本概念：\n`;
      content += `- CSS规则由选择器和声明组成\n`;
      content += `- 选择器：指定要样式化的HTML元素\n`;
      content += `- 声明：属性和值对\n\n`;

      content += `## Level 2\n\n`;
      content += `CSS有多种添加样式到HTML文档的方法。\n\n`;
      content += `### 使用方式：\n`;
      content += `- 内联样式：直接在HTML标签中使用\n`;
      content += `- 内部样式表：在head中使用style标签\n`;
      content += `- 外部样式表：链接独立的.css文件\n`;
      content += `- 优先级：内联 > 内部 > 外部\n\n`;

      content += `## Level 3\n\n`;
      content += `掌握CSS选择器和常用属性。\n\n`;
      content += `### 选择器类型：\n`;
      content += `- 元素选择器：p, div, h1\n`;
      content += `- 类选择器：.classname\n`;
      content += `- ID选择器：#idname\n`;
      content += `- 属性选择器：[type="text"]\n\n`;

      content += `## Level 4\n\n`;
      content += `了解CSS的层叠和继承机制。\n\n`;
      content += `### 高级概念：\n`;
      content += `- 层叠：多个规则如何相互作用\n`;
      content += `- 特殊性：选择器的优先级计算\n`;
      content += `- 继承：子元素继承父元素样式\n`;
      content += `- 盒模型：元素的尺寸和间距\n\n`;

      return content;
    },

    // 文本样式内容 - 4个等级
    generateTextStylingContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `CSS提供了丰富的文本样式控制属性。\n\n`;
      content += `### 基础属性：\n`;
      content += `- color: 文本颜色\n`;
      content += `- font-size: 字体大小\n`;
      content += `- font-family: 字体类型\n`;
      content += `- font-weight: 字重（粗细）\n\n`;

      content += `## Level 2\n\n`;
      content += `掌握文本格式化的各种方法。\n\n`;
      content += `### 格式化属性：\n`;
      content += `- font-style: italic（斜体）\n`;
      content += `- text-decoration: underline（下划线）\n`;
      content += `- text-transform: 大小写转换\n`;
      content += `- letter-spacing: 字间距\n`;
      content += `- line-height: 行高\n\n`;

      content += `## Level 3\n\n`;
      content += `了解文本对齐和间距控制。\n\n`;
      content += `### 布局属性：\n`;
      content += `- text-align: 文本对齐方式\n`;
      content += `- text-indent: 首行缩进\n`;
      content += `- word-spacing: 词间距\n`;
      content += `- white-space: 空白处理\n\n`;

      content += `## Level 4\n\n`;
      content += `掌握高级文本样式技巧。\n\n`;
      content += `### 高级技巧：\n`;
      content += `- @font-face: 自定义字体\n`;
      content += `- text-shadow: 文本阴影\n`;
      content += `- 多列文本：column-count\n`;
      content += `- 响应式字体：clamp() 函数\n\n`;

      return content;
    },

    // JavaScript基础内容 - 4个等级
    generateJSBasicContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `JavaScript是一种高级编程语言，主要用于为网页添加交互功能。\n\n`;
      content += `### 基本概念：\n`;
      content += `- 脚本语言：在浏览器中运行\n`;
      content += `- 动态语言：变量类型可变\n`;
      content += `- 事件驱动：响应用户操作\n`;
      content += `- 对象模型：操作HTML文档\n\n`;

      content += `## Level 2\n\n`;
      content += `JavaScript的基本语法包括变量、数据类型和运算符。\n\n`;
      content += `### 语法基础：\n`;
      content += `- 变量声明：let, const, var\n`;
      content += `- 数据类型：字符串、数字、布尔值\n`;
      content += `- 运算符：算术、比较、逻辑\n`;
      content += `- 语句：条件、循环\n\n`;

      content += `## Level 3\n\n`;
      content += `函数是JavaScript的核心概念之一。\n\n`;
      content += `### 函数编程：\n`;
      content += `- 函数声明和调用\n`;
      content += `- 参数和返回值\n`;
      content += `- 作用域和闭包\n`;
      content += `- 箭头函数语法\n\n`;

      content += `## Level 4\n\n`;
      content += `掌握JavaScript的对象和数组操作。\n\n`;
      content += `### 数据结构：\n`;
      content += `- 对象字面量语法\n`;
      content += `- 数组操作方法\n`;
      content += `- JSON数据格式\n`;
      content += `- DOM操作基础\n\n`;

      return content;
    },

    // 事件监听器内容 - 4个等级
    generateEventListenerContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `事件监听器允许JavaScript响应用户的操作。\n\n`;
      content += `### 事件概念：\n`;
      content += `- 用户交互触发事件\n`;
      content += `- 浏览器自动分发事件\n`;
      content += `- JavaScript可以监听和处理事件\n`;
      content += `- 事件驱动编程模型\n\n`;

      content += `## Level 2\n\n`;
      content += `addEventListener是添加事件监听器的标准方法。\n\n`;
      content += `### 基本用法：\n`;
      content += `- element.addEventListener(event, handler)\n`;
      content += `- 第一个参数：事件类型（如'click'）\n`;
      content += `- 第二个参数：事件处理函数\n`;
      content += `- 可添加多个监听器\n\n`;

      content += `## Level 3\n\n`;
      content += `事件对象包含了事件的详细信息。\n\n`;
      content += `### 事件对象：\n`;
      content += `- event.target: 触发事件的元素\n`;
      content += `- event.type: 事件类型\n`;
      content += `- event.preventDefault(): 阻止默认行为\n`;
      content += `- event.stopPropagation(): 阻止事件冒泡\n\n`;

      content += `## Level 4\n\n`;
      content += `掌握事件委托和高级事件处理技巧。\n\n`;
      content += `### 高级技巧：\n`;
      content += `- 事件委托：利用事件冒泡\n`;
      content += `- 事件捕获：从外到内的传递\n`;
      content += `- 自定义事件：创建自己的事件\n`;
      content += `- 性能优化：减少事件监听器数量\n\n`;

      return content;
    },

    // 通用内容（兜底）- 4个等级
    generateGenericContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `这是该知识点的基础概念介绍。理解这些基本原理是学习后续高级内容的基础。\n\n`;
      content += `### 核心要点：\n`;
      content += `- 基本概念和定义\n`;
      content += `- 核心原理和机制\n`;
      content += `- 相关术语和概念\n\n`;

      content += `## Level 2\n\n`;
      content += `深入理解该知识点的工作原理和应用场景。\n\n`;
      content += `### 详细说明：\n`;
      content += `- 工作流程和步骤\n`;
      content += `- 实际应用案例\n`;
      content += `- 常见问题和解决方案\n`;
      content += `- 最佳实践建议\n\n`;

      content += `## Level 3\n\n`;
      content += `掌握该知识点的进阶应用和优化技巧。\n\n`;
      content += `### 进阶内容：\n`;
      content += `- 性能优化方法\n`;
      content += `- 高级配置和自定义\n`;
      content += `- 故障排除技巧\n`;
      content += `- 扩展和集成方案\n\n`;

      content += `## Level 4\n\n`;
      content += `精通该知识点的所有方面，能够独立解决复杂问题。\n\n`;
      content += `### 专家级内容：\n`;
      content += `- 架构设计和系统优化\n`;
      content += `- 最佳实践和设计模式\n`;
      content += `- 性能监控和调优\n`;
      content += `- 创新应用和技术前沿\n\n`;

      return content;
    },

    // 图片元素内容 - 4个等级
    generateImageContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `img 元素用于在网页中显示图片，是HTML中最常用的元素之一。\n\n`;
      content += `### 基本语法：\n`;
      content += `- \`<img src="图片路径" alt="描述">\`\n`;
      content += `- src 属性：指定图片文件的路径\n`;
      content += `- alt 属性：图片无法显示时的替代文本\n\n`;

      content += `## Level 2\n\n`;
      content += `掌握img元素的所有属性和基本用法。\n\n`;
      content += `### 常用属性：\n`;
      content += `- width 和 height：设置图片尺寸\n`;
      content += `- title：鼠标悬停时显示的提示文本\n`;
      content += `- loading：控制图片加载方式（lazy/eager）\n`;
      content += `- 相对路径和绝对路径的使用\n\n`;

      content += `## Level 3\n\n`;
      content += `深入了解图片优化的最佳实践。\n\n`;
      content += `### 优化技巧：\n`;
      content += `- 选择合适的图片格式（JPG/PNG/WebP/SVG）\n`;
      content += `- 压缩图片文件大小\n`;
      content += `- 使用响应式图片（srcset）\n`;
      content += `- 懒加载（loading="lazy"）提升性能\n\n`;

      content += `## Level 4\n\n`;
      content += `掌握高级的图片处理技术和无障碍访问。\n\n`;
      content += `### 高级应用：\n`;
      content += `- picture 元素和 source 元素\n`;
      content += `- 艺术方向（art direction）技术\n`;
      content += `- 图片预加载和缓存策略\n`;
      content += `- 无障碍访问：为装饰性图片使用空alt\n\n`;

      return content;
    },

    // 超链接内容 - 4个等级
    generateLinkContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `a 元素（anchor）用于创建超链接，让用户能够在不同页面间导航。\n\n`;
      content += `### 基本用法：\n`;
      content += `- \`<a href="URL">链接文本</a>\`\n`;
      content += `- href 属性：指定链接目标地址\n`;
      content += `- 链接文本：用户点击的可见文本\n\n`;

      content += `## Level 2\n\n`;
      content += `了解超链接的各种属性和链接类型。\n\n`;
      content += `### 链接属性：\n`;
      content += `- target="_blank"：在新标签页打开\n`;
      content += `- rel="noopener"：安全属性\n`;
      content += `- title：链接提示信息\n`;
      content += `- 内部链接和外部链接\n\n`;

      content += `## Level 3\n\n`;
      content += `掌握链接的SEO优化和用户体验设计。\n\n`;
      content += `### 最佳实践：\n`;
      content += `- 描述性链接文本（避免"点击这里"）\n`;
      content += `- 链接状态样式（:link, :visited, :hover, :active）\n`;
      content += `- 键盘导航支持\n`;
      content += `- 链接验证和维护\n\n`;

      content += `## Level 4\n\n`;
      content += `精通超链接的高级特性和无障碍访问。\n\n`;
      content += `### 高级特性：\n`;
      content += `- 锚点链接（#fragment）\n`;
      content += `- 邮件链接（mailto:）和电话链接（tel:）\n`;
      content += `- 下载链接（download 属性）\n`;
      content += `- ARIA 属性增强无障碍访问\n\n`;

      return content;
    },

    // CSS盒模型内容 - 4个等级
    generateBoxModelContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `CSS盒模型是CSS布局的基础，所有HTML元素都可以看作是一个盒子。\n\n`;
      content += `### 盒模型组成：\n`;
      content += `- content：内容区域\n`;
      content += `- padding：内边距\n`;
      content += `- border：边框\n`;
      content += `- margin：外边距\n\n`;

      content += `## Level 2\n\n`;
      content += `掌握盒模型的尺寸计算和属性设置。\n\n`;
      content += `### 尺寸计算：\n`;
      content += `- 标准盒模型：width = content\n`;
      content += `- IE盒模型：width = content + padding + border\n`;
      content += `- box-sizing 属性控制计算方式\n`;
      content += `- 外边距合并（margin collapsing）\n\n`;

      content += `## Level 3\n\n`;
      content += `深入了解盒模型的布局影响和调试技巧。\n\n`;
      content += `### 布局影响：\n`;
      content += `- 外边距折叠规则\n`;
      content += `- 负边距的应用\n`;
      content += `- 盒子阴影和圆角\n`;
      content += `- 开发者工具调试盒模型\n\n`;

      content += `## Level 4\n\n`;
      content += `精通盒模型的复杂应用和性能优化。\n\n`;
      content += `### 高级应用：\n`;
      content += `- Flexbox 和 Grid 中的盒模型\n`;
      content += `- 基于容器的尺寸单位\n`;
      content += `- 响应式盒模型设计\n`;
      content += `- CSS 逻辑属性（margin-inline 等）\n\n`;

      return content;
    },

    // 背景样式内容 - 4个等级
    generateBackgroundContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `background 属性用于设置元素的背景效果，让网页更加美观。\n\n`;
      content += `### 基本属性：\n`;
      content += `- background-color：背景颜色\n`;
      content += `- background-image：背景图片\n`;
      content += `- background-repeat：重复方式\n`;
      content += `- background-position：位置设置\n\n`;

      content += `## Level 2\n\n`;
      content += `掌握背景属性的各种设置选项。\n\n`;
      content += `### 常用设置：\n`;
      content += `- background-size：背景图片尺寸\n`;
      content += `- background-attachment：滚动行为\n`;
      content += `- 多重背景图片\n`;
      content += `- 渐变背景（linear-gradient）\n\n`;

      content += `## Level 3\n\n`;
      content += `学习背景样式的优化和高级效果。\n\n`;
      content += `### 高级效果：\n`;
      content += `- 径向渐变（radial-gradient）\n`;
      content += `- 锥形渐变（conic-gradient）\n`;
      content += `- CSS 图案和纹理\n`;
      content += `- 响应式背景图片\n\n`;

      content += `## Level 4\n\n`;
      content += `精通背景样式的创意应用和性能优化。\n\n`;
      content += `### 创意应用：\n`;
      content += `- 多重背景的复杂组合\n`;
      content += `- 动画背景效果\n`;
      content += `- CSS 自定义属性控制主题\n`;
      content += `- 背景图片的懒加载和优化\n\n`;

      return content;
    },

    // DOM操作内容 - 4个等级
    generateDOMContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `DOM（Document Object Model）是JavaScript操作HTML文档的接口。\n\n`;
      content += `### 基本概念：\n`;
      content += `- 文档对象模型\n`;
      content += `- 节点类型：元素节点、文本节点、属性节点\n`;
      content += `- document 对象：DOM的根对象\n`;
      content += `- getElementById() 方法\n\n`;

      content += `## Level 2\n\n`;
      content += `掌握常用的DOM选择和操作方法。\n\n`;
      content += `### 选择方法：\n`;
      content += `- getElementsByClassName()\n`;
      content += `- getElementsByTagName()\n`;
      content += `- querySelector() 和 querySelectorAll()\n`;
      content += `- 元素属性和内容操作\n\n`;

      content += `## Level 3\n\n`;
      content += `深入学习DOM操作的高级技巧。\n\n`;
      content += `### 高级操作：\n`;
      content += `- 创建和插入新元素\n`;
      content += `- 事件委托（event delegation）\n`;
      content += `- DOM 遍历和操作性能\n`;
      content += `- 现代 DOM API（classList, dataset）\n\n`;

      content += `## Level 4\n\n`;
      content += `精通DOM操作的架构设计和最佳实践。\n\n`;
      content += `### 架构设计：\n`;
      content += `- 组件化DOM操作\n`;
      content += `- 虚拟DOM概念\n`;
      content += `- 声明式 vs 命令式操作\n`;
      content += `- 性能监控和优化策略\n\n`;

      return content;
    },

    // 表单验证内容 - 4个等级
    generateFormValidationContent() {
      let content = '';

      content += `## Level 1\n\n`;
      content += `表单验证确保用户输入数据的质量和完整性。\n\n`;
      content += `### HTML验证：\n`;
      content += `- required 属性：必填字段\n`;
      content += `- type 属性：输入类型验证\n`;
      content += `- min/max 属性：数值范围\n`;
      content += `- pattern 属性：正则表达式\n\n`;

      content += `## Level 2\n\n`;
      content += `掌握HTML5表单验证的所有特性。\n\n`;
      content += `### 验证属性：\n`;
      content += `- email 和 url 类型\n`;
      content += `- step 和 minlength/maxlength\n`;
      content += `- novalidate 属性禁用验证\n`;
      content += `- :valid 和 :invalid 伪类\n\n`;

      content += `## Level 3\n\n`;
      content += `学习JavaScript增强的表单验证。\n\n`;
      content += `### JavaScript验证：\n`;
      content += `- Constraint Validation API\n`;
      content += `- setCustomValidity() 自定义错误\n`;
      content += `- 实时验证和异步验证\n`;
      content += `- 表单状态管理\n\n`;

      content += `## Level 4\n\n`;
      content += `精通表单验证的用户体验设计和安全性。\n\n`;
      content += `### 高级验证：\n`;
      content += `- 多重验证策略\n`;
      content += `- 服务端验证集成\n`;
      content += `- 无障碍验证反馈\n`;
      content += `- 安全考虑和XSS防护\n\n`;

      return content;
    },

    stopGeneration() {
      this.isGenerating = false;
      this.isMockGenerating = false;
      console.log('停止生成知识点内容');
    },

    resetGeneration() {
      this.stopGeneration();
      this.$emit('generated-contents-updated', {});
      this.updateGenerationProgress({
        total: 0,
        completed: 0,
        failed: 0
      });
      console.log('重置生成状态');
    },

    getGenerationStatus(nodeId) {
      // 查找节点信息
      const node = this.knowledgeData.graph.nodes.find(n => n.data.id === nodeId);
      if (!node) return 'unknown';

      // 章节节点无需生成
      if (node.data.type === 'chapter') {
        return 'skipped';
      }

      // 如果正在生成中且该节点还没有内容，则显示生成中状态
      if ((this.isGenerating || this.isMockGenerating) && this.currentGeneratedContents[nodeId] === undefined) {
        return 'generating';
      }

      // 检查是否已有生成结果
      if (this.currentGeneratedContents[nodeId] !== undefined) {
        return this.currentGeneratedContents[nodeId] === null ? 'failed' : 'completed';
      }

      return 'pending';
    },

    getGenerationStatusText(nodeId) {
      const status = this.getGenerationStatus(nodeId);
      switch (status) {
        case 'generating': return '生成中';
        case 'completed': return '已完成';
        case 'failed': return '失败';
        case 'skipped': return '无需生成';
        default: return '待生成';
      }
    },

    hasGeneratedContent(nodeId) {
      return this.currentGeneratedContents[nodeId] !== undefined && this.currentGeneratedContents[nodeId] !== null;
    },

    viewContent(nodeId) {
      this.currentContentNodeId = nodeId;
      this.currentContent = this.currentGeneratedContents[nodeId];
      this.showContentModal = true;
    },

    editContent(nodeId) {
      this.currentContentNodeId = nodeId;
      const content = this.currentGeneratedContents[nodeId];

      if (content) {
        // 解析存储的内容为结构化数据
        this.parseContentForEditing(content);
      } else {
        // 如果没有内容，初始化为空结构
        this.editingContent = {
          title: '',
          levels: []
        };
      }

      this.showEditModal = true;
      this.showContentModal = false; // 关闭查看弹窗
    },

    parseContentForEditing(contentText) {
      // 解析文本内容为结构化数据
      const lines = contentText.split('\n');
      let title = '';
      const levels = [];

      // 检查是否是markdown格式
      if (contentText.includes('# ')) {
        // Markdown格式解析
        let currentLevel = null;
        let currentDescription = '';

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i];
          const trimmedLine = line.trim();

          // 解析标题
          if (trimmedLine.startsWith('# ') && !title) {
            title = trimmedLine.substring(2).trim();
          }
          // 解析Level标题
          else if (trimmedLine.startsWith('## Level ') || trimmedLine.startsWith('##Level ')) {
            // 保存之前的level
            if (currentLevel !== null && currentDescription.trim()) {
              levels.push({
                level: currentLevel,
                description: currentDescription.trim()
              });
            }

            // 提取新的level编号
            const levelMatch = trimmedLine.match(/Level\s*(\d+)/i);
            if (levelMatch) {
              currentLevel = parseInt(levelMatch[1]);
              currentDescription = '';
            }
          }
          // 累积level内容
          else if (currentLevel !== null) {
            currentDescription += line + '\n';
          }
        }

        // 保存最后一个level
        if (currentLevel !== null && currentDescription.trim()) {
          levels.push({
            level: currentLevel,
            description: currentDescription.trim()
          });
        }
      } else {
        // 旧格式解析（兼容性）
        for (const line of lines) {
          const trimmedLine = line.trim();
          if (trimmedLine.startsWith('标题:')) {
            title = trimmedLine.substring(3).trim();
          } else if (trimmedLine.startsWith('Level ')) {
            const levelMatch = trimmedLine.match(/^Level (\d+):\s*(.*)$/);
            if (levelMatch) {
              const levelNum = parseInt(levelMatch[1]);
              const description = levelMatch[2].trim();
              levels.push({
                level: levelNum,
                description: description
              });
            }
          }
        }
      }

      this.editingContent = {
        title: title,
        levels: levels
      };
    },

    renderMarkdown(content) {
      if (!content) return '';
      const md = new MarkdownIt({
        html: true,
        linkify: true,
        typographer: true,
        breaks: true
      });
      return md.render(content);
    },

    addNewLevel() {
      const nextLevel = this.editingContent.levels.length + 1;
      this.editingContent.levels.push({
        level: nextLevel,
        description: ''
      });
    },

    removeLevel(index) {
      this.editingContent.levels.splice(index, 1);
      // 重新编号剩余的levels
      this.editingContent.levels.forEach((level, idx) => {
        level.level = idx + 1;
      });
    },

    parseContentTitle(contentText) {
      const lines = contentText.split('\n');
      for (const line of lines) {
        if (line.trim().startsWith('标题:')) {
          return line.trim().substring(3).trim();
        }
      }
      return '未命名知识点';
    },

    parseContentLevels(contentText) {
      const lines = contentText.split('\n');
      const levels = [];

      for (const line of lines) {
        const trimmedLine = line.trim();
        if (trimmedLine.startsWith('Level ')) {
          const levelMatch = trimmedLine.match(/^Level (\d+):\s*(.*)$/);
          if (levelMatch) {
            const levelNum = parseInt(levelMatch[1]);
            const description = levelMatch[2].trim();
            levels.push({
              level: levelNum,
              description: description
            });
          }
        }
      }

      return levels;
    },

    saveEditedContent() {
      if (this.currentContentNodeId) {
        // 将结构化数据转换为markdown格式存储
        let contentText = `# ${this.editingContent.title}\n\n`;
        this.editingContent.levels.forEach(level => {
          contentText += `## Level ${level.level}\n\n${level.description}\n\n`;
        });
        this.updateGeneratedContents(this.currentContentNodeId, contentText.trim());
        console.log('知识点内容已修改');
        console.log('保存的内容:', contentText.trim());
      }
      this.closeEditModal();
    },

    closeContentModal() {
      this.showContentModal = false;
      this.currentContentNodeId = null;
      this.currentContent = null;
    },

    closeEditModal() {
      this.showEditModal = false;
      this.currentContentNodeId = null;
      this.editingContent = {
        title: '',
        levels: []
      };
    },

    goToKnowledgeGraph() {
      // 跳转到知识图谱生成步骤（步骤3）
      this.$emit('go-to-step', 3);
    },

    // 更新生成的知识点内容（通过 emit 更新父组件）
    updateGeneratedContents(nodeId, content) {
      const updatedContents = { ...this.generatedContents };
      updatedContents[nodeId] = content;
      this.$emit('generated-contents-updated', updatedContents);
    },

    // 删除生成的知识点内容
    removeGeneratedContent(nodeId) {
      const updatedContents = { ...this.generatedContents };
      delete updatedContents[nodeId];
      this.$emit('generated-contents-updated', updatedContents);
    },

    // 更新生成进度（通过 emit 更新父组件）
    updateGenerationProgress(progress) {
      this.$emit('generation-progress-updated', progress);
    },

    async saveAllToDatabase() {
      if (this.isSaving) return;

      this.isSaving = true;

      try {
        // 将markdown内容解析为数据库格式
        const knowledgeContents = this.parseContentsForDatabase();

        // 准备要保存的数据 - 符合后端数据库结构
        const saveData = {
          course_id: "TEST001",
          knowledge_contents: knowledgeContents
        };

        console.log('保存知识点内容到数据库:', saveData);
        console.log('解析后的记录数量:', knowledgeContents.length);

        // 调用后端API保存知识点内容
        const response = await learningAPI.saveKnowledgeContent(saveData);

        if (response.code === '00000') {
            alert(`所有知识点内容已成功保存到数据库！\n共保存了 ${response.data.saved_count} 条记录`);
        } else {
            throw new Error(response.message || '保存失败');
        }
        // 通知父组件保存完成
        this.$emit('generation-completed', saveData);

      } catch (error) {
        console.error('保存知识点内容到数据库失败:', error);
        alert('保存失败: ' + (error.message || '未知错误'));
      } finally {
        this.isSaving = false;
      }
    },

    // 将markdown内容解析为数据库格式，每个level一个记录
    parseContentsForDatabase() {
      const records = [];

      // 遍历所有生成的知识点内容
      for (const [nodeId, content] of Object.entries(this.currentGeneratedContents)) {
        if (!content || content === null) continue;

        // 找到对应的节点信息，获取节点标题
        const node = this.knowledgeData.graph.nodes.find(n => n.data.id === nodeId);
        const nodeTitle = node ? node.data.label : `知识点 ${nodeId}`;

        // 解析markdown内容，按level拆分
        const levels = this.parseMarkdownLevels(content);

        // 为每个level创建数据库记录
        levels.forEach(levelData => {
          records.push({
            node_id: nodeId,
            level: levelData.level,
            title: nodeTitle,
            description: levelData.description
          });
        });
      }

      return records;
    },

    // 解析markdown内容，按Level拆分
    parseMarkdownLevels(markdownContent) {
      const levels = [];
      const lines = markdownContent.split('\n');
      let currentLevel = null;
      let currentDescription = '';

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmedLine = line.trim();

        // 检查是否是Level标题行
        const levelMatch = trimmedLine.match(/^#+\s*Level\s*(\d+)/i);
        if (levelMatch) {
          // 保存之前的level
          if (currentLevel !== null && currentDescription.trim()) {
            levels.push({
              level: currentLevel,
              description: currentDescription.trim()
            });
          }

          // 开始新的level
          currentLevel = parseInt(levelMatch[1]);
          currentDescription = '';
        }
        // 累积内容
        else if (currentLevel !== null) {
          currentDescription += line + '\n';
        }
      }

      // 保存最后一个level
      if (currentLevel !== null && currentDescription.trim()) {
        levels.push({
          level: currentLevel,
          description: currentDescription.trim()
        });
      }

      return levels;
    },

    async regenerateKnowledgePoint(node) {
      if (this.isRegeneratingNode) return;

      this.isRegeneratingNode = node.data.id;

      try {
        console.log(`开始重新生成知识点内容: ${node.data.label}`);

        // 记录重新生成前的状态，用于更新进度
        const previousStatus = this.getGenerationStatus(node.data.id);
        const wasFailed = previousStatus === 'failed';

        // 清除现有的内容
        this.removeGeneratedContent(node.data.id);

        // 调用API重新生成内容
        const response = await learningAPI.generateKnowledgeContent(node.data);

        // 存储新生成的内容
        if (response.levels && Array.isArray(response.levels)) {
          // 将分层学习内容转换为markdown格式
          let contentText = `# ${response.title || ''}\n\n`;
          response.levels.forEach((level) => {
            contentText += `## Level ${level.level}\n\n${level.description || ''}\n\n`;
          });
          this.updateGeneratedContents(node.data.id, contentText.trim());
        } else {
          // 如果没有levels，存储为JSON字符串
          this.updateGeneratedContents(node.data.id, JSON.stringify(response, null, 2));
        }

        console.log(`知识点内容重新生成成功: ${node.data.label}`);

        // 如果之前是失败状态，更新进度计数
        if (wasFailed) {
          const updatedProgress = { ...this.generationProgress };
          updatedProgress.completed++;
          updatedProgress.failed--;
          this.updateGenerationProgress(updatedProgress);
        }

        // 显示成功提示
        ElMessage.success(`知识点"${node.data.label}"重新生成成功！`);

      } catch (error) {
        console.error(`重新生成知识点内容失败: ${node.data.label}`, error);
        this.updateGeneratedContents(node.data.id, null); // 标记为失败

        // 显示错误提示
        const errorMsg = error?.message || error?.toString() || '未知错误';
        ElMessage.error(`重新生成失败: ${errorMsg}`);
      } finally {
        this.isRegeneratingNode = null;
      }
    }
  }
};
</script>

<style scoped>
.generation-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.control-buttons {
  display: flex;
  gap: 10px;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.progress-bar {
  width: 200px;
  height: 8px;
  background-color: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #4a90e2;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: #666;
  font-weight: bold;
}

.generation-list {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  max-height: 500px;
  overflow-y: auto;
}

/* 美化滚动条样式 */
.generation-list::-webkit-scrollbar {
  width: 6px;
}

.generation-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.generation-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.generation-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.list-header {
  display: grid;
  grid-template-columns: 60px 1fr 100px 100px 220px;
  gap: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
  font-weight: bold;
  color: #333;
}

.header-item {
  text-align: center;
}

.generation-item {
  display: grid;
  grid-template-columns: 60px 1fr 100px 100px 220px;
  gap: 15px;
  padding: 12px 15px;
  border-bottom: 1px solid #f0f0f0;
  align-items: center;
  transition: background-color 0.2s ease;
}

.generation-item:hover {
  background-color: #f8f9fa;
}

.generation-item.generating {
  background-color: #e3f2fd;
  border-left: 4px solid #4a90e2;
}

.item-seq {
  text-align: center;
  font-weight: bold;
  color: #666;
}

.item-title {
  font-weight: 500;
  color: #333;
}

.item-type {
  text-align: center;
}

.item-status {
  text-align: center;
}

.item-actions {
  display: flex;
  justify-content: flex-start;
  gap: 8px;
  flex-wrap: wrap;
}

.type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.type-badge.chapter {
  background-color: #e3f2fd;
  color: #1976d2;
}

.type-badge.knowledge {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.generating {
  background-color: #d1ecf1;
  color: #0c5460;
}

.status-badge.completed {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.failed {
  background-color: #f8d7da;
  color: #721c24;
}

.status-badge.skipped {
  background-color: #e2e3e5;
  color: #383d41;
}

.save-section {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.save-controls {
  text-align: center;
  margin-top: 15px;
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
}

.ml-1 {
  margin-left: 0.25rem;
}

.ml-2 {
  margin-left: 0.5rem;
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
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.large-modal {
  max-width: 1000px;
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

.content-display pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  max-height: 400px;
  overflow-y: auto;
}

.no-content {
  text-align: center;
  color: #999;
  padding: 40px;
  font-style: italic;
}

/* 编辑器样式 */
.levels-editor {
  margin-top: 20px;
}

.levels-editor label {
  display: block;
  margin-bottom: 15px;
  font-weight: bold;
  color: #333;
}

.level-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background-color: #fafafa;
}

.level-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.level-label {
  font-weight: bold;
  color: #4a90e2;
  font-size: 16px;
}

.level-description {
  width: 100%;
  min-height: 80px;
  resize: vertical;
}

.add-level {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.4;
}

.form-control:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

/* 查看内容样式 */
.structured-content {
  max-width: 100%;
}

.content-title {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
}

.content-title h4 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.content-levels {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.level-display {
  background-color: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
}

.level-header {
  margin-bottom: 10px;
}

.level-badge {
  display: inline-block;
  background-color: #4a90e2;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.level-description {
  color: #555;
  line-height: 1.6;
  white-space: pre-wrap;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  max-width: 400px;
  margin: 0 auto;
}

.empty-state-icon {
  margin-bottom: 24px;
  opacity: 0.7;
}

.empty-state-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.empty-state-description {
  font-size: 16px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 32px;
}

.empty-state-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>