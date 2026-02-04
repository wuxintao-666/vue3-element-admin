<template>
  <div class="card">
    <h2 class="card-title">编程练习题生成</h2>

    <!-- 前置条件警告 -->
    <div v-if="showPrerequisitesWarning">
      <div class="alert alert-warning">
        请先完成知识点图谱和知识点内容的生成与保存
      </div>
    </div>

    <!-- 主要内容 -->
    <div v-else-if="knowledgeGraph">
          <div class="alert alert-info">
            <p><strong>知识图谱信息:</strong></p>
            <p>图谱名称: {{ knowledgeGraph.name || '未命名' }}</p>
            <p>节点数量: {{ knowledgeGraph.graph.nodes ? knowledgeGraph.graph.nodes.length : 0 }}</p>
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
              <span class="header-item">测试题</span>
              <span class="header-item">类型</span>
              <span class="header-item">状态</span>
              <span class="header-item">操作</span>
            </div>

            <div
              v-for="(node, index) in (knowledgeGraph.graph.nodes || [])"
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
                  v-if="node.data && (hasGeneratedContent(node.data.id) || getGenerationStatus(node.data.id) === 'failed')"
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
              <strong>恭喜！</strong> 所有编程练习题已生成完成。
            </div>

            <div class="save-controls">
              <button
                @click="saveAllToDatabase"
                :disabled="isSaving"
                class="btn btn-success"
              >
                {{ isSaving ? '保存中...' : '保存所有测试题到数据库' }}
              </button>
            </div>
          </div>

          <!-- 内容详情弹窗 -->
          <div v-if="showContentModal" class="modal-overlay" @click="closeContentModal">
            <div class="modal-content" @click.stop>
              <div class="modal-header">
                <h3>{{ currentContentNode ? currentContentNode.label : '编程练习题内容' }}</h3>
                <button @click="closeContentModal" class="close-btn">&times;</button>
    </div>
    
              <div class="modal-body">
                <div v-if="currentContent" class="structured-content">
                  <div class="content-title">
                    <h4>{{ currentContent.title }}</h4>
      </div>
      
                  <div class="content-levels">
                    <div class="level-display">
                      <div class="level-header">
                        <span class="level-badge">任务描述</span>
                      </div>
                      <div class="level-description">{{ currentContent.description_md }}</div>
      </div>
      
                    <div class="level-display">
                      <div class="level-header">
                        <span class="level-badge">起始代码</span>
                      </div>
                      <div class="code-sections">
                        <div v-if="currentContent.start_code.html" class="code-section">
                          <h5>HTML</h5>
                          <pre><code class="language-html">{{ currentContent.start_code.html }}</code></pre>
                        </div>
                        <div v-if="currentContent.start_code.css" class="code-section">
                          <h5>CSS</h5>
                          <pre><code class="language-css">{{ currentContent.start_code.css }}</code></pre>
                        </div>
                        <div v-if="currentContent.start_code.js" class="code-section">
                          <h5>JavaScript</h5>
                          <pre><code class="language-javascript">{{ currentContent.start_code.js }}</code></pre>
                        </div>
        </div>
      </div>
      
                    <div v-if="currentContent.checkpoints && currentContent.checkpoints.length" class="level-display">
                      <div class="level-header">
                        <span class="level-badge">检查点</span>
                      </div>
                      <ul class="checkpoints-list">
                        <li v-for="(checkpoint, idx) in currentContent.checkpoints" :key="idx">
                          <strong>{{ checkpoint.name }}:</strong> {{ checkpoint.feedback }}
          </li>
        </ul>
      </div>
      
                    <div class="level-display">
                      <div class="level-header">
                        <span class="level-badge">参考答案</span>
                      </div>
                      <div class="code-sections">
                        <div v-if="currentContent.answer.html" class="code-section">
                          <h5>HTML</h5>
                          <pre><code class="language-html">{{ currentContent.answer.html }}</code></pre>
                        </div>
                        <div v-if="currentContent.answer.css" class="code-section">
                          <h5>CSS</h5>
                          <pre><code class="language-css">{{ currentContent.answer.css }}</code></pre>
                        </div>
                        <div v-if="currentContent.answer.js" class="code-section">
                          <h5>JavaScript</h5>
                          <pre><code class="language-javascript">{{ currentContent.answer.js }}</code></pre>
                        </div>
                      </div>
                    </div>
                  </div>
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
                <h3>编辑编程练习题 - {{ currentContentNode ? currentContentNode.label : '' }}</h3>
                <button @click="closeEditModal" class="close-btn">&times;</button>
              </div>

              <div class="modal-body">
                <div class="form-group">
                  <label>标题:</label>
                  <input v-model="editingContent.title" type="text" class="form-control" placeholder="输入测试题标题">
                </div>

                <div class="form-group">
                  <label>任务描述:</label>
                  <textarea v-model="editingContent.description_md" rows="6" class="form-control" placeholder="描述任务内容"></textarea>
                </div>

                <div class="form-group">
                  <label>起始代码:</label>
                  <div class="code-sections">
                    <div class="code-section">
                      <h5>HTML</h5>
                      <textarea v-model="editingContent.start_code.html" rows="6" class="form-control code-editor" placeholder="输入起始HTML代码"></textarea>
                    </div>
                    <div class="code-section">
                      <h5>CSS</h5>
                      <textarea v-model="editingContent.start_code.css" rows="6" class="form-control code-editor" placeholder="输入起始CSS代码"></textarea>
                    </div>
                    <div class="code-section">
                      <h5>JavaScript</h5>
                      <textarea v-model="editingContent.start_code.js" rows="6" class="form-control code-editor" placeholder="输入起始JavaScript代码"></textarea>
                    </div>
                  </div>
                </div>

                <div class="form-group">
                  <label>检查点:</label>
                  <div v-for="(checkpoint, idx) in editingContent.checkpoints" :key="idx" class="checkpoint-item">
                    <input
                      v-model="checkpoint.name"
                      type="text"
                      placeholder="检查点名称"
                      class="form-control checkpoint-name"
                    >
                    <input
                      v-model="checkpoint.feedback"
                      type="text"
                      placeholder="反馈信息"
                      class="form-control checkpoint-feedback"
                    >
                    <button @click="removeCheckpoint(idx)" class="btn btn-sm btn-danger">删除</button>
                  </div>
                  <button @click="addCheckpoint" class="btn btn-sm btn-outline">添加检查点</button>
                </div>

                <div class="form-group">
                  <label>参考答案:</label>
                  <div class="code-sections">
                    <div class="code-section">
                      <h5>HTML</h5>
                      <textarea v-model="editingContent.answer.html" rows="6" class="form-control code-editor" placeholder="输入答案HTML代码"></textarea>
                    </div>
                    <div class="code-section">
                      <h5>CSS</h5>
                      <textarea v-model="editingContent.answer.css" rows="6" class="form-control code-editor" placeholder="输入答案CSS代码"></textarea>
                    </div>
                    <div class="code-section">
                      <h5>JavaScript</h5>
                      <textarea v-model="editingContent.answer.js" rows="6" class="form-control code-editor" placeholder="输入答案JavaScript代码"></textarea>
                    </div>
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
    <div v-if="!knowledgeGraph">
        <div class="alert alert-warning">
          请先完成知识点图谱和知识点内容的生成
        </div>
        </div>
    </div>
  </div>
</template>

<script>
import { testGenerationAPI, programmingExerciseAPI } from './api/index.js';
import { TEST_COURSE_ID } from '@/constants';

export default {
  name: 'TestTaskDisplay',
  props: {
    knowledgeGraph: {
      type: Object,
      required: true
    },
    generatedContents: {
      type: Object,
      default: () => ({})
    },
    showPrerequisitesWarning: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      // 生成状态
      isGenerating: false,
      isMockGenerating: false,
      isRegeneratingNode: null, // 当前正在重新生成的节点ID

      // 生成的内容存储（现在通过 prop 获取）
      generatedTestTasks: {}, // 存储生成的测试题内容

      // 弹窗状态
      showContentModal: false,
      showEditModal: false,
      currentContentNodeId: null,
      currentContent: null,
      editingContent: {
        title: '',
        description_md: '',
        start_code: { html: '', css: '', js: '' },
        checkpoints: [],
        answer: { html: '', css: '', js: '' }
      },

      // 保存状态
      isSaving: false
    };
  },
  computed: {
    currentContentNode() {
      if (!this.currentContentNodeId || !this.knowledgeGraph.graph || !this.knowledgeGraph.graph.nodes) return null;
      return this.knowledgeGraph.graph.nodes.find(node => node.data.id === this.currentContentNodeId)?.data;
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
      return this.generatedTestTasks;
    },

    generationProgress() {
      // 计算生成进度
      const total = (this.knowledgeGraph.graph && this.knowledgeGraph.graph.nodes || []).filter(node =>
        node.data && (node.data.type === 'knowledge' || node.data.type === 'chapter')
      ).length;

      const completed = Object.keys(this.generatedTestTasks).filter(nodeId =>
        this.generatedTestTasks[nodeId] !== null
      ).length;

      const failed = Object.keys(this.generatedTestTasks).filter(nodeId =>
        this.generatedTestTasks[nodeId] === null
      ).length;

      return {
        total,
        completed,
        failed
      };
    }
  },
  methods: {
    async startGeneration() {
      if (this.isGenerating) return;

      this.isGenerating = true;
      this.isMockGenerating = false;
      // 获取需要生成的知识点和章节节点
      console.log(this.knowledgeGraph.graph.nodes);
      const targetNodes = this.knowledgeGraph.graph.nodes;

      console.log(`开始生成 ${targetNodes.length} 个编程练习题`);

      // 并行生成所有测试题
      await this.generateAllTestTasks(targetNodes);
    },

    async startMockGeneration() {
      if (this.isMockGenerating) return;

      this.isMockGenerating = true;
      this.isGenerating = false;
      // 获取需要生成的知识点和章节节点
      const targetNodes = (this.knowledgeGraph.graph && this.knowledgeGraph.graph.nodes || []).filter(node =>
        node.data && (node.data.type === 'knowledge' || node.data.type === 'chapter')
      );

      console.log(`开始模拟生成 ${targetNodes.length} 个编程练习题`);

      // 使用模拟数据生成
      await this.generateAllTestTasksMock(targetNodes);
    },

    async generateAllTestTasks(targetNodes) {
      if (targetNodes.length === 0) {
        this.isGenerating = false;
        console.log('没有需要生成的节点');
        return;
      }

      // 为每个节点创建生成任务
      const generationPromises = targetNodes.map(async (node, index) => {
        try {
          console.log(`开始生成编程练习题 (${index + 1}/${targetNodes.length}): ${node.data.label}`);

          // 获取该节点的知识点内容
          const learningContent = this.getLearningContentForNode(node.data);

          const requestData = {
            topic_id: node.data.id,
            knowledge_node: node.data,
            learning_content: learningContent
          };

          // 调用API生成测试题
          const response = await testGenerationAPI.generateTestTask(requestData);

          // 存储生成的内容
          this.updateGeneratedTestTasks(node.data.id, {
            title: response.title,
            description_md: response.description_md,
            start_code: response.start_code,
            checkpoints: response.checkpoints,
            answer: response.answer
          });

          console.log(`编程练习题生成成功: ${node.data.label}`);

        } catch (error) {
          console.error(`生成编程练习题失败: ${node.data.label}`, error);
          this.updateGeneratedTestTasks(node.data.id, null); // 标记为失败
        }
      });

      try {
        // 并发执行所有生成任务
        await Promise.all(generationPromises);
        console.log(`所有编程练习题生成完成`);
      } catch (error) {
        console.error('批量生成过程中发生错误:', error);
      } finally {
        // 生成完成
        this.isGenerating = false;
      }
    },

    async generateAllTestTasksMock(targetNodes) {
      if (targetNodes.length === 0) {
        this.isMockGenerating = false;
        console.log('没有需要生成的节点');
        return;
      }

      // 为每个节点创建模拟生成任务
      const generationPromises = targetNodes.map(async (node, index) => {
        try {
          console.log(`模拟生成编程练习题 (${index + 1}/${targetNodes.length}): ${node.data.label}`);

          // 模拟API调用延迟
          await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 1000));

          // 生成模拟的测试题内容
          const mockContent = this.generateMockTestTask(node.data);

          // 存储模拟生成的内容
          this.updateGeneratedTestTasks(node.data.id, mockContent);

          console.log(`编程练习题模拟生成成功: ${node.data.label}`);

        } catch (error) {
          console.error(`模拟生成编程练习题失败: ${node.data.label}`, error);
          this.updateGeneratedTestTasks(node.data.id, null); // 标记为失败
        }
      });

      try {
        // 并发执行所有模拟生成任务
        await Promise.all(generationPromises);
        console.log(`模拟生成完成`);
      } catch (error) {
        console.error('模拟生成过程中发生错误:', error);
      } finally {
        // 生成完成
        this.isMockGenerating = false;
      }
    },

    generateMockTestTask(nodeData) {
      // 生成模拟的编程练习题内容
      const title = '编程练习：' + nodeData.label;

      let description_md = nodeData.label + ' 编程练习\n\n';
      description_md += '这是一个关于 ' + nodeData.label + ' 的编程练习题。\n\n';
      description_md += '任务目标：\n\n';
      description_md += '- 理解相关概念\n';
      description_md += '- 掌握基本用法\n';
      description_md += '- 能够独立实现\n\n';

      const start_code = {
        html: '<!DOCTYPE html>\n<html>\n<head>\n<title>' + nodeData.label + '</title>\n</head>\n<body>\n<!-- 开始你的代码 -->\n</body>\n</html>',
        css: '/* 添加样式 */\nbody { margin: 20px; }',
        js: '// 添加JavaScript代码\nconsole.log(\'' + nodeData.label + '\');'
      };

      const checkpoints = [
        {
          name: '基础结构',
          feedback: '确保HTML文档结构正确'
        },
        {
          name: '样式实现',
          feedback: '检查CSS样式是否生效'
        },
        {
          name: '功能实现',
          feedback: '验证JavaScript功能是否正常'
        }
      ];

      const answer = {
        html: '<!DOCTYPE html>\n<html>\n<head>\n<title>' + nodeData.label + '</title>\n</head>\n<body>\n<h1>' + nodeData.label + '</h1>\n<p>练习完成</p>\n</body>\n</html>',
        css: 'body { margin: 20px; }\nh1 { color: blue; }',
        js: 'console.log(\'' + nodeData.label + ' 练习完成\');'
      };

      return {
        title,
        description_md,
        start_code,
        checkpoints,
        answer
      };
    },

    stopGeneration() {
      this.isGenerating = false;
      this.isMockGenerating = false;
      console.log('停止生成编程练习题');
    },

    resetGeneration() {
      this.stopGeneration();
      this.generatedTestTasks = {};
      console.log('重置生成状态');
    },

    getGenerationStatus(nodeId) {
      // 查找节点信息
      const node = (this.knowledgeGraph.graph && this.knowledgeGraph.graph.nodes || []).find(n => n.data && n.data.id === nodeId);
      if (!node) return 'unknown';

      // 章节节点无需生成
      // if (node.data.type === 'chapter') {
      //   return 'skipped';
      // }

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
        // 复制内容到编辑对象
        this.editingContent = {
          title: content.title || '',
          description_md: content.description_md || '',
          start_code: { ...content.start_code },
          checkpoints: [...(content.checkpoints || [])],
          answer: { ...content.answer }
        };
      } else {
        // 如果没有内容，初始化为空结构
        this.editingContent = {
          title: '',
          description_md: '',
          start_code: { html: '', css: '', js: '' },
          checkpoints: [],
          answer: { html: '', css: '', js: '' }
        };
      }

      this.showEditModal = true;
      this.showContentModal = false; // 关闭查看弹窗
    },

    saveEditedContent() {
      if (this.currentContentNodeId) {
        // 保存编辑的内容
        this.updateGeneratedTestTasks(this.currentContentNodeId, { ...this.editingContent });
        console.log('编程练习题内容已修改');
        console.log('保存的内容:', this.editingContent);
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
        description_md: '',
        start_code: { html: '', css: '', js: '' },
        checkpoints: [],
        answer: { html: '', css: '', js: '' }
      };
    },

    addCheckpoint() {
      this.editingContent.checkpoints.push({
        name: '',
        feedback: ''
      });
    },

    removeCheckpoint(index) {
      this.editingContent.checkpoints.splice(index, 1);
    },

    async saveAllToDatabase() {
      if (this.isSaving) return;

      this.isSaving = true;

      try {
        // 将测试题内容转换为数据库格式
        const exercises = this.parseContentsForDatabase();

        // 准备要保存的数据
        const saveData = {
          course_id: TEST_COURSE_ID,
          exercises: exercises
        };

        console.log('保存编程练习题到数据库:', saveData);
        console.log('解析后的记录数量:', exercises.length);

        // 调用后端API保存
        const response = await programmingExerciseAPI.saveProgrammingExercises(saveData);

        if (response.code === '00000') {
            alert(`所有编程练习题已成功保存到数据库！\n共保存了 ${response.data.saved_count} 条记录`);
        } else {
            throw new Error(response.message || '保存失败');
        }

        // 通知父组件保存完成
        this.$emit('generation-completed', saveData);

      } catch (error) {
        console.error('保存编程练习题到数据库失败:', error);
        alert('保存失败: ' + (error.message || '未知错误'));
      } finally {
        this.isSaving = false;
      }
    },



    // 将测试题内容转换为数据库格式
    parseContentsForDatabase() {
      const records = [];

      // 遍历所有生成的测试题内容
      for (const [nodeId, content] of Object.entries(this.currentGeneratedContents)) {
        if (!content || content === null) continue;

        // 找到对应的节点信息，获取节点标题
        const node = (this.knowledgeGraph.graph && this.knowledgeGraph.graph.nodes || []).find(n => n.data && n.data.id === nodeId);
        const nodeTitle = node ? node.data.label : `测试题 ${nodeId}`;

        records.push({
          node_id: nodeId,
          title: content.title || nodeTitle,
          description_md: content.description_md || '',
          start_code: content.start_code || { html: '', css: '', js: '' },
          checkpoints: content.checkpoints || [],
          answer: content.answer || { html: '', css: '', js: '' }
        });
      }

      return records;
    },

    // 获取节点的知识点内容
    // getLearningContentForNode(node) {
    //   // 对于知识点节点，直接返回对应的内容
    //   if (node.type === 'knowledge') {
    //     return this.generatedContents[node.id] || null;
    //   } else if (node.type === 'chapter') {
    //     // 对于章节节点，收集它包含的所有知识点的内容
    //     const chapterContents = {};

    //     // 遍历所有节点，找到属于这个章节的知识点
    //     for (const otherNode of (this.knowledgeGraph.graph && this.knowledgeGraph.graph.nodes || [])) {
    //       if (otherNode.data && otherNode.data.type === 'knowledge' && this.isNodeInChapter(otherNode.data, node)) {
    //         if (this.generatedContents[otherNode.data.id]) {
    //           chapterContents[otherNode.data.id] = this.generatedContents[otherNode.data.id];
    //         }
    //       }
    //     }

    //     return Object.keys(chapterContents).length > 0 ? chapterContents : null;
    //   }

    //   return null;
    // },

    // 判断知识点节点是否属于某个章节
    isNodeInChapter(knowledgeNode, chapterNode) {
      // 通过知识图谱的边关系来判断

      if (!this.knowledgeGraph.edges) {
        // 如果没有边数据，使用简单的层级判断
        return knowledgeNode.level > chapterNode.level;
      }

      // 检查是否存在从chapter到knowledge的边
      return this.knowledgeGraph.edges.some(edge =>
        edge.source === chapterNode.id &&
        edge.target === knowledgeNode.id &&
        edge.type === 'structural'
      );
    },

    // 更新生成的测试题内容（通过 emit 更新父组件）
    updateGeneratedTestTasks(nodeId, content) {
      const updatedContents = { ...this.generatedTestTasks };
      updatedContents[nodeId] = content;
      this.generatedTestTasks = updatedContents;
      this.$emit('generated-test-tasks-updated', updatedContents);
    },

    // 删除生成的测试题内容
    removeGeneratedTestTask(nodeId) {
      const updatedContents = { ...this.generatedTestTasks };
      delete updatedContents[nodeId];
      this.generatedTestTasks = updatedContents;
      this.$emit('generated-test-tasks-updated', updatedContents);
    },

    getLearningContentForNode(node) {
      // 获取节点的知识点内容，返回prompts.py期望的格式
      if (!this.generatedContents) {
        return null;
      }

      // 从generatedContents中获取内容
      const content = this.generatedContents[node.id];
      if (!content) {
        return null;
      }

      // 解析markdown内容，提取levels信息
      const levels = this.parseContentLevels(content);

      return {
        levels: levels
      };
    },

    parseContentLevels(contentText) {
      // 解析markdown内容，提取level信息
      const levels = [];
      const lines = contentText.split('\n');

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

      return levels;
    },

    async regenerateKnowledgePoint(node) {
      if (this.isRegeneratingNode) return;

      this.isRegeneratingNode = node.data.id;

      try {
        console.log(`开始重新生成编程练习题: ${node.data.label}`);

        // 记录重新生成前的状态
        const previousStatus = this.getGenerationStatus(node.data.id);
        const wasFailed = previousStatus === 'failed';

        // 清除现有的内容
        this.removeGeneratedTestTask(node.data.id);

        // 获取该节点的知识点内容
        const learningContent = this.getLearningContentForNode(node.data);

        const requestData = {
          topic_id: node.data.id,
          knowledge_node: node.data,
          learning_content: learningContent
        };

        // 调用API重新生成测试题
        const response = await testGenerationAPI.generateTestTask(requestData);

        // 存储新生成的内容
        this.updateGeneratedTestTasks(node.data.id, {
          title: response.title,
          description_md: response.description_md,
          start_code: response.start_code,
          checkpoints: response.checkpoints,
          answer: response.answer
        });

        console.log(`编程练习题重新生成成功: ${node.data.label}`);

      } catch (error) {
        console.error(`重新生成编程练习题失败: ${node.data.label}`, error);
        this.updateGeneratedTestTasks(node.data.id, null); // 标记为失败
      } finally {
        this.isRegeneratingNode = null;
      }
    },
    
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
  grid-template-columns: 60px 1fr 100px 100px 160px;
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
  grid-template-columns: 60px 1fr 100px 100px 160px;
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
  gap: 4px;
  flex-wrap: wrap;
  align-items: center;
}

.item-actions .btn {
  padding: 3px 6px;
  font-size: 11px;
  line-height: 1.2;
  min-width: auto;
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

.code-editor {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  resize: vertical;
  min-height: 80px;
}

.checkpoint-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.checkpoint-name,
.checkpoint-feedback {
  flex: 1;
}

.checkpoint-name {
  flex: 0 0 200px;
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

.code-sections {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.code-sections .code-section {
  background-color: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
}

.code-sections h5 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
  font-weight: 600;
}

.code-sections pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  background-color: #fff;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #ddd;
  max-height: 200px;
  overflow-y: auto;
}

.checkpoints-list {
  padding-left: 20px;
}

.checkpoints-list li {
  margin-bottom: 5px;
  line-height: 1.5;
}

/* 基础按钮样式 */
.btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #333;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn:hover {
  background-color: #f8f9fa;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #4a90e2;
  color: white;
  border-color: #4a90e2;
}

.btn-primary:hover:not(:disabled) {
  background-color: #357abd;
}

.btn-success {
  background-color: #27ae60;
  color: white;
  border-color: #27ae60;
}

.btn-success:hover:not(:disabled) {
  background-color: #229954;
}

.btn-info {
  background-color: #17a2b8;
  color: white;
  border-color: #17a2b8;
}

.btn-info:hover:not(:disabled) {
  background-color: #138496;
}

.btn-warning {
  background-color: #ffc107;
  color: #212529;
  border-color: #ffc107;
}

.btn-warning:hover:not(:disabled) {
  background-color: #e0a800;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
  border-color: #dc3545;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c82333;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  border-color: #6c757d;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #5a6268;
}

.btn-outline {
  background: transparent;
  border-color: #ddd;
}

.btn-outline:hover:not(:disabled) {
  background-color: #f8f9fa;
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

.prerequisites-warning {
  padding: 40px 20px;
  text-align: center;
}

.alert {
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}



.alert-warning {
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  color: #856404;
}

.alert-success {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.alert-danger {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}
.generate-section {
  text-align: center;
  padding: 40px 20px;
}

.generate-section .btn {
  padding: 12px 24px;
  font-size: 16px;
}

.help-text {
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}

.test-tasks-container {
  margin-top: 20px;
}

.tasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.tasks-header h3 {
  margin: 0;
  color: var(--primary-color);
}

.actions {
  display: flex;
  gap: 10px;
}

.test-task-item {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 20px;
  background: white;
}

.test-task-item.editing {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid var(--border-color);
  border-radius: 8px 8px 0 0;
}

.task-info h4 {
  margin: 0 0 5px 0;
  color: var(--primary-color);
}

.node-id {
  font-size: 12px;
  color: #666;
}

.node-type {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: bold;
  text-transform: uppercase;
}

.node-type.chapter {
  background-color: #3498db;
  color: white;
}

.node-type.knowledge {
  background-color: #27ae60;
  color: white;
}

.task-actions {
  display: flex;
  gap: 8px;
}

.task-view,
.task-edit {
  padding: 20px;
}

.task-title,
.task-description,
.task-start-code,
.task-checkpoints {
  margin-bottom: 20px;
}

.task-title strong,
.task-description strong,
.task-start-code strong,
.task-checkpoints strong {
  display: block;
  margin-bottom: 8px;
  color: var(--primary-color);
}

.code-tabs,
.code-edit-tabs {
  display: flex;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.code-tabs button,
.code-edit-tabs button {
  padding: 8px 16px;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.code-tabs button.active,
.code-edit-tabs button.active {
  border-bottom-color: var(--primary-color);
  color: var(--primary-color);
  font-weight: bold;
}

.code-block {
  background-color: #f8f9fa;
  border-radius: 4px;
  overflow: hidden;
}

.code-block pre {
  margin: 0;
  padding: 15px;
  overflow-x: auto;
  max-height: 300px;
}

.code-block pre code {
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.task-checkpoints ul {
  padding-left: 20px;
}

.task-checkpoints li {
  margin-bottom: 5px;
  padding: 5px 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: var(--primary-color);
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

.code-editor {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.4;
  resize: vertical;
}

.checkpoint-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.checkpoint-name,
.checkpoint-feedback {
  flex: 1;
}

.checkpoint-name {
  flex: 0 0 200px;
}

.btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: white;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.btn:hover {
  background-color: #f8f9fa;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-success {
  background-color: #27ae60;
  color: white;
  border-color: #27ae60;
}

.btn-success:hover:not(:disabled) {
  background-color: #219a52;
}

.btn-outline {
  background: transparent;
  border-color: var(--border-color);
}

.btn-outline:hover:not(:disabled) {
  background-color: #f8f9fa;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
  border-color: #e74c3c;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c0392b;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
  border-color: #95a5a6;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #7f8c8d;
}

.spinner,
.spinner-small {
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-left-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
}

.spinner-small {
  width: 12px;
  height: 12px;
}

.alert {
  padding: 12px 16px;
  border-radius: 4px;
  margin-top: 20px;
}

.alert-warning {
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  color: #856404;
}

.alert-danger {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3 {
  margin-top: 1em;
  margin-bottom: 0.5em;
  color: var(--primary-color);
}

.markdown-content ul {
  padding-left: 20px;
}

.markdown-content li {
  margin-bottom: 5px;
}

.markdown-content p {
  line-height: 1.6;
  margin: 0 0 1em 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>