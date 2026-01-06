<template>
  <div class="page">
    <div class="header">
      <h1 class="title">用户画像分析</h1>
      <el-button type="primary" @click="showChartDialog = true">
        查看可视化图表
      </el-button>
    </div>

    <el-empty v-if="users.length === 0" description="暂无用户数据" />

    <div
      v-for="(user, index) in users"
      :key="user.participant_id"
      class="user-card"
    >
      <!-- 用户概要 -->
      <div class="user-summary">
        <div>
          <div class="user-id">{{ user.participant_id }}</div>
          <el-tag
            :type="clusterMap[user.progress_clustering.current_cluster].type"
            size="small"
          >
            {{ clusterMap[user.progress_clustering.current_cluster].label }}
          </el-tag>
        </div>

        <el-button
          size="small"
          type="primary"
          plain
          @click="toggleDetail(index)"
        >
          {{ expandedUserIndex === index ? '收起详情' : '查看详情' }}
        </el-button>
      </div>

      <!-- 详情 -->
      <transition name="fade">
        <div v-if="expandedUserIndex === index" class="user-detail">
          <!-- 情绪状态 -->
          <div class="section">
            <h3>情绪状态</h3>
            <div class="emotion">
              <el-tag :type="emotionType(user.emotion_state.current_sentiment)">
                {{ user.emotion_state.current_sentiment }}
              </el-tag>
              <span>挫败感：{{ percent(user.emotion_state.frustration_level) }}</span>
              <span>参与度：{{ percent(user.emotion_state.engagement_level) }}</span>
            </div>
          </div>

          <!-- 知识点 -->
          <div class="section">
            <h3>知识点掌握情况</h3>

            <div
              v-for="(bkt, topic) in user.bkt_models"
              :key="topic"
              class="topic-row"
            >
              <div class="topic-name">{{ topic }}</div>

              <div class="progress">
                <div
                  class="progress-bar"
                  :style="{ width: bkt.mastery_prob * 100 + '%' }"
                />
              </div>

              <div class="percent">
                {{ percent(bkt.mastery_prob) }}
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- 图表弹窗 -->
    <el-dialog
      v-model="showChartDialog"
      title="用户画像可视化图表"
      width="70%"
      align-center
    >
      <div class="chart-container">
        <img
          src="./bkt_data_visualization.png"
          class="chart-image"
          @error="handleImageError"
        />
        <img
          src="./learning_trajectories.png"
          class="chart-image"
          @error="handleImageError"
        />
      </div>

      <template #footer>
        <el-button @click="showChartDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const expandedUserIndex = ref(null)
const showChartDialog = ref(false)

const toggleDetail = (index) => {
  expandedUserIndex.value =
    expandedUserIndex.value === index ? null : index
}

const percent = (value) => `${Math.round(value * 100)}%`

const emotionType = (emotion) => {
  if (emotion === 'POSITIVE') return 'success'
  if (emotion === 'NEGATIVE') return 'danger'
  return 'info'
}

const handleImageError = () => {
  ElMessage.error('图表加载失败，请检查图片路径')
}

const clusterMap = {
  Struggling: { label: '学习困难', type: 'danger' },
  Normal: { label: '正常学习', type: 'warning' },
  Advanced: { label: '进阶学习', type: 'success' }
}

const users = ref([
  {
    participant_id: 'user_001',
    progress_clustering: { current_cluster: 'Struggling' },
    emotion_state: {
      current_sentiment: 'NEGATIVE',
      frustration_level: 0.78,
      engagement_level: 0.32
    },
    bkt_models: {
      topic_01: { mastery_prob: 0.22 },
      topic_02: { mastery_prob: 0.18 },
      topic_03: { mastery_prob: 0.25 },
      topic_04: { mastery_prob: 0.20 },
      topic_05: { mastery_prob: 0.27 },
      topic_06: { mastery_prob: 0.19 },
      topic_07: { mastery_prob: 0.31 },
      topic_08: { mastery_prob: 0.24 },
      topic_09: { mastery_prob: 0.29 },
      topic_10: { mastery_prob: 0.26 }
    }
  },
  {
    participant_id: 'user_002',
    progress_clustering: { current_cluster: 'Normal' },
    emotion_state: {
      current_sentiment: 'NEUTRAL',
      frustration_level: 0.42,
      engagement_level: 0.61
    },
    bkt_models: {
      topic_01: { mastery_prob: 0.48 },
      topic_02: { mastery_prob: 0.52 },
      topic_03: { mastery_prob: 0.46 },
      topic_04: { mastery_prob: 0.55 },
      topic_05: { mastery_prob: 0.51 },
      topic_06: { mastery_prob: 0.49 },
      topic_07: { mastery_prob: 0.57 },
      topic_08: { mastery_prob: 0.53 },
      topic_09: { mastery_prob: 0.59 },
      topic_10: { mastery_prob: 0.56 }
    }
  },
  {
    participant_id: 'user_003',
    progress_clustering: { current_cluster: 'Advanced' },
    emotion_state: {
      current_sentiment: 'POSITIVE',
      frustration_level: 0.12,
      engagement_level: 0.88
    },
    bkt_models: {
      topic_01: { mastery_prob: 0.82 },
      topic_02: { mastery_prob: 0.85 },
      topic_03: { mastery_prob: 0.88 },
      topic_04: { mastery_prob: 0.81 },
      topic_05: { mastery_prob: 0.86 },
      topic_06: { mastery_prob: 0.90 },
      topic_07: { mastery_prob: 0.84 },
      topic_08: { mastery_prob: 0.89 },
      topic_09: { mastery_prob: 0.92 },
      topic_10: { mastery_prob: 0.87 }
    }
  },
  {
    participant_id: 'user_004',
    progress_clustering: { current_cluster: 'Struggling' },
    emotion_state: {
      current_sentiment: 'NEGATIVE',
      frustration_level: 0.69,
      engagement_level: 0.41
    },
    bkt_models: {
      topic_01: { mastery_prob: 0.31 },
      topic_02: { mastery_prob: 0.27 },
      topic_03: { mastery_prob: 0.38 },
      topic_04: { mastery_prob: 0.29 },
      topic_05: { mastery_prob: 0.35 },
      topic_06: { mastery_prob: 0.26 },
      topic_07: { mastery_prob: 0.41 },
      topic_08: { mastery_prob: 0.33 },
      topic_09: { mastery_prob: 0.37 },
      topic_10: { mastery_prob: 0.34 }
    }
  },
  {
    participant_id: 'user_005',
    progress_clustering: { current_cluster: 'Normal' },
    emotion_state: {
      current_sentiment: 'POSITIVE',
      frustration_level: 0.21,
      engagement_level: 0.74
    },
    bkt_models: {
      topic_01: { mastery_prob: 0.63 },
      topic_02: { mastery_prob: 0.58 },
      topic_03: { mastery_prob: 0.67 },
      topic_04: { mastery_prob: 0.61 },
      topic_05: { mastery_prob: 0.69 },
      topic_06: { mastery_prob: 0.60 },
      topic_07: { mastery_prob: 0.72 },
      topic_08: { mastery_prob: 0.65 },
      topic_09: { mastery_prob: 0.75 },
      topic_10: { mastery_prob: 0.68 }
    }
  }
])


</script>

<style scoped>
.page {
  padding: 24px;
  background: #f5f7fb;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title {
  font-size: 24px;
  font-weight: bold;
}

.user-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.user-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-id {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 6px;
}

.user-detail {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.section {
  margin-bottom: 16px;
}

.emotion {
  display: flex;
  gap: 12px;
  align-items: center;
}

.topic-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.topic-name {
  width: 90px;
}

.progress {
  flex: 1;
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
  margin: 0 10px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #66b1ff);
  transition: width 0.4s ease;
}

.percent {
  width: 50px;
  text-align: right;
}

.chart-container {
  text-align: center;
}

.chart-image {
  max-width: 100%;
  margin-bottom: 16px;
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
