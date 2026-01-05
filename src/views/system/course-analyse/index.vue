<template>
  <div class="page">
    <!-- 主题选择 -->
    <el-card class="card">
      <div class="header">
        <h2>📊 主题学习数据统计</h2>
        <el-select v-model="currentThemeId" style="width: 260px">
          <el-option
            v-for="theme in themes"
            :key="theme.id"
            :label="theme.name"
            :value="theme.id"
          />
        </el-select>
      </div>
      <p class="desc">{{ currentTheme?.description }}</p>
    </el-card>

    <!-- 核心指标 -->
    <el-row :gutter="16" class="metrics">
      <el-col :span="8">
        <el-card class="metric">
          <div class="value">{{ stats.learnerCount }}</div>
          <div class="label">学习人数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="metric">
          <div class="value">{{ percent(stats.avgMastery) }}</div>
          <div class="label">平均掌握度</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="metric">
          <div class="value">{{ percent(stats.completionRate) }}</div>
          <div class="label">完成率</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 用户画像 -->
    <el-card class="card">
      <h3>👤 用户画像分布</h3>
      <el-row :gutter="12">
        <el-col :span="8">
          <div class="tag bad">吃力型：{{ stats.userDistribution.Struggling }}</div>
        </el-col>
        <el-col :span="8">
          <div class="tag normal">正常型：{{ stats.userDistribution.Normal }}</div>
        </el-col>
        <el-col :span="8">
          <div class="tag good">进阶型：{{ stats.userDistribution.Advanced }}</div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 知识点 -->
    <el-card class="card">
      <h3>📘 知识点掌握情况</h3>
      <el-table :data="stats.topics" stripe>
        <el-table-column prop="name" label="知识点" />
        <el-table-column label="平均掌握度">
          <template #default="{ row }">
            <el-progress
              :percentage="Math.round(row.avgMastery * 100)"
              :stroke-width="12"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";

/* ===============================
   主题 mock 数据
================================ */
const themes = ref([
  {
    id: "7",
    name: "萌宠乐园",
    description: "以萌宠乐园为背景，完成宠物列表与互动页面"
  },
  {
    id: "8",
    name: "校园小助手",
    description: "围绕校园场景实现课程与信息管理页面"
  },
  {
    id: "9",
    name: "小店铺经营记",
    description: "通过小店铺场景理解数据联动与交互"
  },
  {
    id: "10",
    name: "数据星球",
    description: "学习数据可视化与统计分析页面设计"
  },
  {
    id: "11",
    name: "智能小管家",
    description: "用户管理与状态控制综合实践"
  }
]);

/* ===============================
   主题统计 mock 数据
================================ */
const themeStatsMap: any = {
  "7": {
    learnerCount: 120,
    avgMastery: 0.78,
    completionRate: 0.7,
    userDistribution: { Struggling: 17, Normal: 58, Advanced: 45 },
    topics: [
      { name: "基础布局", avgMastery: 0.75 },
      { name: "列表渲染", avgMastery: 0.8 },
      { name: "事件交互", avgMastery: 0.7 }
    ]
  },
  "8": {
    learnerCount: 95,
    avgMastery: 0.69,
    completionRate: 0.62,
    userDistribution: { Struggling: 22, Normal: 49, Advanced: 24 },
    topics: [
      { name: "表单处理", avgMastery: 0.66 },
      { name: "信息展示", avgMastery: 0.71 },
      { name: "简单交互", avgMastery: 0.68 }
    ]
  },
  "9": {
    learnerCount: 80,
    avgMastery: 0.73,
    completionRate: 0.67,
    userDistribution: { Struggling: 14, Normal: 41, Advanced: 25 },
    topics: [
      { name: "商品列表", avgMastery: 0.7 },
      { name: "状态管理", avgMastery: 0.74 },
      { name: "数据联动", avgMastery: 0.75 }
    ]
  },
  "10": {
    learnerCount: 110,
    avgMastery: 0.81,
    completionRate: 0.76,
    userDistribution: { Struggling: 10, Normal: 46, Advanced: 54 },
    topics: [
      { name: "数据结构", avgMastery: 0.79 },
      { name: "图表组件", avgMastery: 0.83 },
      { name: "统计分析", avgMastery: 0.81 }
    ]
  },
  "11": {
    learnerCount: 32,
    avgMastery: 0.46,
    completionRate: 0.38,
    userDistribution: { Struggling: 18, Normal: 10, Advanced: 4 },
    topics: [
      { name: "用户管理", avgMastery: 0.45 },
      { name: "状态控制", avgMastery: 0.48 },
      { name: "权限逻辑", avgMastery: 0.42 }
    ]
  }
};

/* ===============================
   状态控制
================================ */
const currentThemeId = ref("7");
const stats = ref(themeStatsMap[currentThemeId.value]);

watch(currentThemeId, (id) => {
  stats.value = themeStatsMap[id];
});

const currentTheme = computed(() =>
  themes.value.find((t) => t.id === currentThemeId.value)
);

const percent = (v: number) => `${Math.round(v * 100)}%`;
</script>

<style scoped>
.page {
  padding: 20px;
  background: #f5f7fa;
}
.card {
  margin-bottom: 16px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.desc {
  margin-top: 8px;
  color: #666;
}
.metrics .metric {
  text-align: center;
}
.metric .value {
  font-size: 32px;
  font-weight: bold;
}
.metric .label {
  color: #888;
  margin-top: 4px;
}
.tag {
  padding: 12px;
  border-radius: 6px;
  text-align: center;
  font-weight: 500;
}
.bad {
  background: #fde2e2;
  color: #c45656;
}
.normal {
  background: #fdf6ec;
  color: #e6a23c;
}
.good {
  background: #e1f3d8;
  color: #67c23a;
}
</style>
