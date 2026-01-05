<template>
  <el-container style="height: 100vh;">
    <!-- 左侧主题列表 -->
    <el-aside width="220px" class="aside-container">
      <el-menu
        :default-active="activeThemeId"
        @select="selectTheme"
        class="theme-menu"
        background-color="#fafafa"
        text-color="#333"
        active-text-color="#409EFF"
      >
        <el-menu-item
          v-for="theme in themes"
          :key="theme.id"
          :index="theme.id"
        >
          {{ theme.name }}
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧小节与代码 -->
    <el-main class="main-container">
      <div v-if="activeTheme">
        <el-tabs v-model="activeSectionId" type="card" stretch>
          <el-tab-pane
            v-for="section in activeThemeSections"
            :key="section.topic_id"
            :label="section.title"
            :name="section.topic_id"
          >
            <div class="section-card">
              <!-- 小节顶部操作栏 -->
              <div class="section-header">
                <span class="section-title">{{ section.title }}</span>
                <el-button
                  size="mini"
                  type="primary"
                  icon="el-icon-edit"
                  @click="openEditDialog(section)"
                >
                编辑        
                </el-button>
              </div>

              <!-- Markdown题目 -->
              <el-card shadow="hover" class="section-md-card">
                <div v-html="renderMarkdown(section.description_md)"></div>
              </el-card>

              <!-- 代码编辑器 -->
              <el-card shadow="hover" class="section-code-card">
                <el-tabs v-model="activeCodeTab" type="border-card">
                  <el-tab-pane label="HTML" name="html">
                    <el-input
                      type="textarea"
                      :rows="12"
                      v-model="section.start_code.html"
                    />
                  </el-tab-pane>
                  <el-tab-pane label="CSS" name="css">
                    <el-input
                      type="textarea"
                      :rows="12"
                      v-model="section.start_code.css"
                    />
                  </el-tab-pane>
                  <el-tab-pane label="JS" name="js">
                    <el-input
                      type="textarea"
                      :rows="12"
                      v-model="section.start_code.js"
                    />
                  </el-tab-pane>
                </el-tabs>
              </el-card>

              <!-- 提交按钮 -->
              <div class="run-button-wrapper">
                <el-button type="success" @click="runCheckpoints(section)">
                  运行测试
                </el-button>
              </div>

              <!-- 测试结果 -->
              <el-card v-if="section.results" class="results-card">
                <div
                  v-for="res in section.results"
                  :key="res.name"
                  :class="res.success ? 'result-success' : 'result-fail'"
                >
                  {{ res.success ? '✅' : '❌' }} {{ res.feedback }}
                </div>
              </el-card>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <div v-else class="no-theme">请选择一个主题</div>

      <!-- 编辑弹窗（Markdown 编辑器 + 实时预览） -->
      <el-dialog
        title="编辑测试题"
        :visible.sync="showEditDialog"
        width="800px"
        top="10vh"
        :destroy-on-close="true"
      >
        <el-row :gutter="12">
          <!-- 左边 Markdown 编辑 -->
          <el-col :span="12">
            <el-form label-width="60px">
              <el-form-item label="标题">
                <el-input v-model="currentSection.title" />
              </el-form-item>
              <el-form-item label="描述">
                <el-input
                  type="textarea"
                  rows="12"
                  v-model="currentSection.description_md"
                />
              </el-form-item>
            </el-form>
          </el-col>

          <!-- 右边实时预览 -->
          <el-col :span="12">
            <div class="markdown-preview">
              <h4>实时预览</h4>
              <div v-html="renderMarkdown(currentSection.description_md)"></div>
            </div>
          </el-col>
        </el-row>

        <template #footer>
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="saveEdit">保存</el-button>
        </template>
      </el-dialog>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, computed } from "vue";
import MarkdownIt from "markdown-it";
import { sections } from "./sections.js";

const themes = [
  { id: "7", name: "萌宠乐园" },
  { id: "8", name: "校园小助手" },
  { id: "9", name: "小店铺经营记" },
  { id: "10", name: "数据星球" },
];

const activeThemeId = ref(null);
const activeSectionId = ref(null);
const activeCodeTab = ref("html");

const showEditDialog = ref(false);
const currentSection = ref({});

// 选中主题
const selectTheme = (id) => {
  activeThemeId.value = id;
  const firstSection = sections.find((s) =>
    s.topic_id.startsWith(id + "_")
  );
  if (firstSection) activeSectionId.value = firstSection.topic_id;
};

// 当前主题对象
const activeTheme = computed(() => themes.find((t) => t.id === activeThemeId.value));
const activeThemeSections = computed(() =>
  sections.filter((s) => s.topic_id.startsWith(activeThemeId.value + "_"))
);

// Markdown 渲染
const md = new MarkdownIt({ html: true, linkify: true, typographer: true });
const renderMarkdown = (text) => md.render(text);

// checkpoint 逻辑
const runCheckpoints = (section) => {
  const results = [];
  section.checkpoints.forEach((cp) => {
    let success = true;
    if (cp.type === "assert_element") {
      success = section.start_code.html.includes(`<${cp.selector}`);
    }
    results.push({ name: cp.name, feedback: cp.feedback, success });
  });
  section.results = results;
};

// 编辑弹窗
const openEditDialog = (section) => {
  currentSection.value = JSON.parse(JSON.stringify(section)); // 深拷贝
  showEditDialog.value = true;
};

const saveEdit = () => {
  const index = sections.findIndex(s => s.topic_id === currentSection.value.topic_id);
  if (index !== -1) {
    sections[index] = { ...currentSection.value };
  }
  showEditDialog.value = false;
};
</script>

<style scoped>
.aside-container {
  background-color: #f9f9f9;
  border-right: 1px solid #e0e0e0;
}

.theme-menu {
  height: 100%;
}

.main-container {
  padding: 16px;
  background-color: #f5f7fa;
}

.section-card {
  margin-top: 16px;
  padding: 16px;
  border-radius: 10px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.el-button {
  display: flex;
  align-items: center;      /* 垂直居中 */
  justify-content: center;  /* 水平居中 */
  text-align: center;       /* 文字居中 */
  padding: 0 12px;          /* 可以根据需要调整左右内边距 */
}
.section-title {
  font-weight: 600;
  font-size: 18px;
}

.section-md-card {
  margin-bottom: 16px;
  padding: 12px;
}

.section-code-card {
  margin-bottom: 16px;
}

.run-button-wrapper {
  text-align: right;
  margin-top: 8px;
}

.results-card {
  margin-top: 16px;
  padding: 12px;
  background-color: #fdfdfd;
  border-radius: 6px;
}

.result-success {
  color: green;
  margin-bottom: 4px;
}

.result-fail {
  color: red;
  margin-bottom: 4px;
}

.markdown-preview {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 12px;
  background-color: #fafafa;
  max-height: 380px;
  overflow-y: auto;
}

.markdown-preview h4 {
  margin-top: 0;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.no-theme {
  color: #888;
  text-align: center;
  margin-top: 100px;
  font-size: 16px;
}
</style>
