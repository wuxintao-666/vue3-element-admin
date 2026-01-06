<template>
  <el-container style="height: 100vh; overflow: hidden;">
    <!-- 左侧主题列表 -->
    <el-aside width="280px" class="aside-container">
      <div class="aside-header">
        <h2 class="aside-title">测试报告</h2>
        <div class="aside-subtitle">查看各主题测试统计</div>
      </div>
      <el-scrollbar class="theme-scrollbar">
        <el-menu
          :default-active="activeThemeId"
          @select="selectTheme"
          class="theme-menu"
          background-color="transparent"
          text-color="#5a5a5a"
          active-text-color="#fff"
        >
          <el-menu-item
            v-for="theme in themes"
            :key="theme.id"
            :index="theme.id"
            class="theme-menu-item"
            :class="{ 'active-theme': activeThemeId === theme.id }"
          >
            <div class="theme-item">
              <div class="theme-header">
                <div class="theme-icon">
                  <span v-if="themeAccuracy(theme) >= 90"></span>
                  <span v-else-if="themeAccuracy(theme) >= 70"></span>
                  <span v-else></span>
                </div>
                <div class="theme-info">
                  <div class="theme-name">{{ theme.name }}</div>
                  <div class="theme-progress">
                    <el-progress
                      :stroke-width="6"
                      :percentage="themeAccuracy(theme)"
                      :show-text="false"
                      :color="getAccuracyColor(themeAccuracy(theme))"
                    />
                  </div>
                </div>
              </div>
              <div class="theme-stats">
                <div class="stat-item">
                  <span class="stat-label">准确率</span>
                  <span class="stat-value" :style="{ color: getAccuracyColor(themeAccuracy(theme)) }">
                    {{ themeAccuracy(theme) }}%
                  </span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">错误数</span>
                  <span class="stat-value error">{{ themeTotalErrors(theme) }}</span>
                </div>
              </div>
            </div>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- 右侧内容区域 -->
    <el-main class="main-container" v-if="activeTheme">
      <!-- 顶部标题栏 -->
      <div class="main-header">
        <div class="theme-header-info">
          <div class="theme-header-left">
            <h1 class="active-theme-name">
              <span class="theme-emoji"></span>
              {{ activeTheme.name }} 测试报告
            </h1>
            <div class="theme-meta">
              <span class="meta-item">主题ID: {{ activeTheme.id }}</span>
              <span class="meta-item">测试小节: {{ activeThemeSections.length }}个</span>
              <span class="meta-item">测试点: {{ activeThemeCheckpoints }}个</span>
            </div>
          </div>
          <div class="theme-status">
            <el-tag :type="getAccuracyTagType(themeAccuracy(activeTheme))" size="large">
              主题准确率: {{ themeAccuracy(activeTheme) }}%
            </el-tag>
            <el-tag type="info" style="margin-left: 10px;">
              总提交次数: {{ formatNumber(totalSubmissions) }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 主题总览 -->
      <el-row :gutter="20" class="overview-row">
        <el-col :xs="24" :sm="12" :md="6" v-for="stat in themeOverviewStats" :key="stat.title">
          <el-card class="overview-card" :style="{ 'border-left': `4px solid ${stat.color}` }" shadow="hover">
            <div class="overview-content">
              <div class="overview-icon" :style="{ backgroundColor: `${stat.color}15` }">
                <span :style="{ color: stat.color }">{{ stat.icon }}</span>
              </div>
              <div class="overview-text">
                <div class="overview-title">{{ stat.title }}</div>
                <div class="overview-value" :style="{ color: stat.color }">
                  {{ stat.value }}
                  <span v-if="stat.unit" class="overview-unit">{{ stat.unit }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 错误分析 -->
      <div class="error-analysis">
        <h3>📉 错误分析</h3>
        <div class="analysis-cards">
          <el-card class="analysis-card">
            <div class="analysis-title">最高错误率测试点</div>
            <div class="analysis-content">
              <div v-if="topErrorCheckpoint" class="top-error-item">
                <div class="error-point-name">{{ topErrorCheckpoint.name }}</div>
                <div class="error-stats">
                  <div class="error-rate">
                    <span class="rate-label">错误率</span>
                    <span class="rate-value error">{{ topErrorCheckpoint.errorRate }}%</span>
                  </div>
                  <div class="error-count">
                    <span class="count-label">错误数</span>
                    <span class="count-value">{{ topErrorCheckpoint.errorCount }}/{{ topErrorCheckpoint.totalSubmissions }}</span>
                  </div>
                </div>
                <div class="error-section">所属小节: {{ topErrorCheckpoint.sectionTitle }}</div>
              </div>
              <div v-else class="no-error">
                暂无错误数据
              </div>
            </div>
          </el-card>
          
          <el-card class="analysis-card">
            <div class="analysis-title">整体通过情况</div>
            <div class="analysis-content">
              <div class="pass-distribution">
                <div class="distribution-item success">
                  <div class="dist-label">优秀通过率 (≥90%)</div>
                  <div class="dist-value">{{ excellentCheckpoints }}个</div>
                </div>
                <div class="distribution-item warning">
                  <div class="dist-label">良好通过率 (70-89%)</div>
                  <div class="dist-value">{{ goodCheckpoints }}个</div>
                </div>
                <div class="distribution-item danger">
                  <div class="dist-label">需关注 (<70%)</div>
                  <div class="dist-value">{{ poorCheckpoints }}个</div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 小节详情 -->
      <div class="sections-container">
        <div class="sections-header">
          <h3>📋 小节详情</h3>
          <div class="sections-meta">
            <span class="meta-item">共 {{ activeThemeSections.length }} 个小节</span>
            <span class="meta-item">平均准确率: {{ themeAverageAccuracy }}%</span>
          </div>
        </div>
        
        <el-scrollbar class="sections-scrollbar">
          <div class="section-list">
            <div
              v-for="section in activeThemeSections"
              :key="section.topic_id"
              class="section-card"
              :class="getSectionCardClass(section)"
            >
              <div class="section-header">
                <div class="section-title">
                  <div class="section-icon">
                    <span v-if="sectionAccuracy(section) >= 90">✅</span>
                    <span v-else-if="sectionAccuracy(section) >= 70">⚠️</span>
                    <span v-else>❌</span>
                  </div>
                  <div>
                    <div class="section-name">{{ section.title }}</div>
                    <div class="section-id">ID: {{ section.topic_id }}</div>
                  </div>
                </div>
                <div class="section-stats">
                  <div class="section-stat-item">
                    <div class="stat-label">准确率</div>
                    <div class="stat-value" :style="{ color: getAccuracyColor(sectionAccuracy(section)) }">
                      {{ sectionAccuracy(section) }}%
                    </div>
                  </div>
                  <div class="section-stat-item">
                    <div class="stat-label">测试点</div>
                    <div class="stat-value">{{ section.results.length }}个</div>
                  </div>
                  <div class="section-stat-item">
                    <div class="stat-label">总错误</div>
                    <div class="stat-value error">{{ sectionTotalErrors(section) }}</div>
                  </div>
                </div>
              </div>
              
              <el-divider />
              
              <div class="checkpoints-list">
                <div class="checkpoints-header">
                  <span class="checkpoints-title">测试点详情</span>
                  <span class="checkpoints-summary">
                    共 {{ section.results.length }} 个测试点，
                    <span class="error-text">错误: {{ sectionTotalErrors(section) }}次</span>
                  </span>
                </div>
                
                <div class="checkpoints-table">
                  <div class="table-header">
                    <div class="header-cell">测试点名称</div>
                    <div class="header-cell">总提交次数</div>
                    <div class="header-cell">错误次数</div>
                    <div class="header-cell">准确率</div>
                    <div class="header-cell">状态</div>
                  </div>
                  
                  <div
                    v-for="checkpoint in section.results"
                    :key="checkpoint.id"
                    class="table-row"
                    :class="{ 'row-error': checkpoint.errorRate >= 30 }"
                  >
                    <div class="row-cell">
                      <div class="checkpoint-name">{{ checkpoint.name }}</div>
                      <div class="checkpoint-desc">{{ checkpoint.description }}</div>
                    </div>
                    <div class="row-cell">
                      <div class="cell-value">{{ formatNumber(checkpoint.totalSubmissions) }}</div>
                    </div>
                    <div class="row-cell">
                      <div class="cell-value error">{{ checkpoint.errorCount }}</div>
                      <div class="cell-subtext">
                        错误率: {{ checkpoint.errorRate }}%
                      </div>
                    </div>
                    <div class="row-cell">
                      <div class="cell-value" :style="{ color: getAccuracyColor(checkpoint.accuracy) }">
                        {{ checkpoint.accuracy }}%
                      </div>
                      <el-progress
                        :percentage="checkpoint.accuracy"
                        :stroke-width="6"
                        :show-text="false"
                        :color="getAccuracyColor(checkpoint.accuracy)"
                      />
                    </div>
                    <div class="row-cell">
                      <el-tag
                        :type="getCheckpointStatusType(checkpoint)"
                        size="small"
                      >
                        {{ getCheckpointStatusText(checkpoint) }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </el-main>

    <el-main v-else class="no-theme">
      <div class="empty-state">
        <div class="empty-icon">📊</div>
        <h2>选择测试主题</h2>
        <p>请在左侧选择一个主题来查看详细的测试报告</p>
      </div>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue';

// -----------------------------
// 模拟数据 - 重构后
// -----------------------------

// 总提交次数统计（假设每个测试点的总提交次数相同）
const totalSubmissions = 234; // 总共有234次提交

// 主题数据
const themes = [
  { id: '7', name: '萌宠乐园' },
  { id: '8', name: '校园小助手' },
  { id: '9', name: '小店铺经营记' }
];

// 小节和测试点数据（包含统计信息）
const sections = [
  {
    topic_id: '7_1',
    theme_id: '7',
    title: 'HTML基础标签',
    results: [
      { 
        id: '7_1_1',
        name: 'h1标题标签', 
        description: '检查是否使用了h1标签',
        totalSubmissions: totalSubmissions, // 总提交次数
        errorCount: 12, // 错误次数（12个学生错了）
        // 计算属性
        get accuracy() {
          return Math.round((1 - this.errorCount / this.totalSubmissions) * 100);
        },
        get errorRate() {
          return Math.round((this.errorCount / this.totalSubmissions) * 100);
        }
      },
      { 
        id: '7_1_2',
        name: 'p段落标签', 
        description: '检查是否使用了p标签',
        totalSubmissions: totalSubmissions,
        errorCount: 8,
        get accuracy() {
          return Math.round((1 - this.errorCount / this.totalSubmissions) * 100);
        },
        get errorRate() {
          return Math.round((this.errorCount / this.totalSubmissions) * 100);
        }
      },
      { 
        id: '7_1_3',
        name: 'class属性', 
        description: '检查是否设置了正确的class',
        totalSubmissions: totalSubmissions,
        errorCount: 45, // 错误率较高
        get accuracy() {
          return Math.round((1 - this.errorCount / this.totalSubmissions) * 100);
        },
        get errorRate() {
          return Math.round((this.errorCount / this.totalSubmissions) * 100);
        }
      }
    ]
  },
  {
    topic_id: '7_2',
    theme_id: '7',
    title: '图片和链接',
    results: [
      { 
        id: '7_2_1',
        name: 'img图片标签', 
        description: '检查是否使用了img标签',
        totalSubmissions: totalSubmissions,
        errorCount: 5,
        get accuracy() {
          return Math.round((1 - this.errorCount / this.totalSubmissions) * 100);
        },
        get errorRate() {
          return Math.round((this.errorCount / this.totalSubmissions) * 100);
        }
      },
      { 
        id: '7_2_2',
        name: 'a链接标签', 
        description: '检查是否使用了a标签',
        totalSubmissions: totalSubmissions,
        errorCount: 25,
        get accuracy() {
          return Math.round((1 - this.errorCount / this.totalSubmissions) * 100);
        },
        get errorRate() {
          return Math.round((this.errorCount / this.totalSubmissions) * 100);
        }
      }
    ]
  },
  {
    topic_id: '8_1',
    theme_id: '8',
    title: '表单元素',
    results: [
      { 
        id: '8_1_1',
        name: 'form表单标签', 
        description: '检查是否使用了form标签',
        totalSubmissions: totalSubmissions,
        errorCount: 3,
        get accuracy() {
          return Math.round((1 - this.errorCount / this.totalSubmissions) * 100);
        },
        get errorRate() {
          return Math.round((this.errorCount / this.totalSubmissions) * 100);
        }
      },
      { 
        id: '8_1_2',
        name: 'input输入框', 
        description: '检查是否使用了input标签',
        totalSubmissions: totalSubmissions,
        errorCount: 7,
        get accuracy() {
          return Math.round((1 - this.errorCount / this.totalSubmissions) * 100);
        },
        get errorRate() {
          return Math.round((this.errorCount / this.totalSubmissions) * 100);
        }
      }
    ]
  },
  {
    topic_id: '9_1',
    theme_id: '9',
    title: '列表元素',
    results: [
      { 
        id: '9_1_1',
        name: 'ul无序列表', 
        description: '检查是否使用了ul标签',
        totalSubmissions: totalSubmissions,
        errorCount: 2,
        get accuracy() {
          return Math.round((1 - this.errorCount / this.totalSubmissions) * 100);
        },
        get errorRate() {
          return Math.round((this.errorCount / this.totalSubmissions) * 100);
        }
      },
      { 
        id: '9_1_2',
        name: 'li列表项', 
        description: '检查是否使用了li标签',
        totalSubmissions: totalSubmissions,
        errorCount: 4,
        get accuracy() {
          return Math.round((1 - this.errorCount / this.totalSubmissions) * 100);
        },
        get errorRate() {
          return Math.round((this.errorCount / this.totalSubmissions) * 100);
        }
      }
    ]
  }
];

const activeThemeId = ref(themes[0].id);

// -----------------------------
// 计算属性
// -----------------------------
const activeTheme = computed(() => themes.find(t => t.id === activeThemeId.value));
const activeThemeSections = computed(() =>
  sections.filter(s => s.theme_id === activeThemeId.value)
);
const activeThemeCheckpoints = computed(() =>
  activeThemeSections.value.reduce((total, section) => total + section.results.length, 0)
);

// 小节准确率计算
const sectionAccuracy = (section) => {
  if (!section.results?.length) return 0;
  const totalAccuracy = section.results.reduce((sum, checkpoint) => sum + checkpoint.accuracy, 0);
  return Math.round(totalAccuracy / section.results.length);
};

// 小节总错误数
const sectionTotalErrors = (section) => {
  return section.results?.reduce((sum, checkpoint) => sum + checkpoint.errorCount, 0) || 0;
};

// 主题准确率计算
const themeAccuracy = (theme) => {
  const themeSections = sections.filter(s => s.theme_id === theme.id);
  if (!themeSections.length) return 0;
  const totalAccuracy = themeSections.reduce((sum, section) => sum + sectionAccuracy(section), 0);
  return Math.round(totalAccuracy / themeSections.length);
};

// 主题总错误数
const themeTotalErrors = (theme) => {
  const themeSections = sections.filter(s => s.theme_id === theme.id);
  return themeSections.reduce((sum, section) => sum + sectionTotalErrors(section), 0);
};

// 主题平均准确率
const themeAverageAccuracy = computed(() => themeAccuracy(activeTheme.value));

// 获取准确率颜色
const getAccuracyColor = (accuracy) => {
  if (accuracy >= 90) return '#67C23A';
  if (accuracy >= 70) return '#E6A23C';
  return '#F56C6C';
};

// 获取准确率标签类型
const getAccuracyTagType = (accuracy) => {
  if (accuracy >= 90) return 'success';
  if (accuracy >= 70) return 'warning';
  return 'danger';
};

// 获取测试点状态类型
const getCheckpointStatusType = (checkpoint) => {
  if (checkpoint.accuracy >= 90) return 'success';
  if (checkpoint.accuracy >= 70) return 'warning';
  return 'danger';
};

// 获取测试点状态文本
const getCheckpointStatusText = (checkpoint) => {
  if (checkpoint.accuracy >= 90) return '优秀';
  if (checkpoint.accuracy >= 70) return '良好';
  return '需关注';
};

// 获取小节卡片类名
const getSectionCardClass = (section) => {
  const accuracy = sectionAccuracy(section);
  if (accuracy >= 90) return 'section-excellent';
  if (accuracy >= 70) return 'section-good';
  return 'section-poor';
};

// 格式化数字
const formatNumber = (num) => {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

// 主题总览统计
const themeOverviewStats = computed(() => {
  const theme = activeTheme.value;
  if (!theme) return [];
  
  const accuracy = themeAccuracy(theme);
  const totalErrors = themeTotalErrors(theme);
  const totalCheckpoints = activeThemeCheckpoints.value;
  
  return [
    { title: '主题准确率', value: accuracy, icon: '📈', color: getAccuracyColor(accuracy), unit: '%' },
    { title: '小节数量', value: activeThemeSections.value.length, icon: '📚', color: '#409EFF' },
    { title: '测试点数量', value: totalCheckpoints, icon: '✅', color: '#67C23A' },
    { title: '总错误次数', value: totalErrors, icon: '⚠️', color: '#F56C6C' }
  ];
});

// 错误率最高的测试点
const topErrorCheckpoint = computed(() => {
  let maxErrorRate = 0;
  let topCheckpoint = null;
  
  activeThemeSections.value.forEach(section => {
    section.results.forEach(checkpoint => {
      if (checkpoint.errorRate > maxErrorRate) {
        maxErrorRate = checkpoint.errorRate;
        topCheckpoint = {
          ...checkpoint,
          sectionTitle: section.title
        };
      }
    });
  });
  
  return topCheckpoint;
});

// 测试点通过率分布
const excellentCheckpoints = computed(() => {
  let count = 0;
  activeThemeSections.value.forEach(section => {
    count += section.results.filter(c => c.accuracy >= 90).length;
  });
  return count;
});

const goodCheckpoints = computed(() => {
  let count = 0;
  activeThemeSections.value.forEach(section => {
    count += section.results.filter(c => c.accuracy >= 70 && c.accuracy < 90).length;
  });
  return count;
});

const poorCheckpoints = computed(() => {
  let count = 0;
  activeThemeSections.value.forEach(section => {
    count += section.results.filter(c => c.accuracy < 70).length;
  });
  return count;
});

// 方法
const selectTheme = (id) => (activeThemeId.value = id);
</script>

<style scoped>
/* 左侧边栏样式 */
.aside-container {
  background: linear-gradient(135deg, #304156 0%, #34495e 100%);
  color: white;
}

.aside-header {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.aside-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: white;
}

.aside-subtitle {
  font-size: 12px;
  opacity: 0.8;
}

.theme-scrollbar {
  height: calc(100vh - 100px);
}

.theme-menu {
  border: none;
}

.theme-menu-item {
  height: auto !important;
  padding: 16px 20px !important;
  margin: 8px 12px;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.08) !important;
}

.theme-menu-item:hover {
  background: rgba(255, 255, 255, 0.12) !important;
  transform: translateX(4px);
}

.active-theme {
  background: rgba(255, 255, 255, 0.15) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border-left: 4px solid #409EFF;
}

.theme-item {
  width: 100%;
}

.theme-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.theme-icon {
  font-size: 24px;
}

.theme-info {
  flex: 1;
  min-width: 0;
}

.theme-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.theme-progress {
  margin-top: 4px;
}

.theme-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  padding: 8px 12px;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 10px;
  opacity: 0.7;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
}

.stat-value.error {
  color: #ff7875;
}

/* 主内容区样式 */
.main-container {
  padding: 0;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
}

.main-header {
  padding: 24px 32px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.theme-header-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.theme-header-left {
  flex: 1;
}

.active-theme-name {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #1f2937;
}

.theme-emoji {
  font-size: 28px;
}

.theme-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  font-size: 14px;
  color: #6b7280;
}

.theme-status {
  display: flex;
  gap: 10px;
}

/* 总览卡片样式 */
.overview-row {
  padding: 24px 32px 0 32px;
}

.overview-card {
  border: none;
  border-radius: 12px;
  margin-bottom: 24px;
  background: white;
  transition: transform 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-4px);
}

.overview-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.overview-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.overview-text {
  flex: 1;
}

.overview-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.overview-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.overview-unit {
  font-size: 16px;
  margin-left: 2px;
  opacity: 0.8;
}

/* 错误分析样式 */
.error-analysis {
  padding: 0 32px;
  margin-top: 20px;
}

.error-analysis h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #1f2937;
}

.analysis-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.analysis-card {
  border: none;
  border-radius: 12px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.analysis-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

.top-error-item {
  padding: 12px;
  background: #fff2f0;
  border-radius: 8px;
  border-left: 4px solid #ff4d4f;
}

.error-point-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
}

.error-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.error-rate, .error-count {
  display: flex;
  flex-direction: column;
}

.rate-label, .count-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.rate-value.error {
  font-size: 20px;
  font-weight: 700;
  color: #ff4d4f;
}

.count-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.error-section {
  font-size: 14px;
  color: #6b7280;
}

.no-error {
  padding: 24px;
  text-align: center;
  color: #6b7280;
}

.pass-distribution {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.distribution-item {
  padding: 12px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.distribution-item.success {
  background: #f6ffed;
  border-left: 4px solid #52c41a;
}

.distribution-item.warning {
  background: #fff7e6;
  border-left: 4px solid #fa8c16;
}

.distribution-item.danger {
  background: #fff2f0;
  border-left: 4px solid #ff4d4f;
}

.dist-label {
  font-size: 14px;
  color: #1f2937;
}

.dist-value {
  font-size: 18px;
  font-weight: 700;
}

/* 小节容器样式 */
.sections-container {
  flex: 1;
  padding: 0 32px 32px;
  display: flex;
  flex-direction: column;
}

.sections-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 24px 0 20px 0;
  padding-top: 8px;
}

.sections-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}

.sections-meta {
  display: flex;
  gap: 16px;
  color: #6b7280;
  font-size: 14px;
}

.sections-scrollbar {
  flex: 1;
}

.section-list {
  display: grid;
  gap: 20px;
  padding-right: 8px;
}

.section-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border: 1px solid #e5e7eb;
}

.section-excellent {
  border-color: #52c41a;
  background: linear-gradient(135deg, #f6ffed 0%, #f0fff3 100%);
}

.section-good {
  border-color: #fa8c16;
  background: linear-gradient(135deg, #fff7e6 0%, #fffaf0 100%);
}

.section-poor {
  border-color: #ff4d4f;
  background: linear-gradient(135deg, #fff2f0 0%, #fffaf0 100%);
}

.section-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.section-icon {
  font-size: 32px;
}

.section-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.section-id {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

.section-stats {
  display: flex;
  align-items: center;
  gap: 24px;
}

.section-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.section-stat-item .stat-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.section-stat-item .stat-value {
  font-size: 20px;
  font-weight: 700;
}

.checkpoints-list {
  margin-top: 16px;
}

.checkpoints-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.checkpoints-title {
  font-weight: 600;
  color: #374151;
  font-size: 16px;
}

.checkpoints-summary {
  font-size: 14px;
  color: #6b7280;
}

.error-text {
  color: #ff4d4f;
  font-weight: 600;
}

/* 测试点表格样式 */
.checkpoints-table {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  background: #f9fafb;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.header-cell {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  transition: background-color 0.2s;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: #f9fafb;
}

.row-error {
  background: #fff2f0;
}

.row-error:hover {
  background: #ffe7e5;
}

.row-cell {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 8px;
}

.checkpoint-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.checkpoint-desc {
  font-size: 12px;
  color: #6b7280;
}

.cell-value {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.cell-value.error {
  color: #ff4d4f;
}

.cell-subtext {
  font-size: 12px;
  color: #6b7280;
}

/* 空状态样式 */
.no-theme {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
}

.empty-state {
  text-align: center;
  padding: 48px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.empty-state h2 {
  font-size: 24px;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.empty-state p {
  color: #6b7280;
  margin: 0;
}
.el-tag{
  height: 20px;
}
/* 响应式调整 */
@media (max-width: 768px) {
  .aside-container {
    width: 240px !important;
  }
  
  .overview-row {
    padding: 16px;
  }
  
  .main-header,
  .sections-container,
  .error-analysis {
    padding-left: 16px;
    padding-right: 16px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .section-stats {
    width: 100%;
    justify-content: space-between;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}

:deep(.el-scrollbar__wrap) {
  scrollbar-width: thin;
}

:deep(.el-scrollbar__thumb) {
  background-color: rgba(255, 255, 255, 0.3);
}

:deep(.el-divider) {
  margin: 16px 0;
}
</style>