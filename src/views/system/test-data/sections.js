export const sections = [
  // 主题 7：萌宠乐园
  {
    topic_id: "7_1",
    title: "7_1 显示宠物列表",
    description_md: "# 任务描述：\n请使用 HTML 构建一个宠物列表页面，显示宠物名称和种类。\n\n## 要求：\n1. 使用 `<ul>` 创建列表。\n2. 列表中至少包含 3 个宠物项，每个项包含 `<li>`。\n3. 每个 `<li>` 中显示宠物名称和种类。",
    start_code: {
      html: "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n<meta charset=\"UTF-8\">\n<title>萌宠乐园</title>\n</head>\n<body>\n<!-- 请在此处添加代码 -->\n</body>\n</html>",
      css: "",
      js: ""
    },
    checkpoints: [
      { name: "ul元素存在检查", type: "assert_element", selector: "ul", assertion_type: "exists", feedback: "请添加一个ul元素。" },
      { name: "li元素存在检查", type: "assert_element", selector: "ul li", assertion_type: "exists", feedback: "请在ul中添加li元素。" }
    ],
    answer: {
      html: "<ul>\n<li>小花 - 猫</li>\n<li>小黑 - 狗</li>\n<li>小白 - 兔</li>\n</ul>",
      css: "",
      js: ""
    }
  },
  {
    topic_id: "7_2",
    title: "7_2 宠物详情展示",
    description_md: "# 任务描述：\n请在页面中展示单个宠物的详细信息。\n\n## 要求：\n1. 使用 `<h2>` 显示宠物名称。\n2. 使用 `<p>` 显示宠物年龄和品种。\n3. 页面布局整齐。",
    start_code: {
      html: "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n<meta charset=\"UTF-8\">\n<title>宠物详情</title>\n</head>\n<body>\n<!-- 请在此处添加代码 -->\n</body>\n</html>",
      css: "",
      js: ""
    },
    checkpoints: [
      { name: "h2元素存在检查", type: "assert_element", selector: "h2", assertion_type: "exists", feedback: "请添加h2元素显示宠物名称。" },
      { name: "p元素存在检查", type: "assert_element", selector: "p", assertion_type: "exists", feedback: "请添加p元素显示宠物信息。" }
    ],
    answer: {
      html: "<h2>小花</h2>\n<p>年龄: 2岁, 品种: 猫</p>",
      css: "",
      js: ""
    }
  },
  {
    topic_id: "7_3",
    title: "7_3 宠物交互按钮",
    description_md: "# 任务描述：\n在宠物详情页添加按钮实现简单交互。\n\n## 要求：\n1. 使用 `<button>` 创建“喂食”和“玩耍”按钮。\n2. 按钮点击后用 JS 弹出对应提示信息。",
    start_code: {
      html: "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n<meta charset=\"UTF-8\">\n<title>宠物互动</title>\n</head>\n<body>\n<!-- 请在此处添加按钮 -->\n</body>\n</html>",
      css: "",
      js: ""
    },
    checkpoints: [
      { name: "按钮存在检查", type: "assert_element", selector: "button", assertion_type: "exists", feedback: "请添加按钮。" },
      { name: "JS功能检查", type: "custom_script", script: "const buttons = document.querySelectorAll('button'); return buttons.length === 2;", feedback: "页面应有两个按钮。" }
    ],
    answer: {
      html: "<button onclick=\"alert('喂食成功')\">喂食</button>\n<button onclick=\"alert('玩耍成功')\">玩耍</button>",
      css: "",
      js: ""
    }
  },

  // 主题 8：校园小助手
  {
    topic_id: "8_1",
    title: "8_1 课程列表展示",
    description_md: "# 任务描述：\n使用 HTML 显示课程列表。\n\n## 要求：\n1. 使用 `<table>` 显示课程名称、时间、老师。\n2. 表格至少包含三行数据。",
    start_code: { html: "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n<meta charset=\"UTF-8\">\n<title>课程列表</title>\n</head>\n<body>\n</body>\n</html>", css: "", js: "" },
    checkpoints: [
      { name: "table存在检查", type: "assert_element", selector: "table", assertion_type: "exists", feedback: "请添加table元素。" },
      { name: "tr存在检查", type: "assert_element", selector: "table tr", assertion_type: "exists", feedback: "表格应包含tr行。" }
    ],
    answer: { html: "<table>\n<tr><td>语文</td><td>08:00</td><td>张老师</td></tr>\n<tr><td>数学</td><td>09:00</td><td>李老师</td></tr>\n<tr><td>英语</td><td>10:00</td><td>王老师</td></tr>\n</table>", css: "", js: "" }
  },
  {
    topic_id: "8_2",
    title: "8_2 学生信息卡片",
    description_md: "# 任务描述：\n在页面中展示学生信息卡片。\n\n## 要求：\n1. 使用 `<div>` 创建卡片。\n2. 显示学生姓名、学号、班级。\n3. 样式整齐美观。",
    start_code: { html: "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n<meta charset=\"UTF-8\">\n<title>学生信息</title>\n</head>\n<body>\n</body>\n</html>", css: "", js: "" },
    checkpoints: [
      { name: "div存在检查", type: "assert_element", selector: "div", assertion_type: "exists", feedback: "请添加div卡片。" }
    ],
    answer: { html: "<div>\n<h2>张三</h2>\n<p>学号: 20240101</p>\n<p>班级: 一年级一班</p>\n</div>", css: "", js: "" }
  },
  {
    topic_id: "8_3",
    title: "8_3 基础交互按钮",
    description_md: "# 任务描述：\n在学生卡片上添加按钮，实现点击提示。\n\n## 要求：\n1. 添加“签到”和“请假”按钮。\n2. 点击按钮显示提示。",
    start_code: { html: "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n<meta charset=\"UTF-8\">\n<title>学生操作</title>\n</head>\n<body>\n</body>\n</html>", css: "", js: "" },
    checkpoints: [
      { name: "按钮检查", type: "assert_element", selector: "button", assertion_type: "exists", feedback: "请添加按钮。" }
    ],
    answer: { html: "<button onclick=\"alert('签到成功')\">签到</button>\n<button onclick=\"alert('请假成功')\">请假</button>", css: "", js: "" }
  },

  // 主题 9：小店铺经营记
  {
    topic_id: "9_1",
    title: "9_1 商品列表",
    description_md: "# 任务描述：\n显示商品列表。\n\n## 要求：\n1. 使用 `<ul>` 展示商品名称和价格。\n2. 列表至少包含三项。",
    start_code: { html: "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n<meta charset=\"UTF-8\">\n<title>商品列表</title>\n</head>\n<body>\n</body>\n</html>", css: "", js: "" },
    checkpoints: [
      { name: "ul检查", type: "assert_element", selector: "ul", assertion_type: "exists", feedback: "请添加ul。" },
      { name: "li检查", type: "assert_element", selector: "ul li", assertion_type: "exists", feedback: "请添加li。" }
    ],
    answer: { html: "<ul>\n<li>面包 - $5</li>\n<li>牛奶 - $3</li>\n<li>水果 - $8</li>\n</ul>", css: "", js: "" }
  },
  {
    topic_id: "9_2",
    title: "9_2 商品详情",
    description_md: "# 任务描述：\n显示单个商品详细信息。\n\n## 要求：\n1. 使用 `<h2>` 显示商品名。\n2. 使用 `<p>` 显示价格和库存。",
    start_code: { html: "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n<meta charset=\"UTF-8\">\n<title>商品详情</title>\n</head>\n<body>\n</body>\n</html>", css: "", js: "" },
    checkpoints: [
      { name: "h2检查", type: "assert_element", selector: "h2", assertion_type: "exists", feedback: "请添加h2。" },
      { name: "p检查", type: "assert_element", selector: "p", assertion_type: "exists", feedback: "请添加p。" }
    ],
    answer: { html: "<h2>面包</h2>\n<p>价格: $5, 库存: 20</p>", css: "", js: "" }
  },
  {
    topic_id: "9_3",
    title: "9_3 购物车按钮",
    description_md: "# 任务描述：\n为商品添加操作按钮。\n\n## 要求：\n1. 添加“加入购物车”和“收藏”按钮。\n2. 点击按钮显示提示信息。",
    start_code: { html: "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n<meta charset=\"UTF-8\">\n<title>商品操作</title>\n</head>\n<body>\n</body>\n</html>", css: "", js: "" },
    checkpoints: [
      { name: "按钮检查", type: "assert_element", selector: "button", assertion_type: "exists", feedback: "请添加按钮。" }
    ],
    answer: { html: "<button onclick=\"alert('加入购物车成功')\">加入购物车</button>\n<button onclick=\"alert('收藏成功')\">收藏</button>", css: "", js: "" }
  },

  // 主题 10：数据星球
  {
    topic_id: "10_1",
    title: "10_1 数据统计表格",
    description_md: "# 任务描述：\n展示数据表格。\n\n## 要求：\n1. 使用 `<table>` 展示数据。\n2. 表格至少包含三行记录。",
    start_code: { html: "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n<meta charset=\"UTF-8\">\n<title>数据表格</title>\n</head>\n<body>\n</body>\n</html>", css: "", js: "" },
    checkpoints: [
      { name: "table检查", type: "assert_element", selector: "table", assertion_type: "exists", feedback: "请添加table。" },
      { name: "tr检查", type: "assert_element", selector: "table tr", assertion_type: "exists", feedback: "请添加tr。" }
    ],
    answer: { html: "<table>\n<tr><td>用户数</td><td>150</td></tr>\n<tr><td>订单数</td><td>80</td></tr>\n<tr><td>访问量</td><td>200</td></tr>\n</table>", css: "", js: "" }
  },
  {
    topic_id: "10_2",
    title: "10_2 数据可视化图表",
    description_md: "# 任务描述：\n展示简单柱状图。\n\n## 要求：\n1. 使用 `<div>` 或 `<canvas>` 绘制图表。\n2. 图表显示三个数据点。",
    start_code: { html: "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n<meta charset=\"UTF-8\">\n<title>柱状图</title>\n</head>\n<body>\n</body>\n</html>", css: "", js: "" },
    checkpoints: [
      { name: "div/canvas检查", type: "assert_element", selector: "div, canvas", assertion_type: "exists", feedback: "请添加div或canvas绘图。" }
    ],
    answer: { html: "<div style='display:flex;'>\n<div style='width:50px;height:150px;background:#4caf50;margin:5px'></div>\n<div style='width:50px;height:80px;background:#2196f3;margin:5px'></div>\n<div style='width:50px;height:120px;background:#f44336;margin:5px'></div>\n</div>", css: "", js: "" }
  },
  {
    topic_id: "10_3",
    title: "10_3 数据筛选按钮",
    description_md: "# 任务描述：\n添加按钮实现简单数据筛选交互。\n\n## 要求：\n1. 添加“显示用户数据”和“显示订单数据”按钮。\n2. 点击按钮显示提示。",
    start_code: { html: "<!DOCTYPE html>\n<html lang=\"zh\">\n<head>\n<meta charset=\"UTF-8\">\n<title>数据筛选</title>\n</head>\n<body>\n</body>\n</html>", css: "", js: "" },
    checkpoints: [
      { name: "按钮检查", type: "assert_element", selector: "button", assertion_type: "exists", feedback: "请添加按钮。" }
    ],
    answer: { html: "<button onclick=\"alert('显示用户数据')\">显示用户数据</button>\n<button onclick=\"alert('显示订单数据')\">显示订单数据</button>", css: "", js: "" }
  }
]
