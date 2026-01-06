<template>
  <el-container style="height: 100vh; overflow: hidden;">
    <!-- 左侧主题列表 -->
    <el-aside width="280px" class="aside-container">
      <div class="aside-header">
        <div class="aside-logo">
          <!-- <span class="logo-icon">💻测试题与调试</span>
          <span class="logo-text"></span> -->
        </div>
        <el-button
          class="new-section-btn"
          type="primary"
          size="small"
          icon="el-icon-plus"
          @click="createNewSection"
        >
          新建小节
        </el-button>
      </div>
      
      <el-scrollbar class="theme-scrollbar">
        <div class="theme-list">
          <div 
            v-for="theme in themes" 
            :key="theme.id"
            class="theme-item"
            :class="{ 'active-theme': activeThemeId === theme.id }"
            @click="selectTheme(theme.id)"
          >
            <div class="theme-icon">📚</div>
            <div class="theme-content">
              <div class="theme-name">{{ theme.name }}</div>
              <div class="theme-stats">
                <span class="section-count">
                  {{ getThemeSectionCount(theme.id) }}小节
                </span>
              </div>
            </div>
            <div class="theme-actions">
              <el-dropdown trigger="click" @command="handleThemeCommand($event, theme)">
                <span class="el-dropdown-link">
                  <el-icon><MoreFilled /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit">编辑主题</el-dropdown-item>
                    <el-dropdown-item command="add">添加小节</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>删除主题</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </el-scrollbar>
    </el-aside>

    <!-- 右侧内容区域 -->
    <el-main class="main-container" v-if="activeTheme">
      <!-- 顶部操作栏 -->
      <div class="main-header">
        <div class="header-left">
          <div class="breadcrumb">
            <span class="breadcrumb-item">{{ activeTheme.name }}</span>
            <el-divider direction="vertical" />
            <span class="breadcrumb-item">
              共 {{ activeThemeSections.length }} 个小节
            </span>
          </div>
        </div>
        <div class="header-actions">
          <el-button-group>
            <el-button
              size="small"
              icon="el-icon-refresh"
              @click="refreshPage"
            >
              刷新
            </el-button>
            <el-button
              size="small"
              type="primary"
              icon="el-icon-video-play"
              @click="runAllCheckpoints"
            >
              全部测试
            </el-button>
            <el-button
              size="small"
              type="success"
              icon="el-icon-download"
              @click="exportCode"
            >
              导出代码
            </el-button>
          </el-button-group>
        </div>
      </div>

      <!-- 小节标签页 -->
      <el-tabs 
        v-model="activeSectionId" 
        type="card" 
        class="section-tabs"
        @tab-click="handleTabClick"
        @edit="handleTabEdit"
        editable
      >
        <el-tab-pane
          v-for="section in activeThemeSections"
          :key="section.topic_id"
          :label="section.title"
          :name="section.topic_id"
          closable
        >
          <!-- 小节内容 -->
          <div class="section-content">
            <!-- 小节标题和操作 -->
            <div class="section-header">
              <div class="section-title-group">
                <h3 class="section-title">{{ section.title }}</h3>
                <el-tag 
                  v-if="section.results" 
                  :type="getSectionResultType(section)"
                  size="small"
                >
                  {{ getSectionResultText(section) }}
                </el-tag>
              </div>
              <div class="section-actions">
                <el-button
                  size="small"
                  icon="el-icon-edit"
                  @click="openEditDialog(section)"
                >
                  编辑
                </el-button>
                <el-button
                  size="small"
                  type="primary"
                  icon="el-icon-video-play"
                  @click="runCheckpoints(section)"
                >
                  运行测试
                </el-button>
                <el-dropdown @command="handleSectionCommand($event, section)">
                  <el-button size="small">
                    更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="duplicate">复制小节</el-dropdown-item>
                      <el-dropdown-item command="reset">重置代码</el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除小节</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>

            <!-- 题目描述区域 -->
            <el-card shadow="hover" class="section-description">
              <template #header>
                <div class="description-header">
                  <span class="description-title">📝 题目描述</span>
                  <el-button
                    size="mini"
                    type="text"
                    icon="el-icon-edit"
                    @click="focusDescription"
                  >
                    编辑
                  </el-button>
                </div>
              </template>
              <div 
                class="markdown-content"
                v-html="renderMarkdown(section.description_md)"
                @dblclick="openEditDialog(section)"
              ></div>
            </el-card>

            <!-- 代码编辑区域 -->
            <div class="code-editor-area">
              <el-card shadow="hover" class="code-editor-card">
                <template #header>
                  <div class="code-header">
                    <span class="code-title">💻 代码编辑器</span>
                    <div class="code-actions">
                      <el-button-group size="mini">
                        <el-button
                          :type="activeCodeTab === 'html' ? 'primary' : ''"
                          @click="activeCodeTab = 'html'"
                        >
                          HTML
                        </el-button>
                        <el-button
                          :type="activeCodeTab === 'css' ? 'primary' : ''"
                          @click="activeCodeTab = 'css'"
                        >
                          CSS
                        </el-button>
                        <el-button
                          :type="activeCodeTab === 'js' ? 'primary' : ''"
                          @click="activeCodeTab = 'js'"
                        >
                          JavaScript
                        </el-button>
                      </el-button-group>
                      <el-button
                        size="mini"
                        icon="el-icon-refresh"
                        @click="resetCode(section)"
                      >
                        重置
                      </el-button>
                    </div>
                  </div>
                </template>
                
                <!-- 代码编辑器 -->
                <div class="editor-wrapper">
                  <div v-if="activeCodeTab === 'html'" class="editor-container">
                    <div class="editor-header">
                      <span class="editor-label">HTML</span>
                      <el-tag size="mini" effect="plain">index.html</el-tag>
                    </div>
                    <el-input
                      type="textarea"
                      :rows="16"
                      v-model="section.start_code.html"
                      placeholder="在此编写 HTML 代码..."
                      class="code-input"
                      resize="none"
                      @input="handleCodeChange"
                    />
                  </div>
                  
                  <div v-if="activeCodeTab === 'css'" class="editor-container">
                    <div class="editor-header">
                      <span class="editor-label">CSS</span>
                      <el-tag size="mini" effect="plain">style.css</el-tag>
                    </div>
                    <el-input
                      type="textarea"
                      :rows="16"
                      v-model="section.start_code.css"
                      placeholder="在此编写 CSS 代码..."
                      class="code-input"
                      resize="none"
                      @input="handleCodeChange"
                    />
                  </div>
                  
                  <div v-if="activeCodeTab === 'js'" class="editor-container">
                    <div class="editor-header">
                      <span class="editor-label">JavaScript</span>
                      <el-tag size="mini" effect="plain">script.js</el-tag>
                    </div>
                    <el-input
                      type="textarea"
                      :rows="16"
                      v-model="section.start_code.js"
                      placeholder="在此编写 JavaScript 代码..."
                      class="code-input"
                      resize="none"
                      @input="handleCodeChange"
                    />
                  </div>
                </div>
                
                <!-- 代码统计 -->
                <div class="code-stats">
                  <span class="stat-item">
                    <el-icon><Document /></el-icon>
                    行数: {{ getCodeLines(section.start_code[activeCodeTab]) }}
                  </span>
                  <span class="stat-item">
                    <el-icon><Finished /></el-icon>
                    字符数: {{ section.start_code[activeCodeTab]?.length || 0 }}
                  </span>
                  <span class="stat-item">
                    <el-icon><Timer /></el-icon>
                    上次保存: {{ formatTime(section.lastModified) }}
                  </span>
                </div>
              </el-card>

              <!-- 实时预览区域 -->
              <el-card shadow="hover" class="preview-card">
                <template #header>
                  <div class="preview-header">
                    <span class="preview-title">👁️ 实时预览</span>
                    <el-button
                      size="mini"
                      icon="el-icon-refresh"
                      @click="refreshPreview"
                    >
                      刷新预览
                    </el-button>
                  </div>
                </template>
                <div class="preview-container">
                  <iframe 
                    :srcdoc="getPreviewHtml(section)"
                    class="preview-frame"
                    title="实时预览"
                  ></iframe>
                </div>
              </el-card>
            </div>

            <!-- 测试结果区域 -->
            <el-card 
              v-if="section.results && section.results.length > 0"
              shadow="hover" 
              class="results-card"
              :class="{'has-results': section.results}"
            >
              <template #header>
                <div class="results-header">
                  <span class="results-title">🧪 测试结果</span>
                  <div class="results-summary">
                    <span class="summary-item success">
                      ✅ 通过: {{ getPassedCount(section.results) }}
                    </span>
                    <span class="summary-item error">
                      ❌ 失败: {{ getFailedCount(section.results) }}
                    </span>
                    <span class="summary-item total">
                      总计: {{ section.results.length }}
                    </span>
                  </div>
                </div>
              </template>
              
              <div class="results-list">
                <div
                  v-for="(res, index) in section.results"
                  :key="index"
                  class="result-item"
                  :class="res.success ? 'result-success' : 'result-fail'"
                >
                  <div class="result-icon">
                    <el-icon v-if="res.success" color="#67C23A" size="20">
                      <CircleCheckFilled />
                    </el-icon>
                    <el-icon v-else color="#F56C6C" size="20">
                      <CircleCloseFilled />
                    </el-icon>
                  </div>
                  <div class="result-content">
                    <div class="result-name">{{ res.name }}</div>
                    <div class="result-feedback">{{ res.feedback }}</div>
                    <div v-if="!res.success" class="result-hint">
                      <el-tag size="mini" type="warning">提示</el-tag>
                      请检查代码是否符合要求
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- 创建新小节按钮 -->
      <div v-if="activeThemeSections.length === 0" class="empty-section">
        <div class="empty-content">
          <div class="empty-icon">📝</div>
          <h3>暂无小节内容</h3>
          <p>点击下方按钮创建第一个小节</p>
          <el-button
            type="primary"
            icon="el-icon-plus"
            @click="createNewSection"
          >
            创建新小节
          </el-button>
        </div>
      </div>
    </el-main>

    <!-- 无主题时的空状态 -->
    <el-main v-else class="no-theme">
      <div class="empty-state">
        <div class="empty-icon">📚</div>
        <!-- <h2>欢迎来到代码实验室</h2> -->
        <p>请从左侧选择一个主题开始编辑或创建新内容</p>
        <div class="empty-actions">
          <el-button type="primary" @click="createNewTheme">
            <el-icon><Plus /></el-icon>
            新建主题
          </el-button>
          <el-button @click="importContent">
            <el-icon><Upload /></el-icon>
            导入内容
          </el-button>
        </div>
      </div>
    </el-main>

    <!-- 编辑弹窗 -->
    <el-dialog
      :title="`编辑小节: ${currentSection.title}`"
      :visible.sync="showEditDialog"
      width="900px"
      top="5vh"
      :destroy-on-close="true"
      custom-class="edit-dialog"
    >
      <div class="edit-dialog-content">
        <el-row :gutter="20">
          <!-- 左侧编辑区 -->
          <el-col :span="12">
            <el-card shadow="never" class="edit-form-card">
              <template #header>
                <div class="card-header">
                  <span>编辑内容</span>
                </div>
              </template>
              
              <el-form label-width="80px" label-position="top">
                <el-form-item label="小节标题">
                  <el-input 
                    v-model="currentSection.title" 
                    placeholder="请输入小节标题"
                    size="medium"
                  />
                </el-form-item>
                
                <el-form-item label="题目描述 (Markdown)">
                  <div class="markdown-editor-toolbar">
                    <el-button-group size="mini">
                      <el-button @click="insertMarkdown('**', '**')">粗体</el-button>
                      <el-button @click="insertMarkdown('*', '*')">斜体</el-button>
                      <el-button @click="insertMarkdown('`', '`')">代码</el-button>
                      <el-button @click="insertMarkdown('```\n', '\n```')">代码块</el-button>
                    </el-button-group>
                  </div>
                  <el-input
                    type="textarea"
                    :rows="15"
                    v-model="currentSection.description_md"
                    placeholder="在此使用 Markdown 语法编写题目描述..."
                    class="markdown-editor"
                    resize="vertical"
                    ref="descriptionEditor"
                  />
                </el-form-item>
                
                <el-form-item label="测试点配置">
                  <div class="checkpoint-config">
                    <div 
                      v-for="(cp, index) in currentSection.checkpoints"
                      :key="index"
                      class="checkpoint-item"
                    >
                      <div class="cp-header">
                        <span class="cp-name">{{ cp.name }}</span>
                        <el-button
                          size="mini"
                          type="text"
                          icon="el-icon-delete"
                          @click="removeCheckpoint(index)"
                        />
                      </div>
                      <div class="cp-content">
                        <el-input
                          size="mini"
                          v-model="cp.selector"
                          placeholder="CSS 选择器"
                        />
                        <el-input
                          size="mini"
                          v-model="cp.feedback"
                          placeholder="反馈信息"
                        />
                      </div>
                    </div>
                    <el-button
                      size="small"
                      icon="el-icon-plus"
                      @click="addCheckpoint"
                    >
                      添加测试点
                    </el-button>
                  </div>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>

          <!-- 右侧预览区 -->
          <el-col :span="12">
            <el-card shadow="never" class="preview-card">
              <template #header>
                <div class="card-header">
                  <span>实时预览</span>
                  <el-button
                    size="mini"
                    type="text"
                    icon="el-icon-full-screen"
                    @click="toggleFullPreview"
                  />
                </div>
              </template>
              
              <div class="markdown-preview">
                <div class="preview-content">
                  <h3>{{ currentSection.title }}</h3>
                  <div v-html="renderMarkdown(currentSection.description_md)"></div>
                </div>
                
                <div class="preview-stats">
                  <el-tag size="small">
                    字数: {{ currentSection.description_md?.length || 0 }}
                  </el-tag>
                  <el-tag size="small">
                    测试点: {{ currentSection.checkpoints?.length || 0 }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="saveEdit">
            <el-icon><Check /></el-icon>
            保存更改
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 新建主题弹窗 -->
    <el-dialog
      title="新建主题"
      :visible.sync="showNewThemeDialog"
      width="400px"
    >
      <el-form :model="newThemeForm" label-width="80px">
        <el-form-item label="主题名称">
          <el-input v-model="newThemeForm.name" placeholder="请输入主题名称" />
        </el-form-item>
        <el-form-item label="主题描述">
          <el-input 
            v-model="newThemeForm.description" 
            type="textarea"
            :rows="3"
            placeholder="请输入主题描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showNewThemeDialog = false">取消</el-button>
        <el-button type="primary" @click="createTheme">创建</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, computed, nextTick } from "vue";
import MarkdownIt from "markdown-it";
import { 
  MoreFilled, 
  ArrowDown, 
  Document, 
  Finished, 
  Timer,
  CircleCheckFilled,
  CircleCloseFilled,
  Plus,
  Upload,
  Check
} from '@element-plus/icons-vue';

const md = new MarkdownIt({ 
  html: true, 
  linkify: true, 
  typographer: true,
  breaks: true,
  highlight: function (str, lang) {
    return `<pre class="code-block"><code class="language-${lang}">${md.utils.escapeHtml(str)}</code></pre>`;
  }
});

// 主题数据
const themes = ref([
  { id: "7", name: "萌宠乐园" },
  { id: "8", name: "校园小助手" },
  { id: "9", name: "小店铺经营记" },
  { id: "10", name: "数据星球" },
]);

// 模拟的 sections 数据
const sections = ref([
  {
    topic_id: "7_1",
    theme_id: "7",
    title: "HTML基础标签",
    description_md: `# 创建你的第一个HTML页面

学习目标：
- 理解HTML基本结构
- 掌握常用标签的使用
- 创建包含标题和段落的页面

## 要求

1. 创建一个包含 \`h1\` 标签的标题
2. 添加至少两个 \`p\` 标签的段落
3. 使用正确的HTML文档结构

## 示例代码

\`\`\`html
<!DOCTYPE html>
<html>
<head>
    <title>我的第一个网页</title>
</head>
<body>
    <h1>欢迎来到萌宠乐园</h1>
    <p>这是一个充满乐趣的地方！</p>
</body>
</html>
\`\`\``,
    start_code: {
      html: `<!DOCTYPE html>
<html>
<head>
    <title>萌宠乐园</title>
</head>
<body>
    <h1 class="title">欢迎来到萌宠乐园</h1>
    <p>这是一个充满乐趣的地方！</p>
    <p>这里有很多可爱的小动物。</p>
</body>
</html>`,
      css: `/* 在这里添加CSS样式 */
.title {
  color: #409EFF;
}`,
      js: `// 在这里添加JavaScript代码
console.log('萌宠乐园欢迎您！');`
    },
    checkpoints: [
      { type: "assert_element", selector: "h1", name: "h1标签", feedback: "检测到 h1 标签" },
      { type: "assert_element", selector: "p", name: "p标签", feedback: "检测到 p 标签" },
      { type: "assert_class", selector: ".title", name: "class名称", feedback: "检测到 class='title'" }
    ],
    results: [],
    lastModified: new Date()
  },
  {
    topic_id: "7_2",
    theme_id: "7",
    title: "图片和链接",
    description_md: `# 添加图片和链接

学习如何在网页中添加图片和创建超链接。`,
    start_code: {
      html: `<div>
    <h2>可爱的宠物</h2>
    <img src="https://example.com/cat.jpg" alt="小猫">
</div>`,
      css: `img {
    max-width: 300px;
    border-radius: 10px;
}`,
      js: `// 暂无JavaScript代码`
    },
    checkpoints: [
      { type: "assert_element", selector: "img", name: "img标签", feedback: "检测到 img 标签" },
      { type: "assert_element", selector: "a", name: "a标签", feedback: "检测到 a 标签" }
    ],
    results: [],
    lastModified: new Date()
  },
  {
    topic_id: "8_1",
    theme_id: "8",
    title: "创建表单",
    description_md: `# 学习创建表单`,
    start_code: {
      html: `<form>
    <input type="text" placeholder="请输入姓名">
</form>`,
      css: `input {
    padding: 8px;
    border: 1px solid #ddd;
}`,
      js: ``
    },
    checkpoints: [
      { type: "assert_element", selector: "form", name: "form标签", feedback: "检测到 form 标签" },
      { type: "assert_element", selector: "input", name: "input标签", feedback: "检测到 input 标签" }
    ],
    results: [],
    lastModified: new Date()
  }
]);

const activeThemeId = ref(null);
const activeSectionId = ref(null);
const activeCodeTab = ref("html");
const showEditDialog = ref(false);
const showNewThemeDialog = ref(false);
const currentSection = ref({});
const newThemeForm = ref({
  name: "",
  description: ""
});

// 计算属性
const activeTheme = computed(() => 
  themes.value.find((t) => t.id === activeThemeId.value)
);

const activeThemeSections = computed(() =>
  sections.value.filter((s) => s.topic_id.startsWith(activeThemeId.value + "_"))
);

// 方法
const selectTheme = (id) => {
  activeThemeId.value = id;
  const firstSection = sections.value.find((s) =>
    s.topic_id.startsWith(id + "_")
  );
  if (firstSection) activeSectionId.value = firstSection.topic_id;
};

const renderMarkdown = (text) => {
  if (!text) return "";
  return md.render(text);
};

const runCheckpoints = (section) => {
  const results = [];
  section.checkpoints.forEach((cp) => {
    let success = false;
    let htmlCode = section.start_code.html || "";
    
    switch(cp.type) {
      case "assert_element":
        success = htmlCode.includes(`<${cp.selector}`);
        break;
      case "assert_class":
        success = htmlCode.includes(`class="${cp.selector.replace('.', '')}"`);
        break;
      default:
        success = false;
    }
    
    results.push({ 
      name: cp.name, 
      feedback: cp.feedback, 
      success,
      timestamp: new Date()
    });
  });
  section.results = results;
  section.lastModified = new Date();
};

const runAllCheckpoints = () => {
  activeThemeSections.value.forEach(section => {
    runCheckpoints(section);
  });
  ElMessage.success('已完成所有测试！');
};

const openEditDialog = (section) => {
  currentSection.value = JSON.parse(JSON.stringify(section));
  showEditDialog.value = true;
  nextTick(() => {
    if (currentSection.value.description_md) {
      // 自动聚焦到描述编辑器
    }
  });
};

const saveEdit = () => {
  const index = sections.value.findIndex(s => s.topic_id === currentSection.value.topic_id);
  if (index !== -1) {
    sections.value[index] = { 
      ...sections.value[index], 
      ...currentSection.value,
      lastModified: new Date()
    };
  }
  showEditDialog.value = false;
  ElMessage.success('保存成功！');
};

const getThemeSectionCount = (themeId) => {
  return sections.value.filter(s => s.topic_id.startsWith(themeId + "_")).length;
};

const getSectionResultType = (section) => {
  if (!section.results || section.results.length === 0) return 'info';
  const passed = section.results.filter(r => r.success).length;
  if (passed === section.results.length) return 'success';
  if (passed > 0) return 'warning';
  return 'danger';
};

const getSectionResultText = (section) => {
  if (!section.results || section.results.length === 0) return '未测试';
  const passed = section.results.filter(r => r.success).length;
  return `${passed}/${section.results.length}`;
};

const getPassedCount = (results) => {
  return results.filter(r => r.success).length;
};

const getFailedCount = (results) => {
  return results.filter(r => !r.success).length;
};

const getCodeLines = (code) => {
  if (!code) return 0;
  return code.split('\n').length;
};

const formatTime = (date) => {
  if (!date) return '刚刚';
  const now = new Date();
  const diff = now - new Date(date);
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}小时前`;
  return `${Math.floor(hours / 24)}天前`;
};

const getPreviewHtml = (section) => {
  const html = section.start_code.html || '';
  const css = section.start_code.css || '';
  const js = section.start_code.js || '';
  
  return `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>${css}</style>
    </head>
    <body>
        ${html}
        <script>${js}<\/script>
    </body>
    </html>
  `;
};

const handleCodeChange = () => {
  // 这里可以添加自动保存功能
};

const resetCode = (section) => {
  ElMessageBox.confirm('确定要重置代码吗？这将恢复初始代码。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 这里应该重置为原始代码
    ElMessage.success('代码已重置');
  });
};

const refreshPreview = () => {
  ElMessage.info('预览已刷新');
};

const createNewSection = () => {
  if (!activeThemeId.value) {
    ElMessage.warning('请先选择一个主题');
    return;
  }
  
  const newSection = {
    topic_id: `${activeThemeId.value}_${activeThemeSections.value.length + 1}`,
    theme_id: activeThemeId.value,
    title: `新小节 ${activeThemeSections.value.length + 1}`,
    description_md: '# 新小节\n\n请在此编写题目描述...',
    start_code: {
      html: '<!DOCTYPE html>\n<html>\n<head>\n    <title>新页面</title>\n</head>\n<body>\n    \n</body>\n</html>',
      css: '/* 在这里添加CSS样式 */',
      js: '// 在这里添加JavaScript代码'
    },
    checkpoints: [
      { type: "assert_element", selector: "h1", name: "h1标签", feedback: "检测到 h1 标签" }
    ],
    results: [],
    lastModified: new Date()
  };
  
  sections.value.push(newSection);
  activeSectionId.value = newSection.topic_id;
  ElMessage.success('新小节创建成功！');
};

const createNewTheme = () => {
  showNewThemeDialog.value = true;
};

const createTheme = () => {
  const newId = String(Math.max(...themes.value.map(t => parseInt(t.id))) + 1);
  themes.value.push({
    id: newId,
    name: newThemeForm.value.name || `新主题 ${newId}`
  });
  showNewThemeDialog.value = false;
  newThemeForm.value = { name: "", description: "" };
  ElMessage.success('新主题创建成功！');
};

const handleThemeCommand = (command, theme) => {
  switch(command) {
    case 'edit':
      ElMessage.info(`编辑主题: ${theme.name}`);
      break;
    case 'add':
      selectTheme(theme.id);
      createNewSection();
      break;
    case 'delete':
      ElMessageBox.confirm(`确定要删除主题"${theme.name}"吗？`, '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        themes.value = themes.value.filter(t => t.id !== theme.id);
        ElMessage.success('主题已删除');
      });
      break;
  }
};

const handleSectionCommand = (command, section) => {
  switch(command) {
    case 'duplicate':
      ElMessage.info(`复制小节: ${section.title}`);
      break;
    case 'reset':
      resetCode(section);
      break;
    case 'delete':
      ElMessageBox.confirm(`确定要删除小节"${section.title}"吗？`, '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        sections.value = sections.value.filter(s => s.topic_id !== section.topic_id);
        ElMessage.success('小节已删除');
      });
      break;
  }
};

const handleTabClick = (tab) => {
  // 处理标签点击
};

const handleTabEdit = (targetKey, action) => {
  if (action === 'remove') {
    const section = sections.value.find(s => s.topic_id === targetKey);
    if (section) {
      ElMessageBox.confirm(`确定要关闭"${section.title}"吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }).then(() => {
        const index = activeThemeSections.value.findIndex(s => s.topic_id === targetKey);
        if (index > 0) {
          activeSectionId.value = activeThemeSections.value[index - 1].topic_id;
        }
      });
    }
  }
};

const refreshPage = () => {
  ElMessage.info('页面已刷新');
};

const exportCode = () => {
  ElMessage.success('代码导出成功！');
};

const focusDescription = () => {
  openEditDialog(activeThemeSections.value.find(s => s.topic_id === activeSectionId.value));
};

const insertMarkdown = (prefix, suffix) => {
  const editor = document.querySelector('.markdown-editor textarea');
  if (!editor) return;
  
  const start = editor.selectionStart;
  const end = editor.selectionEnd;
  const text = currentSection.value.description_md || '';
  const selectedText = text.substring(start, end);
  
  currentSection.value.description_md = 
    text.substring(0, start) + 
    prefix + selectedText + suffix + 
    text.substring(end);
  
  nextTick(() => {
    editor.focus();
    editor.setSelectionRange(start + prefix.length, end + prefix.length);
  });
};

const addCheckpoint = () => {
  if (!currentSection.value.checkpoints) {
    currentSection.value.checkpoints = [];
  }
  currentSection.value.checkpoints.push({
    type: "assert_element",
    selector: "",
    name: "新测试点",
    feedback: "请输入反馈信息"
  });
};

const removeCheckpoint = (index) => {
  currentSection.value.checkpoints.splice(index, 1);
};

const toggleFullPreview = () => {
  ElMessage.info('全屏预览功能');
};
</script>

<style scoped>
/* 左侧边栏 */
.aside-container {
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  border-right: none;
}

.aside-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.aside-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
}

.new-section-btn {
  font-size: 12px;
}

.theme-scrollbar {
  height: calc(100vh - 80px);
}

.theme-list {
  padding: 10px;
}

.theme-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin: 6px 0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.05);
}

.theme-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.active-theme {
  background: rgba(64, 158, 255, 0.2);
  border-left: 3px solid #409EFF;
}

.theme-icon {
  font-size: 20px;
  margin-right: 12px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
}

.theme-content {
  flex: 1;
}

.theme-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.theme-stats {
  font-size: 12px;
  opacity: 0.7;
}

.theme-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.theme-item:hover .theme-actions {
  opacity: 1;
}

/* 主内容区 */
.main-container {
  padding: 0;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.main-header {
  background: white;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 12px;
}

.breadcrumb-item {
  font-size: 14px;
  color: #4b5563;
}

.breadcrumb-item:first-child {
  font-weight: 600;
  color: #1f2937;
}

/* 标签页 */
.section-tabs {
  flex: 1;
  padding: 0 24px;
  background: transparent;
}

:deep(.el-tabs__header) {
  margin: 0;
}

:deep(.el-tabs__nav-wrap) {
  padding: 0;
}

:deep(.el-tabs__item) {
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
}

/* 小节内容 */
.section-content {
  padding: 20px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.section-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
}

.section-actions {
  display: flex;
  gap: 8px;
}

/* 描述区域 */
.section-description {
  margin-bottom: 20px;
}

.description-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.description-title {
  font-weight: 600;
  color: #1f2937;
}

.markdown-content {
  line-height: 1.6;
  color: #374151;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3 {
  color: #1f2937;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

.markdown-content pre {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
}

.markdown-content code {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
}

/* 代码编辑区域 */
.code-editor-area {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.code-editor-card {
  grid-column: 1;
}

.preview-card {
  grid-column: 2;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.code-title {
  font-weight: 600;
  color: #1f2937;
}

.code-actions {
  display: flex;
  gap: 8px;
}

.editor-wrapper {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.editor-container {
  display: none;
}

.editor-container:first-child {
  display: block;
}

.editor-header {
  background: #f9fafb;
  padding: 8px 12px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-label {
  font-weight: 500;
  color: #4b5563;
}

.code-input {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.5;
}

:deep(.code-input textarea) {
  font-family: 'Consolas', 'Monaco', monospace !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
  padding: 16px !important;
  border: none !important;
}

.code-stats {
  background: #f9fafb;
  padding: 8px 16px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #6b7280;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 预览区域 */
.preview-container {
  height: 500px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.preview-frame {
  width: 100%;
  height: 100%;
  border: none;
  background: white;
}

/* 测试结果区域 */
.results-card {
  margin-top: 20px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.results-title {
  font-weight: 600;
  color: #1f2937;
}

.results-summary {
  display: flex;
  gap: 16px;
  font-size: 14px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.summary-item.success {
  color: #67C23A;
}

.summary-item.error {
  color: #F56C6C;
}

.summary-item.total {
  color: #909399;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.result-success {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
}

.result-fail {
  background: #fff2f0;
  border: 1px solid #ffccc7;
}

.result-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.result-content {
  flex: 1;
}

.result-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.result-feedback {
  font-size: 14px;
  color: #595959;
  margin-bottom: 4px;
}

.result-hint {
  font-size: 12px;
  color: #d46b08;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 空状态 */
.empty-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.empty-content {
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-content h3 {
  margin: 0 0 8px 0;
  color: #1f2937;
}

.empty-content p {
  color: #6b7280;
  margin-bottom: 20px;
}

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
  margin: 0 0 24px 0;
}

.empty-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* 编辑弹窗 */
.edit-dialog-content {
  max-height: 70vh;
  overflow-y: auto;
}

.edit-form-card,
.preview-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.markdown-editor-toolbar {
  margin-bottom: 8px;
}

.markdown-editor {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
}

.markdown-preview {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 12px;
}

.preview-stats {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.checkpoint-config {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  background: #f9fafb;
}

.checkpoint-item {
  padding: 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-bottom: 8px;
}

.cp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.cp-name {
  font-weight: 500;
  color: #1f2937;
}

.cp-content {
  display: flex;
  gap: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .code-editor-area {
    grid-template-columns: 1fr;
  }
  
  .code-editor-card,
  .preview-card {
    grid-column: 1;
  }
}

@media (max-width: 768px) {
  .aside-container {
    width: 200px !important;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .section-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .code-editor-area {
    grid-template-columns: 1fr;
  }
}
</style>