import { defineMock } from "./base";
import { SUCCESS_CODE ,ERROR_CODE} from '../src/constants'

// 模拟学习内容数据
const learningContents = [
  {
    "topic_id": "1_1",
    "title": "使用h元素和p元素体验标题与段落",
    "graphId": "萌宠乐园",
    "levels": [
      {
        "level": 1,
        "description": "在网页开发中，HTML（超文本标记语言）是构建页面结构的基础。为了让用户清晰地理解页面内容，我们需要合理组织文字信息。标题和段落就是最基础的文本结构工具。HTML提供了从h1到h6共六个级别的标题元素，其中h1代表最高级别的主标题，重要性依次递减，h6为最低级别。这些标题不仅让内容层次分明，还能帮助搜索引擎和屏幕阅读器理解页面结构。例如，一篇文章的主标题可以用h1，章节标题用h2，小节用h3，以此类推。而p元素则用于定义段落，它会自动在前后形成换行，使文字成块显示，提升可读性。浏览器通常会对不同标题应用默认的字体大小和加粗样式，但这些外观可以通过CSS进一步定制。初学者应理解，使用正确的语义化标签比单纯追求视觉效果更重要，这有助于构建可访问、结构清晰的网页。"
      },
      {
        "level": 2,
        "description": "在实际开发中，标题和段落元素经常组合使用来构建内容区块。例如，在一个新闻页面中，h1可能用于整个网站的名称或当前文章的主标题，随后用h2展示各个新闻板块的标题，如‘国内新闻’、‘国际新闻’等，再用h3表示具体新闻条目的标题。每个新闻条目下方则紧跟一个或多个p元素，用于展示新闻正文。这种层级结构不仅便于用户快速浏览，也利于搜索引擎优化（SEO）。值得注意的是，虽然可以跳过某个级别的标题（比如从h1直接到h3），但不推荐这样做，因为这会破坏文档的逻辑结构。此外，p元素内部只能包含短语内容（如文本、链接、强调标签等），不能嵌套其他块级元素如div或另一个p。正确使用这些元素能确保网页结构严谨，为后续添加样式和交互打下良好基础。"
      },
      {
        "level": 3,
        "description": "深入理解标题和段落元素的作用，需要关注其在文档大纲（Document Outline）中的角色。HTML5引入了更复杂的结构模型，允许通过section、article等元素划分内容区域，每个区域都可以拥有自己的标题层级。这意味着在一个section内，即使使用h1，也不会与页面其他部分的h1冲突，浏览器会根据上下文自动计算标题级别。然而，并非所有浏览器都完全支持这一特性，因此仍建议按照传统方式使用递进的标题级别。另外，p元素的闭合行为也很关键：如果在下一个块级元素出现前未显式关闭p标签，浏览器会自动补全，但这可能导致意外的布局问题。性能方面，大量不必要的p或h标签会增加DOM树的复杂度，影响渲染效率。因此，应仅在语义需要时才使用这些元素，避免为了样式而滥用标签。掌握这些机制有助于编写高效、兼容性强的HTML代码。"
      },
      {
        "level": 4,
        "description": "现在我们来完成一个综合练习，巩固对标题和段落的理解。假设你要创建一个关于‘前端学习指南’的网页，要求如下：首先使用h2作为页面主标题，内容为‘前端开发入门路径’；然后在下方添加一个h4作为副标题，内容为‘HTML、CSS与JavaScript基础’；最后，在副标题下方插入两个段落。第一个段落内容为‘学习前端开发的第一步是掌握HTML，它负责定义网页的结构。’第二个段落内容为‘接着通过CSS美化页面样式，并用JavaScript添加交互功能。’以下是示例代码：\n\n```html\n<h2>前端开发入门路径</h2>\n<h4>HTML、CSS与JavaScript基础</h4>\n<p>学习前端开发的第一步是掌握HTML，它负责定义网页的结构。</p>\n<p>接着通过CSS美化页面样式，并用JavaScript添加交互功能。</p>\n```\n\n这段代码展示了如何按逻辑顺序组织内容。注意标签的嵌套和顺序，确保结构清晰。你可以尝试修改标题级别或添加更多段落，观察页面变化，从而加深对HTML语义结构的理解。"
      }
    ],
    "createTime": "2026-01-05 10:00:00",  
    "updateTime": "2026-01-05 12:00:00"
  },
  {
    "topic_id": "1_2",
    "title": "理解HTML列表元素ul、ol与li",
    "graphId": "萌宠乐园",
    "levels": [
      {
        "level": 1,
        "description": "列表元素在网页中用于组织有序或无序信息。ul表示无序列表，ol表示有序列表，而li表示列表项。通过合理使用列表，页面结构更清晰，信息更易理解。"
      },
      {
        "level": 2,
        "description": "在实际应用中，ul和ol常用来展示导航菜单、文章目录或步骤说明。每个li元素包含具体内容，可以是文本、链接甚至嵌套的列表。使用嵌套列表可以表现层级关系，但要注意不要过度嵌套，以免影响可读性。"
      },
      {
        "level": 3,
        "description": "HTML5中列表的语义化非常重要，搜索引擎和辅助工具可以更好地解析页面结构。良好的列表使用习惯包括避免空的li、控制嵌套深度以及配合CSS进行样式优化。"
      },
      {
        "level": 4,
        "description": "综合练习：创建一个购物清单网页，要求：使用ol展示购买步骤，使用ul展示购物物品，每个步骤和物品都包含li元素。确保结构清晰，并尝试嵌套子列表，观察显示效果。"
      }
    ],
    "createTime": "2026-01-05 10:00:00",  
    "updateTime": "2026-01-05 12:00:00"
  },
  {
    "topic_id": "1_3",
    "title": "使用HTML表格元素table、tr、td",
    "graphId": "萌宠乐园",
    "levels": [
      {
        "level": 1,
        "description": "表格元素用于显示二维数据，table定义表格，tr定义行，td定义单元格。合理使用表格可以让数据可视化和易读。"
      },
      {
        "level": 2,
        "description": "在实际开发中，表格常用于展示成绩单、商品清单或统计信息。可以通过thead、tbody、tfoot分别管理表头、表体和表尾。"
      },
      {
        "level": 3,
        "description": "HTML5允许表格嵌套、合并单元格（rowspan、colspan）以及使用caption描述表格内容。良好的语义化表格有助于屏幕阅读器和搜索引擎理解数据。"
      },
      {
        "level": 4,
        "description": "综合练习：创建一个学生成绩表格，要求包含姓名、科目和成绩列，并合并表头，实现表格可读性和可访问性。"
      }
    ],
    "createTime": "2026-01-05 10:00:00",  
    "updateTime": "2026-01-05 12:00:00"
  },
  {
    "topic_id": "1_4",
    "title": "理解HTML链接元素a及其属性",
    "graphId": "萌宠乐园",
    "levels": [
      {
        "level": 1,
        "description": "a元素用于创建超链接，href属性指向目标地址。正确使用链接可以让用户轻松在页面和网站之间导航。"
      },
      {
        "level": 2,
        "description": "在实际开发中，链接可以是内部页面跳转，也可以是外部网址。可通过target属性控制打开方式，通过rel属性增加安全性。"
      },
      {
        "level": 3,
        "description": "HTML5支持锚点链接和带参数的URL，配合id或name属性可以实现页面内跳转或特定内容定位。"
      },
      {
        "level": 4,
        "description": "综合练习：创建一个网站导航栏，包含首页、关于、联系页面链接，并设置外部链接在新窗口打开，同时保证语义化和可访问性。"
      }
    ],
    "createTime": "2026-01-05 10:00:00",  
    "updateTime": "2026-01-05 12:00:00"
  }
]

export default defineMock([
  // 查询知识点内容列表 - 对应 /api/v1/learning-content 路径
  {
    url: '/learning-content',
    method: ['GET'],
    body: ({ params }) => {
      const { pageNum = 1, pageSize = 10, title, status } = params;
      
      // 过滤数据
      let filteredContents = [...learningContents];
      // if (title) {
      //   filteredContents = filteredContents.filter(content => 
      //     content.title.toLowerCase().includes(title.toLowerCase())
      //   );
      // }
      // if (status !== undefined) {
      //   filteredContents = filteredContents.filter(content => 
      //     content.status === Number(status)
      //   );
      // }
      
      // 计算分页数据
      const total = filteredContents.length;
      const start = (Number(pageNum) - 1) * Number(pageSize);
      const end = start + Number(pageSize);
      const list = filteredContents.slice(start, end);
      
      return {
        code: "00000",
        data: {
          list,
          total
        }
      };
    }
  },
  //根据ID找到知识点内容 - 对应 /api/v1/learning-content/:id 路径
  {
  url: '/learning-content/:id',
  method: ['GET'],
  body: ({ query, params }) => {
    const { id } = params; // 获取路径参数 id
    // 找到对应的知识点
    const content = learningContents.find(item => item.topic_id === id);

    if (!content) {
      return {
        code: "404",
        message: "知识点未找到",
      };
    }

    return {
      code: "00000",
      data: content,
    };
  },
},
  // 获取知识点内容表单数据
  {
    url: '/learning-content/([^\\s/]+)/form',
    method: ['GET'],
    body: ({ url }) => {
      const id = url.match(/learning-content\/([^\/]+)\/form/)?.[1];
      const content = learningContents.find(item => item.id === Number(id));
      
      if (content) {
        return {
          code: SUCCESS_CODE,
          data: content
        };
      } else {
        return {
          code: ERROR_CODE,
          message: "知识点内容不存在"
        };
      }
    }
  },
  
  // 新增知识点内容
  {
    url: '/learning-content',
    method: ['POST'],
    body: ({ body }) => {
      const newId = Math.max(...learningContents.map(item => item.id), 0) + 1;
      const newContent = {
        ...body,
        id: newId,
        createTime: new Date().toISOString().slice(0, 19).replace('T', ' '),
        updateTime: new Date().toISOString().slice(0, 19).replace('T', ' ')
      };
      
      learningContents.push(newContent);
      
      return {
        code: SUCCESS_CODE,
        message: "新增成功"
      };
    }
  },
  
  // 修改知识点内容
  {
    url: '/learning-content/([^\\s/]+)',
    method: ['PUT'],
    body: ({ url, body }) => {
      const id = url.match(/learning-content\/([^\/]+)/)?.[1];
      const index = learningContents.findIndex(item => item.id === Number(id));
      
      if (index !== -1) {
        learningContents[index] = {
          ...learningContents[index],
          ...body,
          updateTime: new Date().toISOString().slice(0, 19).replace('T', ' ')
        };
        
        return {
          code: SUCCESS_CODE,
          message: "更新成功"
        };
      } else {
        return {
          code: ERROR_CODE,
          message: "知识点内容不存在"
        };
      }
    }
  },
  
  // 删除知识点内容
  {
    url: '/learning-content/([^\\s/]+)',
    method: ['DELETE'],
    body: ({ url }) => {
      const id = url.match(/learning-content\/([^\/]+)/)?.[1];
      const index = learningContents.findIndex(item => item.id === Number(id));
      
      if (index !== -1) {
        learningContents.splice(index, 1);
        
        return {
          code: SUCCESS_CODE,
          message: "删除成功"
        };
      } else {
        return {
          code: ERROR_CODE,
          message: "知识点内容不存在"
        };
      }
    }
  }
])