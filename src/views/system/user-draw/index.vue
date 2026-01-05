<template>
  <div class="page">
    <h1 class="title">用户画像分析</h1>

    <div
      v-for="(user, index) in users"
      :key="user.participant_id"
      class="user-card"
    >
      <!-- 用户概要 -->
      <div class="user-summary">
        <div>
          <div class="user-id">{{ user.participant_id }}</div>
          <span class="tag" :class="user.progress_clustering.current_cluster">
            {{ user.progress_clustering.current_cluster }}
          </span>
        </div>

        <button class="btn" @click="toggle(index)">
          {{ expandedIndex === index ? '收起详情' : '查看详情' }}
        </button>
      </div>

      <!-- 详情 -->
      <div v-if="expandedIndex === index" class="user-detail">
        <!-- 情绪 -->
        <div class="section">
          <h3>情绪状态</h3>
          <div class="emotion">
            <span>情绪：{{ user.emotion_state.current_sentiment }}</span>
            <span>挫败感：{{ user.emotion_state.frustration_level }}</span>
            <span>参与度：{{ user.emotion_state.engagement_level }}</span>
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
              ></div>
            </div>

            <div class="percent">
              {{ (bkt.mastery_prob * 100).toFixed(0) }}%
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const expandedIndex = ref(null)

const toggle = (index) => {
  expandedIndex.value = expandedIndex.value === index ? null : index
}

const users = ref([
  {
    participant_id: 'user_001',
    progress_clustering: {
      current_cluster: 'Struggling'
    },
    emotion_state: {
      current_sentiment: 'NEGATIVE',
      frustration_level: 0.78,
      engagement_level: 0.32
    },
    bkt_models: {
      topic_01: { mastery_prob: 0.25 },
      topic_02: { mastery_prob: 0.18 },
      topic_03: { mastery_prob: 0.33 }
    }
  },
  {
    participant_id: 'user_002',
    progress_clustering: {
      current_cluster: 'Normal'
    },
    emotion_state: {
      current_sentiment: 'NEUTRAL',
      frustration_level: 0.42,
      engagement_level: 0.61
    },
    bkt_models: {
      topic_01: { mastery_prob: 0.54 },
      topic_02: { mastery_prob: 0.47 },
      topic_03: { mastery_prob: 0.59 }
    }
  },
  {
    participant_id: 'user_003',
    progress_clustering: {
      current_cluster: 'Advanced'
    },
    emotion_state: {
      current_sentiment: 'POSITIVE',
      frustration_level: 0.12,
      engagement_level: 0.88
    },
    bkt_models: {
      topic_01: { mastery_prob: 0.86 },
      topic_02: { mastery_prob: 0.81 },
      topic_03: { mastery_prob: 0.92 }
    }
  },
  {
    participant_id: 'user_004',
    progress_clustering: {
      current_cluster: 'Struggling'
    },
    emotion_state: {
      current_sentiment: 'NEGATIVE',
      frustration_level: 0.69,
      engagement_level: 0.41
    },
    bkt_models: {
      topic_01: { mastery_prob: 0.31 },
      topic_02: { mastery_prob: 0.27 },
      topic_03: { mastery_prob: 0.38 }
    }
  },
  {
    participant_id: 'user_005',
    progress_clustering: {
      current_cluster: 'Normal'
    },
    emotion_state: {
      current_sentiment: 'POSITIVE',
      frustration_level: 0.21,
      engagement_level: 0.74
    },
    bkt_models: {
      topic_01: { mastery_prob: 0.63 },
      topic_02: { mastery_prob: 0.58 },
      topic_03: { mastery_prob: 0.67 }
    }
  },
  {
    participant_id: 'user_006',
    progress_clustering: {
      current_cluster: 'Advanced'
    },
    emotion_state: {
      current_sentiment: 'POSITIVE',
      frustration_level: 0.08,
      engagement_level: 0.93
    },
    bkt_models: {
      topic_01: { mastery_prob: 0.91 },
      topic_02: { mastery_prob: 0.87 },
      topic_03: { mastery_prob: 0.95 }
    }
  }
])
</script>

<style scoped>
.page {
  padding: 24px;
  background: #f5f7fb;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

.user-card {
  background: white;
  border-radius: 10px;
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
}

.tag {
  display: inline-block;
  margin-top: 6px;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  color: white;
}

.tag.Struggling {
  background: #e74c3c;
}
.tag.Normal {
  background: #f39c12;
}
.tag.Advanced {
  background: #2ecc71;
}

.btn {
  background: #409eff;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
}

.btn:hover {
  opacity: 0.9;
}

.user-detail {
  margin-top: 16px;
  border-top: 1px solid #eee;
  padding-top: 16px;
}

.section {
  margin-bottom: 16px;
}

.emotion span {
  margin-right: 16px;
  color: #555;
}

.topic-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.topic-name {
  width: 80px;
  font-size: 14px;
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
}

.percent {
  width: 50px;
  font-size: 13px;
  text-align: right;
}
</style>
