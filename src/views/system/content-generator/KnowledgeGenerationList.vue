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
                :disabled="isGenerating || allGenerated"
                class="btn btn-primary"
              >
                {{ isGenerating ? '生成中...' : allGenerated ? '已全部生成' : '开始生成' }}
              </button>

              <button
                @click="startMockGeneration"
                :disabled="isGenerating || allGenerated"
                class="btn btn-success ml-2"
              >
                {{ isGenerating ? '生成中...' : allGenerated ? '已全部生成' : '模拟生成' }}
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
              :class="{ 'generating': isGenerating && !hasGeneratedContent(node.data.id) }"
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
      if (this.isGenerating) return;

      this.isGenerating = true;
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
          const mockContent = this.generateMockContent(node.data.label);

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
        this.isGenerating = false;
      }
    },

    generateMockContent(nodeLabel) {
      // 统一的模拟内容，所有知识点都使用相同的内容结构
      let mockContent = `# ${nodeLabel}\n\n`;

      mockContent += `## Level 1\n\n`;
      mockContent += `这是${nodeLabel}的基础概念介绍。理解这些基本原理是学习后续高级内容的基础。\n\n`;
      mockContent += `### 核心要点：\n`;
      mockContent += `- 基本概念和定义\n`;
      mockContent += `- 核心原理和机制\n`;
      mockContent += `- 相关术语和概念\n\n`;

      mockContent += `## Level 2\n\n`;
      mockContent += `深入理解${nodeLabel}的工作原理和应用场景。\n\n`;
      mockContent += `### 详细说明：\n`;
      mockContent += `- 工作流程和步骤\n`;
      mockContent += `- 实际应用案例\n`;
      mockContent += `- 常见问题和解决方案\n`;
      mockContent += `- 最佳实践建议\n\n`;

      mockContent += `## Level 3\n\n`;
      mockContent += `高级应用和优化技巧，掌握这些内容可以让你在实际工作中更加高效。\n\n`;
      mockContent += `### 进阶内容：\n`;
      mockContent += `- 性能优化方法\n`;
      mockContent += `- 高级配置和自定义\n`;
      mockContent += `- 故障排除技巧\n`;
      mockContent += `- 扩展和集成方案\n\n`;

      return mockContent.trim();
    },

    stopGeneration() {
      this.isGenerating = false;
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
      if (this.isGenerating && this.currentGeneratedContents[nodeId] === undefined) {
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
        // 准备要保存的数据
        const saveData = {
          course_id: "TEST001",
          knowledge_contents: this.currentGeneratedContents
        };
        console.log('保存知识点内容到数据库:', saveData);
        //模拟
        await new Promise(resolve => setTimeout(resolve, 2000));
        //await learningAPI.saveKnowledgeContent(saveData);

        alert('所有知识点内容已成功保存到数据库！');
        // 通知父组件保存完成
        this.$emit('generation-completed', saveData);

      } catch (error) {
        console.error('保存知识点内容到数据库失败:', error);
        alert('保存失败: ' + (error.message || '未知错误'));
      } finally {
        this.isSaving = false;
      }
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