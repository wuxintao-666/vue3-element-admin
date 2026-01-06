<template>
  <div class="conversation-analysis">
    <!-- 顶部概览 -->
    <div class="overview-header">
      <h1>对话分析系统</h1>
      <div class="overview-stats">
        <div class="stat-item">
          <div class="stat-value">{{ totalConversations }}</div>
          <div class="stat-label">总对话数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ totalUsers }}</div>
          <div class="stat-label">总用户数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ avgConversationLength.toFixed(1) }}</div>
          <div class="stat-label">平均轮次</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ avgResponseTime }}s</div>
          <div class="stat-label">平均响应时间</div>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：对话列表 -->
      <div class="conversation-list-section">
        <div class="section-header">
          <h2>对话列表</h2>
          <div class="filters">
            <div class="filter-group">
              <label>筛选用户：</label>
              <select v-model="selectedUser" @change="filterConversations">
                <option value="all">所有用户</option>
                <option v-for="user in uniqueUsers" :key="user" :value="user">{{ user }}</option>
              </select>
            </div>
            <div class="filter-group">
              <label>情绪状态：</label>
              <select v-model="selectedSentiment" @change="filterConversations">
                <option value="all">全部</option>
                <option value="positive">积极</option>
                <option value="neutral">中性</option>
                <option value="negative">消极</option>
              </select>
            </div>
          </div>
        </div>

        <div class="conversation-cards">
          <div 
            v-for="conv in filteredConversations" 
            :key="conv.conversation_id"
            class="conversation-card"
            :class="{ 'active': selectedConversationId === conv.conversation_id }"
            @click="selectConversation(conv.conversation_id)"
          >
            <div class="conversation-header">
              <div class="user-info">
                <span class="user-id">{{ conv.participant_id }}</span>
                <span class="topic-tag">{{ conv.context.topic }}</span>
              </div>
              <div class="time-info">
                {{ formatTime(conv.timestamp) }}
              </div>
            </div>
            
            <div class="conversation-preview">
              <div class="preview-text">
                {{ getConversationPreview(conv) }}
              </div>
              <div class="conversation-stats">
                <span class="turn-count">{{ conv.turns.length }} 轮对话</span>
                <span class="sentiment-badge" :class="getOverallSentiment(conv)">
                  {{ getOverallSentiment(conv) }}
                </span>
              </div>
            </div>

            <div class="conversation-metrics">
              <div class="metric">
                <div class="metric-label">理解度</div>
                <div class="metric-value">
                  {{ (getUnderstandingScore(conv) * 100).toFixed(0) }}%
                </div>
              </div>
              <div class="metric">
                <div class="metric-label">参与度</div>
                <div class="metric-value">
                  {{ (getEngagementScore(conv) * 100).toFixed(0) }}%
                </div>
              </div>
              <div class="metric">
                <div class="metric-label">效率</div>
                <div class="metric-value">
                  {{ getEfficiencyScore(conv) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：对话详情 -->
      <div class="conversation-detail-section" v-if="selectedConversation">
        <div class="detail-header">
          <h2>对话详情</h2>
          <div class="conversation-info">
            <span>用户：{{ selectedConversation.participant_id }}</span>
            <span>主题：{{ selectedConversation.context.topic }}</span>
            <span>时间：{{ formatTime(selectedConversation.timestamp) }}</span>
          </div>
        </div>

        <!-- 对话流可视化 -->
        <div class="dialogue-flow">
          <div class="flow-header">
            <h3>对话流程</h3>
            <div class="flow-legend">
              <div class="legend-item">
                <span class="legend-color student"></span>
                <span>学生</span>
              </div>
              <div class="legend-item">
                <span class="legend-color ai"></span>
                <span>AI助教</span>
              </div>
            </div>
          </div>
          
          <div class="dialogue-timeline">
            <div 
              v-for="(turn, index) in selectedConversation.turns"
              :key="index"
              class="turn-item"
              :class="[turn.speaker, getSentimentClass(turn.metadata.sentiment)]"
              @mouseenter="highlightTurn(index)"
              @mouseleave="clearHighlight"
            >
              <div class="turn-header">
                <span class="speaker-badge">{{ turn.speaker === 'student' ? '学生' : 'AI助教' }}</span>
                <span class="turn-time">{{ formatTurnTime(turn.timestamp) }}</span>
                <span class="turn-sentiment" v-if="turn.metadata.sentiment">
                  {{ getSentimentEmoji(turn.metadata.sentiment) }}
                </span>
              </div>
              <div class="turn-content">
                {{ turn.content }}
              </div>
              <div class="turn-metadata">
                <span v-if="turn.metadata.response_time" class="response-time">
                  响应时间：{{ turn.metadata.response_time }}ms
                </span>
                <span v-if="turn.metadata.confidence" class="confidence">
                  置信度：{{ (turn.metadata.confidence * 100).toFixed(0) }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 分析仪表板 -->
        <div class="analysis-dashboard">
          <!-- <div class="dashboard-section">
            <h3>对话分析</h3>
            <div class="analysis-metrics">
              <div class="analysis-card">
                <div class="analysis-title">情绪变化</div>
                <div ref="sentimentChart" class="chart-container"></div>
              </div>
              <div class="analysis-card">
                <div class="analysis-title">响应时间分布</div>
                <div ref="responseTimeChart" class="chart-container"></div>
              </div>
              <div class="analysis-card">
                <div class="analysis-title">对话轮次分布</div>
                <div class="turn-distribution">
                  <div class="turn-stats">
                    <div class="turn-stat">
                      <div class="stat-label">学生发言</div>
                      <div class="stat-value">
                        {{ getStudentTurnCount(selectedConversation) }}
                      </div>
                      <div class="stat-percent">
                        {{ getStudentTurnPercentage(selectedConversation) }}%
                      </div>
                    </div>
                    <div class="turn-stat">
                      <div class="stat-label">AI发言</div>
                      <div class="stat-value">
                        {{ getAITurnCount(selectedConversation) }}
                      </div>
                      <div class="stat-percent">
                        {{ getAITurnPercentage(selectedConversation) }}%
                      </div>
                    </div>
                  </div>
                  <div ref="turnDistributionChart" class="chart-container"></div>
                </div>
              </div>
            </div>
          </div> -->

          <!-- HTML知识点掌握 -->
          <div class="dashboard-section">
            <h3>HTML知识点掌握情况</h3>
            <div class="knowledge-progress">
              <div 
                v-for="(progress, topic) in getHTMLKnowledgeProgress(selectedConversation)"
                :key="topic"
                class="knowledge-item"
              >
                <div class="knowledge-info">
                  <span class="knowledge-topic">{{ topic }}</span>
                  <span class="knowledge-percent">{{ progress.percent }}%</span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: progress.percent + '%' }"
                    :class="progress.level"
                  ></div>
                </div>
                <div class="knowledge-status">{{ progress.status }}</div>
              </div>
            </div>
          </div>

          <!-- 关键洞察 -->
          <div class="dashboard-section">
            <h3>关键洞察</h3>
            <div class="insights">
              <div 
                v-for="insight in getConversationInsights(selectedConversation)"
                :key="insight.id"
                class="insight-card"
                :class="insight.type"
              >
                <div class="insight-icon">{{ getInsightIcon(insight.type) }}</div>
                <div class="insight-content">
                  <div class="insight-title">{{ insight.title }}</div>
                  <div class="insight-description">{{ insight.description }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 学习建议 -->
          <div class="dashboard-section">
            <h3>学习建议</h3>
            <div class="recommendations">
              <div 
                v-for="(rec, index) in getRecommendations(selectedConversation)"
                :key="index"
                class="recommendation-item"
              >
                <span class="rec-number">{{ index + 1 }}</span>
                <span class="rec-text">{{ rec }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

// 响应式数据
const selectedConversationId = ref(null)
const selectedUser = ref('all')
const selectedSentiment = ref('all')

// 对话数据 - 修改为HTML学习主题
const conversations = ref([
  {
    conversation_id: 'conv_001',
    participant_id: 'user_001',
    timestamp: '2024-01-15T10:30:00Z',
    session_id: 'session_001',
    context: {
      topic: 'HTML基础',
      difficulty: '初级',
      learning_goal: '理解HTML文档结构'
    },
    turns: [
      {
        speaker: 'student',
        content: '我正在学习HTML，但我不明白<!DOCTYPE html>是做什么用的？',
        timestamp: '2024-01-15T10:30:05Z',
        metadata: {
          response_time: 2000,
          text_complexity: 0.7,
          sentiment: 'confused',
          confidence: 0.3
        }
      },
      {
        speaker: 'ai_tutor',
        content: '很好的问题！<!DOCTYPE html>是文档类型声明，它告诉浏览器这是一个HTML5文档。在HTML5之前有更复杂的DOCTYPE声明，但现在这个是最简单的。',
        timestamp: '2024-01-15T10:30:15Z',
        metadata: {
          explanation_depth: 'detailed',
          scaffolding_type: 'example_based',
          hints_provided: 1
        }
      },
      {
        speaker: 'student',
        content: '所以我必须把它放在每个HTML文件的开头吗？如果我忘记写会怎样？',
        timestamp: '2024-01-15T10:30:45Z',
        metadata: {
          response_time: 30000,
          text_complexity: 0.8,
          sentiment: 'curious',
          confidence: 0.4
        }
      },
      {
        speaker: 'ai_tutor',
        content: '是的，应该放在每个HTML文件的最开始。如果不写，浏览器会进入"怪异模式"，可能无法正确渲染页面。但现代浏览器大多会尝试猜测文档类型。让我们看看一个完整的HTML5文档结构：<html><head><title>页面标题</title></head><body>页面内容</body></html>',
        timestamp: '2024-01-15T10:31:00Z',
        metadata: {
          explanation_depth: 'conceptual',
          scaffolding_type: 'conceptual_explanation',
          hints_provided: 0
        }
      },
      {
        speaker: 'student',
        content: '哦，我明白了！所以结构是：DOCTYPE声明 → html标签 → head和body。那head和body有什么区别？',
        timestamp: '2024-01-15T10:31:30Z',
        metadata: {
          response_time: 30000,
          text_complexity: 0.6,
          sentiment: 'understanding',
          confidence: 0.7
        }
      },
      {
        speaker: 'ai_tutor',
        content: '完全正确！head部分包含页面的元信息，如标题、字符编码、CSS和JavaScript链接，这些内容用户看不到。body部分包含用户能看到的所有内容，如文本、图片、链接等。',
        timestamp: '2024-01-15T10:31:45Z',
        metadata: {
          explanation_depth: 'application',
          scaffolding_type: 'guided_practice',
          hints_provided: 0
        }
      },
      {
        speaker: 'student',
        content: '太棒了！我现在理解了HTML文档的基本结构。我可以开始创建我的第一个网页了吗？',
        timestamp: '2024-01-15T10:32:15Z',
        metadata: {
          response_time: 30000,
          text_complexity: 0.5,
          sentiment: 'positive',
          confidence: 0.9
        }
      }
    ],
    summary: {
      total_turns: 7,
      student_speak_ratio: 0.43,
      average_response_time: 25000,
      completion_status: 'completed',
      learning_outcome: 'understood'
    }
  },
  {
    conversation_id: 'conv_002',
    participant_id: 'user_002',
    timestamp: '2024-01-15T14:20:00Z',
    session_id: 'session_002',
    context: {
      topic: 'HTML表单',
      difficulty: '中级',
      learning_goal: '创建交互式表单'
    },
    turns: [
      {
        speaker: 'student',
        content: '我正在尝试创建一个注册表单，但不确定<input>标签的不同type属性有什么区别？',
        timestamp: '2024-01-15T14:20:05Z',
        metadata: {
          response_time: 1500,
          text_complexity: 0.7,
          sentiment: 'neutral',
          confidence: 0.5
        }
      },
      {
        speaker: 'ai_tutor',
        content: '很好的问题！<input>标签的type属性定义了输入框的类型。常见的有：text(文本)、password(密码)、email(邮箱)、number(数字)、date(日期)等。不同的类型在移动设备上会显示不同的键盘。',
        timestamp: '2024-01-15T14:20:10Z',
        metadata: {
          explanation_depth: 'basic',
          scaffolding_type: 'direct_instruction',
          hints_provided: 0
        }
      },
      {
        speaker: 'student',
        content: '那<textarea>和<input type="text">有什么区别？什么时候用哪个？',
        timestamp: '2024-01-15T14:20:25Z',
        metadata: {
          response_time: 15000,
          text_complexity: 0.6,
          sentiment: 'curious',
          confidence: 0.6
        }
      },
      {
        speaker: 'ai_tutor',
        content: '很好观察到这个区别！<input type="text">是单行文本框，适合简短输入如用户名。<textarea>是多行文本区域，可以调整大小，适合评论、描述等长文本。',
        timestamp: '2024-01-15T14:20:35Z',
        metadata: {
          explanation_depth: 'intermediate',
          scaffolding_type: 'comparative_analysis',
          hints_provided: 1
        }
      },
      {
        speaker: 'student',
        content: '我明白了！那下拉选择框怎么做？我看到有<select>标签，但不知道如何添加选项。',
        timestamp: '2024-01-15T14:21:00Z',
        metadata: {
          response_time: 25000,
          text_complexity: 0.5,
          sentiment: 'engaged',
          confidence: 0.7
        }
      },
      {
        speaker: 'ai_tutor',
        content: '对的！<select>创建下拉列表，每个选项用<option>标签定义。例如：<select><option value="beijing">北京</option><option value="shanghai">上海</option></select>。value属性是提交表单时的值，标签内的文本是显示给用户看的。',
        timestamp: '2024-01-15T14:21:15Z',
        metadata: {
          explanation_depth: 'step_by_step',
          scaffolding_type: 'worked_example',
          hints_provided: 0
        }
      },
      {
        speaker: 'student',
        content: '哦，这样一步步来就清楚多了。谢谢！我现在可以创建一个完整的注册表单了。',
        timestamp: '2024-01-15T14:21:45Z',
        metadata: {
          response_time: 30000,
          text_complexity: 0.3,
          sentiment: 'positive',
          confidence: 0.8
        }
      }
    ],
    summary: {
      total_turns: 7,
      student_speak_ratio: 0.43,
      average_response_time: 20000,
      completion_status: 'completed',
      learning_outcome: 'mastered'
    }
  },
  {
    conversation_id: 'conv_003',
    participant_id: 'user_003',
    timestamp: '2024-01-15T16:45:00Z',
    session_id: 'session_003',
    context: {
      topic: 'HTML语义化',
      difficulty: '高级',
      learning_goal: '理解语义化标签'
    },
    turns: [
      {
        speaker: 'student',
        content: '我听说HTML5有很多新的语义化标签，但我不太明白为什么需要它们？',
        timestamp: '2024-01-15T16:45:05Z',
        metadata: {
          response_time: 1000,
          text_complexity: 0.8,
          sentiment: 'curious',
          confidence: 0.6
        }
      },
      {
        speaker: 'ai_tutor',
        content: '这是一个很重要的问题！语义化标签如<header>、<nav>、<main>、<article>、<section>、<footer>等，让HTML结构对机器（搜索引擎、屏幕阅读器）和开发者都更有意义。',
        timestamp: '2024-01-15T16:45:15Z',
        metadata: {
          explanation_depth: 'procedural',
          scaffolding_type: 'stepwise_procedure',
          hints_provided: 0
        }
      },
      {
        speaker: 'student',
        content: '那<article>和<section>有什么区别？看起来它们很相似。',
        timestamp: '2024-01-15T16:45:35Z',
        metadata: {
          response_time: 20000,
          text_complexity: 0.7,
          sentiment: 'engaged',
          confidence: 0.7
        }
      },
      {
        speaker: 'ai_tutor',
        content: '很好的观察！<article>表示一个独立、完整的内容块，如博客文章、新闻报道，它应该有自己的标题。<section>是文档中的一个主题分组，通常有标题，但不一定是独立的。一个<article>可以包含多个<section>。',
        timestamp: '2024-01-15T16:45:55Z',
        metadata: {
          explanation_depth: 'detailed_example',
          scaffolding_type: 'comparative_analysis',
          hints_provided: 0
        }
      },
      {
        speaker: 'student',
        content: '我理解了！那语义化对SEO（搜索引擎优化）有什么具体好处？',
        timestamp: '2024-01-15T16:46:25Z',
        metadata: {
          response_time: 30000,
          text_complexity: 0.8,
          sentiment: 'engaged',
          confidence: 0.75
        }
      },
      {
        speaker: 'ai_tutor',
        content: '很好的深入思考！语义化标签帮助搜索引擎理解页面结构，识别主要内容区域。例如，<main>标签告诉搜索引擎这是页面的主要内容，<nav>包含导航链接，<article>是独立内容。这有助于提高搜索排名和可访问性。',
        timestamp: '2024-01-15T16:46:45Z',
        metadata: {
          explanation_depth: 'applied',
          scaffolding_type: 'real_world_application',
          hints_provided: 0
        }
      },
      {
        speaker: 'student',
        content: '这太有用了！我现在明白了语义化的重要性，不仅仅是div和span了。非常感谢！',
        timestamp: '2024-01-15T16:47:15Z',
        metadata: {
          response_time: 30000,
          text_complexity: 0.6,
          sentiment: 'positive',
          confidence: 0.9
        }
      }
    ],
    summary: {
      total_turns: 7,
      student_speak_ratio: 0.43,
      average_response_time: 25000,
      completion_status: 'completed',
      learning_outcome: 'mastered'
    }
  },
  {
    conversation_id: 'conv_004',
    participant_id: 'user_001',
    timestamp: '2024-01-16T09:15:00Z',
    session_id: 'session_004',
    context: {
      topic: 'HTML媒体元素',
      difficulty: '中级',
      learning_goal: '嵌入图片和视频'
    },
    turns: [
      {
        speaker: 'student',
        content: '我想在我的网页中添加图片，但<img>标签总是显示不正确，alt属性是必须的吗？',
        timestamp: '2024-01-16T09:15:05Z',
        timestamp: '2024-01-16T09:15:05Z',
        metadata: {
          response_time: 2000,
          text_complexity: 0.6,
          sentiment: 'confused',
          confidence: 0.4
        }
      },
      {
        speaker: 'ai_tutor',
        content: '是的，alt属性对于可访问性非常重要！它提供图片的文本描述，当图片无法加载时显示，也帮助屏幕阅读器用户理解图片内容。基本语法：<img src="image.jpg" alt="图片描述">',
        timestamp: '2024-01-16T09:15:15Z',
        metadata: {
          explanation_depth: 'basic',
          scaffolding_type: 'direct_instruction',
          hints_provided: 1
        }
      },
      {
        speaker: 'student',
        content: '我明白了。那添加视频呢？HTML5有专门的视频标签吗？',
        timestamp: '2024-01-16T09:15:35Z',
        metadata: {
          response_time: 20000,
          text_complexity: 0.5,
          sentiment: 'curious',
          confidence: 0.6
        }
      },
      {
        speaker: 'ai_tutor',
        content: '是的！HTML5引入了<video>标签。基本用法：<video src="video.mp4" controls></video>。controls属性添加播放控件，你还可以指定width、height，以及添加多种格式的<source>标签作为备选。',
        timestamp: '2024-01-16T09:15:50Z',
        metadata: {
          explanation_depth: 'detailed',
          scaffolding_type: 'example_based',
          hints_provided: 0
        }
      },
      {
        speaker: 'student',
        content: '太棒了！那音频呢？有类似的标签吗？',
        timestamp: '2024-01-16T09:16:10Z',
        metadata: {
          response_time: 20000,
          text_complexity: 0.4,
          sentiment: 'engaged',
          confidence: 0.7
        }
      },
      {
        speaker: 'ai_tutor',
        content: '没错！HTML5也有<audio>标签，用法类似：<audio src="audio.mp3" controls></audio>。同样支持controls属性，以及多种音频格式的<source>标签。',
        timestamp: '2024-01-16T09:16:25Z',
        metadata: {
          explanation_depth: 'basic',
          scaffolding_type: 'analogy_based',
          hints_provided: 0
        }
      },
      {
        speaker: 'student',
        content: '现在我理解了HTML媒体元素的用法，可以给我的网页添加丰富的媒体内容了！',
        timestamp: '2024-01-16T09:16:50Z',
        metadata: {
          response_time: 25000,
          text_complexity: 0.5,
          sentiment: 'positive',
          confidence: 0.9
        }
      }
    ],
    summary: {
      total_turns: 7,
      student_speak_ratio: 0.43,
      average_response_time: 22500,
      completion_status: 'completed',
      learning_outcome: 'understood'
    }
  }
])

// 计算属性
const totalConversations = computed(() => conversations.value.length)
const totalUsers = computed(() => {
  const users = new Set(conversations.value.map(c => c.participant_id))
  return users.size
})
const avgConversationLength = computed(() => {
  const totalTurns = conversations.value.reduce((sum, conv) => sum + conv.turns.length, 0)
  return totalTurns / conversations.value.length
})
const avgResponseTime = computed(() => {
  const totalResponseTime = conversations.value.reduce((sum, conv) => {
    const studentTurns = conv.turns.filter(t => t.speaker === 'student')
    const avgTurnTime = studentTurns.reduce((turnSum, turn) => {
      return turnSum + (turn.metadata.response_time || 0)
    }, 0) / (studentTurns.length || 1)
    return sum + avgTurnTime
  }, 0)
  return Math.round(totalResponseTime / conversations.value.length / 1000)
})

const uniqueUsers = computed(() => {
  return [...new Set(conversations.value.map(c => c.participant_id))]
})

const filteredConversations = computed(() => {
  let filtered = conversations.value
  
  if (selectedUser.value !== 'all') {
    filtered = filtered.filter(conv => conv.participant_id === selectedUser.value)
  }
  
  if (selectedSentiment.value !== 'all') {
    filtered = filtered.filter(conv => {
      const sentiment = getOverallSentiment(conv)
      return sentiment === selectedSentiment.value
    })
  }
  
  return filtered
})

const selectedConversation = computed(() => {
  return conversations.value.find(c => c.conversation_id === selectedConversationId.value)
})

// 图表实例
let sentimentChart = null
let responseTimeChart = null
let turnDistributionChart = null

// 方法
const selectConversation = (conversationId) => {
  selectedConversationId.value = conversationId
  if (selectedConversationId.value) {
    // 延迟渲染图表，确保DOM已更新
    setTimeout(() => {
      renderCharts()
    }, 100)
  }
}

const filterConversations = () => {
  // 重置选中的对话
  selectedConversationId.value = null
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatTurnTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getConversationPreview = (conv) => {
  const firstTurn = conv.turns.find(t => t.speaker === 'student')
  return firstTurn ? firstTurn.content.substring(0, 60) + '...' : '无对话内容'
}

const getOverallSentiment = (conv) => {
  const sentiments = conv.turns
    .filter(t => t.speaker === 'student')
    .map(t => t.metadata.sentiment)
  
  if (sentiments.length === 0) return 'neutral'
  
  const positiveCount = sentiments.filter(s => ['positive', 'understanding', 'engaged'].includes(s)).length
  const negativeCount = sentiments.filter(s => ['negative', 'confused', 'frustrated'].includes(s)).length
  
  if (positiveCount > negativeCount) return 'positive'
  if (negativeCount > positiveCount) return 'negative'
  return 'neutral'
}

const getUnderstandingScore = (conv) => {
  // 基于对话轮次和情绪变化的简单理解度评估
  const studentTurns = conv.turns.filter(t => t.speaker === 'student')
  if (studentTurns.length === 0) return 0
  
  const lastSentiment = studentTurns[studentTurns.length - 1].metadata.sentiment
  const finalConfidence = studentTurns[studentTurns.length - 1].metadata.confidence || 0
  
  // 情绪权重
  const sentimentWeights = {
    'positive': 0.9,
    'understanding': 0.8,
    'engaged': 0.7,
    'curious': 0.7,
    'neutral': 0.5,
    'confused': 0.3,
    'frustrated': 0.2,
    'negative': 0.1
  }
  
  const sentimentWeight = sentimentWeights[lastSentiment] || 0.5
  
  return (sentimentWeight * 0.6 + finalConfidence * 0.4)
}

const getEngagementScore = (conv) => {
  // 基于学生发言比例和响应时间计算参与度
  const studentTurns = conv.turns.filter(t => t.speaker === 'student')
  const totalTurns = conv.turns.length
  
  if (totalTurns === 0) return 0
  
  const studentRatio = studentTurns.length / totalTurns
  
  // 计算平均响应时间（反向指标，响应时间越短参与度越高）
  const avgResponseTime = studentTurns.reduce((sum, turn) => {
    return sum + (turn.metadata.response_time || 30000)
  }, 0) / studentTurns.length
  
  const responseTimeScore = Math.max(0, 1 - avgResponseTime / 60000) // 60秒为基准
  
  return (studentRatio * 0.6 + responseTimeScore * 0.4)
}

const getEfficiencyScore = (conv) => {
  // 基于学习成果和对话轮次的效率评分
  const learningOutcome = conv.summary.learning_outcome
  const totalTurns = conv.turns.length
  
  const outcomeScores = {
    'mastered': 5,
    'understood': 4,
    'partial_understanding': 3,
    'not_understood': 2,
    'abandoned': 1
  }
  
  const outcomeScore = outcomeScores[learningOutcome] || 3
  
  // 轮次效率：理想的对话应该在5-10轮内完成
  const turnEfficiency = Math.max(0, 1 - Math.abs(totalTurns - 7.5) / 7.5)
  
  return (outcomeScore * 0.6 + turnEfficiency * 4 * 0.4).toFixed(1)
}

const getSentimentClass = (sentiment) => {
  const sentimentClasses = {
    'positive': 'sentiment-positive',
    'understanding': 'sentiment-understanding',
    'engaged': 'sentiment-engaged',
    'curious': 'sentiment-curious',
    'neutral': 'sentiment-neutral',
    'confused': 'sentiment-confused',
    'frustrated': 'sentiment-frustrated',
    'negative': 'sentiment-negative'
  }
  return sentimentClasses[sentiment] || ''
}

const getSentimentEmoji = (sentiment) => {
  const emojis = {
    'positive': '😊',
    'understanding': '🧠',
    'engaged': '🔥',
    'curious': '🤨',
    'neutral': '😐',
    'confused': '🤔',
    'frustrated': '😣',
    'negative': '😞'
  }
  return emojis[sentiment] || '❓'
}

const getStudentTurnCount = (conv) => {
  return conv.turns.filter(t => t.speaker === 'student').length
}

const getAITurnCount = (conv) => {
  return conv.turns.filter(t => t.speaker === 'ai_tutor').length
}

const getStudentTurnPercentage = (conv) => {
  return Math.round(getStudentTurnCount(conv) / conv.turns.length * 100)
}

const getAITurnPercentage = (conv) => {
  return Math.round(getAITurnCount(conv) / conv.turns.length * 100)
}

// 新增：获取HTML知识点掌握进度
const getHTMLKnowledgeProgress = (conv) => {
  const progress = {}
  const topic = conv.context.topic
  
  // 根据对话主题判断知识点掌握情况
  if (topic === 'HTML基础') {
    progress['文档结构'] = {
      percent: 85,
      level: 'high',
      status: '已掌握'
    }
    progress['基本标签'] = {
      percent: 75,
      level: 'medium',
      status: '学习中'
    }
    progress['属性使用'] = {
      percent: 65,
      level: 'medium',
      status: '学习中'
    }
  } else if (topic === 'HTML表单') {
    progress['输入类型'] = {
      percent: 90,
      level: 'high',
      status: '已掌握'
    }
    progress['表单元素'] = {
      percent: 80,
      level: 'high',
      status: '已掌握'
    }
    progress['表单验证'] = {
      percent: 60,
      level: 'medium',
      status: '需练习'
    }
  } else if (topic === 'HTML语义化') {
    progress['语义化概念'] = {
      percent: 95,
      level: 'high',
      status: '已掌握'
    }
    progress['标签区别'] = {
      percent: 85,
      level: 'high',
      status: '已掌握'
    }
    progress['SEO应用'] = {
      percent: 75,
      level: 'medium',
      status: '理解中'
    }
  } else if (topic === 'HTML媒体元素') {
    progress['图片嵌入'] = {
      percent: 80,
      level: 'high',
      status: '已掌握'
    }
    progress['视频音频'] = {
      percent: 70,
      level: 'medium',
      status: '学习中'
    }
    progress['可访问性'] = {
      percent: 65,
      level: 'medium',
      status: '需加强'
    }
  }
  
  return progress
}

const highlightTurn = (index) => {
  // 可以添加高亮效果
  const turnItems = document.querySelectorAll('.turn-item')
  turnItems.forEach((item, i) => {
    if (i === index) {
      item.style.transform = 'scale(1.02)'
      item.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'
    }
  })
}

const clearHighlight = () => {
  const turnItems = document.querySelectorAll('.turn-item')
  turnItems.forEach(item => {
    item.style.transform = 'scale(1)'
    item.style.boxShadow = 'none'
  })
}

const getConversationInsights = (conv) => {
  const insights = []
  
  // 分析情绪变化
  const studentTurns = conv.turns.filter(t => t.speaker === 'student')
  const firstSentiment = studentTurns[0]?.metadata.sentiment
  const lastSentiment = studentTurns[studentTurns.length - 1]?.metadata.sentiment
  
  if (lastSentiment === 'positive' && firstSentiment !== 'positive') {
    insights.push({
      id: 1,
      type: 'success',
      title: '情绪改善',
      description: '学生的情绪从困惑或中性转变为积极状态'
    })
  }
  
  // 分析学习深度
  const aiTurns = conv.turns.filter(t => t.speaker === 'ai_tutor')
  const hasConceptualExplanation = aiTurns.some(t => 
    t.metadata.explanation_depth?.includes('conceptual') ||
    t.metadata.scaffolding_type?.includes('conceptual')
  )
  
  if (hasConceptualExplanation) {
    insights.push({
      id: 2,
      type: 'info',
      title: '概念理解',
      description: 'AI助教提供了概念性解释，帮助学生深入理解HTML'
    })
  }
  
  // 分析响应模式
  const responseTimes = studentTurns.map(t => t.metadata.response_time || 0)
  const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length
  
  if (avgResponseTime < 15000) {
    insights.push({
      id: 3,
      type: 'info',
      title: '积极互动',
      description: '学生响应迅速，表现出较高的学习参与度'
    })
  }
  
  // 分析问题解决过程
  const hasWorkedExample = aiTurns.some(t => 
    t.metadata.scaffolding_type?.includes('example') ||
    t.metadata.explanation_depth?.includes('step_by_step')
  )
  
  if (hasWorkedExample) {
    insights.push({
      id: 4,
      type: 'success',
      title: '有效示范',
      description: '通过HTML代码示例逐步演示，帮助学生理解'
    })
  }
  
  // 分析学习结果
  if (conv.summary.learning_outcome === 'mastered' || conv.summary.learning_outcome === 'understood') {
    insights.push({
      id: 5,
      type: 'success',
      title: '学习成功',
      description: '学生成功掌握了HTML目标知识点'
    })
  }
  
  // HTML特定洞察
  const htmlKeywords = ['标签', '属性', '语义化', '表单', '结构']
  const hasHTMLKeywords = conv.turns.some(turn => 
    htmlKeywords.some(keyword => turn.content.includes(keyword))
  )
  
  if (hasHTMLKeywords) {
    insights.push({
      id: 6,
      type: 'info',
      title: 'HTML重点',
      description: '对话聚焦HTML核心概念，学习方向正确'
    })
  }
  
  return insights
}

const getInsightIcon = (type) => {
  const icons = {
    'success': '✓',
    'info': 'ℹ',
    'warning': '⚠',
    'error': '✗'
  }
  return icons[type] || '•'
}

const getRecommendations = (conv) => {
  const recommendations = []
  const overallSentiment = getOverallSentiment(conv)
  const understandingScore = getUnderstandingScore(conv)
  const topic = conv.context.topic
  
  // 基于情绪的建议
  if (overallSentiment === 'negative' || overallSentiment === 'frustrated') {
    recommendations.push('学生表现出挫败感，建议调整HTML学习节奏或提供更多鼓励')
  }
  
  // 基于理解度的建议
  if (understandingScore < 0.5) {
    recommendations.push('学生对HTML概念理解不够深入，建议提供更多基础解释和代码实例')
  } else if (understandingScore < 0.7) {
    recommendations.push('学生基本理解HTML概念，建议通过实际编写网页巩固知识')
  } else {
    recommendations.push('学生掌握良好，可以引入更复杂的HTML5新特性学习')
  }
  
  // 基于HTML主题的特定建议
  if (topic === 'HTML基础') {
    recommendations.push('建议下一步学习CSS样式，将HTML结构与样式分离')
  } else if (topic === 'HTML表单') {
    recommendations.push('建议学习表单验证和JavaScript交互，使表单功能更完整')
  } else if (topic === 'HTML语义化') {
    recommendations.push('建议学习ARIA属性，进一步提升网页可访问性')
  } else if (topic === 'HTML媒体元素') {
    recommendations.push('建议学习响应式图片和视频，适配不同设备')
  }
  
  // 基于对话模式
  const studentTurns = conv.turns.filter(t => t.speaker === 'student')
  const aiTurns = conv.turns.filter(t => t.speaker === 'ai_tutor')
  
  if (aiTurns.length > studentTurns.length * 1.5) {
    recommendations.push('AI助教发言过多，建议更多地鼓励学生表达自己的HTML学习想法')
  }
  
  // 基于响应时间
  const responseTimes = studentTurns.map(t => t.metadata.response_time || 0)
  const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length
  
  if (avgResponseTime > 30000) {
    recommendations.push('学生响应时间较长，可能需要更多时间思考或遇到HTML编码困难')
  }
  
  return recommendations
}

// 图表渲染方法
const renderCharts = () => {
  if (!selectedConversation.value) return
  
  renderSentimentChart()
  renderResponseTimeChart()
  renderTurnDistributionChart()
}

const renderSentimentChart = () => {
  const container = document.querySelector('.analysis-card:nth-child(1) .chart-container')
  if (!container) return
  
  if (sentimentChart) {
    sentimentChart.dispose()
  }
  
  sentimentChart = echarts.init(container)
  
  const studentTurns = selectedConversation.value.turns.filter(t => t.speaker === 'student')
  const sentimentData = studentTurns.map((turn, index) => {
    const sentiment = turn.metadata.sentiment
    const sentimentValues = {
      'positive': 3,
      'understanding': 2.5,
      'engaged': 2,
      'curious': 1.5,
      'neutral': 1,
      'confused': 0,
      'frustrated': -1,
      'negative': -2
    }
    return {
      name: `轮次 ${index + 1}`,
      value: [index, sentimentValues[sentiment] || 0],
      sentiment: sentiment
    }
  })
  
  const option = {
    tooltip: {
      formatter: function(params) {
        const sentimentNames = {
          'positive': '积极',
          'understanding': '理解中',
          'engaged': '投入',
          'curious': '好奇',
          'neutral': '中性',
          'confused': '困惑',
          'frustrated': '挫败',
          'negative': '消极'
        }
        return `轮次 ${params.data.value[0] + 1}<br/>情绪: ${sentimentNames[params.data.sentiment] || params.data.sentiment}<br/>评分: ${params.data.value[1]}`
      }
    },
    xAxis: {
      type: 'category',
      name: '对话轮次',
      data: sentimentData.map((_, i) => i + 1),
      axisLine: {
        lineStyle: {
          color: '#E5E7EB'
        }
      },
      axisLabel: {
        color: '#9CA3AF'
      }
    },
    yAxis: {
      type: 'value',
      name: '情绪评分',
      min: -3,
      max: 4,
      axisLine: {
        lineStyle: {
          color: '#E5E7EB'
        }
      },
      axisLabel: {
        color: '#9CA3AF'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#374151'
        }
      }
    },
    series: [{
      data: sentimentData,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        width: 3,
        color: '#60A5FA'
      },
      itemStyle: {
        color: function(params) {
          const sentiment = params.data.sentiment
          const colors = {
            'positive': '#34D399',
            'understanding': '#60A5FA',
            'engaged': '#FBBF24',
            'curious': '#A78BFA',
            'neutral': '#9CA3AF',
            'confused': '#F87171',
            'frustrated': '#DC2626',
            'negative': '#7C2D12'
          }
          return colors[sentiment] || '#60A5FA'
        }
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          {
            offset: 0,
            color: 'rgba(96, 165, 250, 0.5)'
          },
          {
            offset: 1,
            color: 'rgba(96, 165, 250, 0.1)'
          }
        ])
      }
    }],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
      backgroundColor: 'transparent'
    }
  }
  
  sentimentChart.setOption(option)
}

const renderResponseTimeChart = () => {
  const container = document.querySelector('.analysis-card:nth-child(2) .chart-container')
  if (!container) return
  
  if (responseTimeChart) {
    responseTimeChart.dispose()
  }
  
  responseTimeChart = echarts.init(container)
  
  const studentTurns = selectedConversation.value.turns.filter(t => t.speaker === 'student')
  const responseTimeData = studentTurns.map((turn, index) => {
    return {
      name: `轮次 ${index + 1}`,
      value: turn.metadata.response_time || 0
    }
  })
  
  const option = {
    tooltip: {
      formatter: function(params) {
        return `${params.name}<br/>响应时间: ${params.value}ms`
      }
    },
    xAxis: {
      type: 'category',
      data: responseTimeData.map((_, i) => i + 1),
      axisLine: {
        lineStyle: {
          color: '#E5E7EB'
        }
      },
      axisLabel: {
        color: '#9CA3AF'
      }
    },
    yAxis: {
      type: 'value',
      name: '响应时间(ms)',
      axisLine: {
        lineStyle: {
          color: '#E5E7EB'
        }
      },
      axisLabel: {
        color: '#9CA3AF'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#374151'
        }
      }
    },
    series: [{
      data: responseTimeData.map(d => d.value),
      type: 'bar',
      barWidth: '60%',
      itemStyle: {
        color: function(params) {
          const value = params.value
          if (value < 10000) return '#34D399'
          if (value < 20000) return '#FBBF24'
          if (value < 30000) return '#F87171'
          return '#DC2626'
        }
      }
    }],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
      backgroundColor: 'transparent'
    }
  }
  
  responseTimeChart.setOption(option)
}

const renderTurnDistributionChart = () => {
  const container = document.querySelector('.analysis-card:nth-child(3) .chart-container')
  if (!container) return
  
  if (turnDistributionChart) {
    turnDistributionChart.dispose()
  }
  
  turnDistributionChart = echarts.init(container)
  
  const studentCount = getStudentTurnCount(selectedConversation.value)
  const aiCount = getAITurnCount(selectedConversation.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    series: [{
      name: '发言分布',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#1F2937',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center',
        color: '#F9FAFB'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '14',
          fontWeight: 'bold',
          color: '#F9FAFB'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: studentCount, name: '学生发言' },
        { value: aiCount, name: 'AI助教发言' }
      ],
      color: ['#60A5FA', '#34D399']
    }]
  }
  
  turnDistributionChart.setOption(option)
}

// 初始化
onMounted(() => {
  // 默认选择第一个对话
  if (conversations.value.length > 0 && !selectedConversationId.value) {
    selectConversation(conversations.value[0].conversation_id)
  }
})

onUnmounted(() => {
  // 清理图表实例
  if (sentimentChart) sentimentChart.dispose()
  if (responseTimeChart) responseTimeChart.dispose()
  if (turnDistributionChart) turnDistributionChart.dispose()
})
</script>

<style scoped>
.conversation-analysis {
  min-height: 100vh;
  background: #304156;
  padding: 24px;
}

.overview-header {
  margin-bottom: 30px;
}

.overview-header h1 {
  color: #F9FAFB;
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 20px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.overview-stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat-item {
  background: rgba(31, 41, 55, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 20px;
  min-width: 150px;
  text-align: center;
  border: 1px solid rgba(75, 85, 99, 0.5);
  transition: all 0.3s ease;
  flex: 1;
}

.stat-item:hover {
  transform: translateY(-5px);
  background: rgba(31, 41, 55, 0.9);
  border-color: #4B5563;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #60A5FA;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #9CA3AF;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 24px;
  height: calc(100vh - 200px);
}

.conversation-list-section {
  background: #1F2937;
  border-radius: 15px;
  padding: 24px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  overflow-y: auto;
  border: 1px solid #374151;
}

.section-header {
  margin-bottom: 20px;
  position: sticky;
  top: 0;
  background: #1F2937;
  z-index: 10;
  padding-bottom: 20px;
}

.section-header h2 {
  color: #F9FAFB;
  font-size: 24px;
  margin-bottom: 16px;
}

.filters {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  color: #D1D5DB;
  white-space: nowrap;
}

.filter-group select {
  padding: 8px 16px;
  border: 2px solid #4B5563;
  border-radius: 8px;
  background: #374151;
  color: #F9FAFB;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.3s ease;
  min-width: 120px;
}

.filter-group select:focus {
  outline: none;
  border-color: #60A5FA;
}

.conversation-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.conversation-card {
  background: #374151;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.conversation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  border-color: #4B5563;
  background: #4B5563;
}

.conversation-card.active {
  border-color: #60A5FA;
  background: #4B5563;
  box-shadow: 0 8px 25px rgba(96, 165, 250, 0.2);
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-id {
  font-size: 16px;
  font-weight: 600;
  color: #F9FAFB;
}

.topic-tag {
  padding: 4px 12px;
  background: rgba(96, 165, 250, 0.2);
  color: #60A5FA;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.time-info {
  font-size: 12px;
  color: #9CA3AF;
}

.conversation-preview {
  margin-bottom: 16px;
}

.preview-text {
  font-size: 14px;
  color: #D1D5DB;
  line-height: 1.5;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.conversation-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.turn-count {
  font-size: 12px;
  color: #9CA3AF;
}

.sentiment-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.sentiment-badge.positive {
  background: rgba(52, 211, 153, 0.2);
  color: #34D399;
}

.sentiment-badge.neutral {
  background: rgba(251, 191, 36, 0.2);
  color: #FBBF24;
}

.sentiment-badge.negative {
  background: rgba(248, 113, 113, 0.2);
  color: #F87171;
}

.conversation-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.metric {
  text-align: center;
  padding: 12px;
  background: #1F2937;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.metric-label {
  font-size: 11px;
  color: #9CA3AF;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 700;
  color: #F9FAFB;
}

.conversation-detail-section {
  background: #1F2937;
  border-radius: 15px;
  padding: 24px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  overflow-y: auto;
  border: 1px solid #374151;
}

.detail-header {
  margin-bottom: 24px;
  position: sticky;
  top: 0;
  background: #1F2937;
  z-index: 10;
  padding-bottom: 20px;
  border-bottom: 2px solid #374151;
}

.detail-header h2 {
  color: #F9FAFB;
  font-size: 24px;
  margin-bottom: 12px;
}

.conversation-info {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.conversation-info span {
  font-size: 14px;
  color: #D1D5DB;
  padding: 6px 16px;
  background: #374151;
  border-radius: 15px;
}

.dialogue-flow {
  margin-bottom: 32px;
}

.flow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.flow-header h3 {
  color: #F9FAFB;
  font-size: 20px;
}

.flow-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #D1D5DB;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-color.student {
  background: #60A5FA;
}

.legend-color.ai {
  background: #34D399;
}

.dialogue-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.turn-item {
  padding: 20px;
  border-radius: 12px;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.turn-item.student {
  background: rgba(96, 165, 250, 0.1);
  border-left-color: #60A5FA;
  margin-right: 20%;
}

.turn-item.ai_tutor {
  background: rgba(52, 211, 153, 0.1);
  border-left-color: #34D399;
  margin-left: 20%;
}

.turn-item.sentiment-positive {
  box-shadow: inset 0 0 0 1px rgba(52, 211, 153, 0.3);
}

.turn-item.sentiment-understanding {
  box-shadow: inset 0 0 0 1px rgba(96, 165, 250, 0.3);
}

.turn-item.sentiment-engaged {
  box-shadow: inset 0 0 0 1px rgba(251, 191, 36, 0.3);
}

.turn-item.sentiment-curious {
  box-shadow: inset 0 0 0 1px rgba(167, 139, 250, 0.3);
}

.turn-item.sentiment-confused {
  box-shadow: inset 0 0 0 1px rgba(248, 113, 113, 0.3);
}

.turn-item.sentiment-frustrated {
  box-shadow: inset 0 0 0 1px rgba(220, 38, 38, 0.3);
}

.turn-item.sentiment-negative {
  box-shadow: inset 0 0 0 1px rgba(124, 45, 18, 0.3);
}

.turn-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.speaker-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.student .speaker-badge {
  background: #60A5FA;
}

.ai_tutor .speaker-badge {
  background: #34D399;
}

.turn-time {
  font-size: 12px;
  color: #9CA3AF;
}

.turn-sentiment {
  font-size: 16px;
  margin-left: auto;
}

.turn-content {
  font-size: 15px;
  line-height: 1.6;
  color: #F9FAFB;
  margin-bottom: 12px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.turn-metadata {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #9CA3AF;
}

.response-time,
.confidence {
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.analysis-dashboard {
  margin-top: 32px;
}

.dashboard-section {
  margin-bottom: 32px;
}

.dashboard-section h3 {
  color: #F9FAFB;
  font-size: 20px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #374151;
}

.analysis-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.analysis-card {
  background: #374151;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.analysis-title {
  font-size: 14px;
  font-weight: 600;
  color: #F9FAFB;
  margin-bottom: 12px;
}

.chart-container {
  height: 200px;
  width: 100%;
}

.turn-distribution {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  align-items: center;
}

.turn-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.turn-stat {
  background: #1F2937;
  padding: 16px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.stat-label {
  font-size: 12px;
  color: #9CA3AF;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #F9FAFB;
  margin-bottom: 2px;
}

.stat-percent {
  font-size: 12px;
  color: #9CA3AF;
}

/* HTML知识点掌握进度样式 */
.knowledge-progress {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.knowledge-item {
  background: #374151;
  border-radius: 12px;
  padding: 16px;
}

.knowledge-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.knowledge-topic {
  font-size: 14px;
  font-weight: 600;
  color: #F9FAFB;
}

.knowledge-percent {
  font-size: 18px;
  font-weight: 700;
  color: #60A5FA;
}

.progress-bar {
  height: 8px;
  background: #1F2937;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 1s ease-in-out;
}

.progress-fill.high {
  background: linear-gradient(90deg, #34D399, #10B981);
}

.progress-fill.medium {
  background: linear-gradient(90deg, #FBBF24, #F59E0B);
}

.progress-fill.low {
  background: linear-gradient(90deg, #F87171, #EF4444);
}

.knowledge-status {
  font-size: 12px;
  color: #9CA3AF;
  text-align: right;
}

.insights {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.insight-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  background: #374151;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  border-left: 4px solid #ccc;
}

.insight-card.success {
  border-left-color: #34D399;
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
}

.insight-card.info {
  border-left-color: #60A5FA;
  background: linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
}

.insight-card.warning {
  border-left-color: #FBBF24;
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%);
}

.insight-card.error {
  border-left-color: #F87171;
  background: linear-gradient(135deg, rgba(248, 113, 113, 0.1) 0%, rgba(239, 68, 68, 0.1) 100%);
}

.insight-icon {
  font-size: 20px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
}

.success .insight-icon {
  background: rgba(52, 211, 153, 0.2);
  color: #34D399;
}

.info .insight-icon {
  background: rgba(96, 165, 250, 0.2);
  color: #60A5FA;
}

.warning .insight-icon {
  background: rgba(251, 191, 36, 0.2);
  color: #FBBF24;
}

.error .insight-icon {
  background: rgba(248, 113, 113, 0.2);
  color: #F87171;
}

.insight-content {
  flex: 1;
}

.insight-title {
  font-size: 14px;
  font-weight: 600;
  color: #F9FAFB;
  margin-bottom: 4px;
}

.insight-description {
  font-size: 13px;
  color: #D1D5DB;
  line-height: 1.5;
}

.recommendations {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: rgba(96, 165, 250, 0.1);
  border-radius: 12px;
  border-left: 4px solid #60A5FA;
}

.rec-number {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #60A5FA;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.rec-text {
  flex: 1;
  font-size: 14px;
  color: #93C5FD;
  line-height: 1.6;
}

@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .conversation-list-section,
  .conversation-detail-section {
    height: auto;
    max-height: 600px;
    overflow-y: auto;
  }
}

@media (max-width: 768px) {
  .conversation-analysis {
    padding: 16px;
  }
  
  .overview-stats {
    gap: 10px;
  }
  
  .stat-item {
    min-width: calc(50% - 10px);
    flex: 1;
  }
  
  .analysis-metrics {
    grid-template-columns: 1fr;
  }
  
  .turn-distribution {
    grid-template-columns: 1fr;
  }
  
  .turn-item.student,
  .turn-item.ai_tutor {
    margin: 0;
  }
}
</style>