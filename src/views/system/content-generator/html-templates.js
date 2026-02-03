export const mockHtmlTemplate = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; line-height: 1.6; }
        .hero-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 0; text-align: center; }
        .content-section { padding: 60px 0; }
        .feature-card { border: none; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); transition: transform 0.3s ease; }
        .feature-card:hover { transform: translateY(-5px); }
        .knowledge-point { background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">{{PLATFORM_TITLE}}</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link active" href="#home">首页</a></li>
                    <li class="nav-item"><a class="nav-link" href="#learn">学习内容</a></li>
                    <li class="nav-item"><a class="nav-link" href="#practice">实践练习</a></li>
                    <li class="nav-item"><a class="nav-link" href="#about">关于</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- 首页横幅 -->
    <section id="home" class="hero-section">
        <div class="container">
            <h1 class="display-4 fw-bold mb-4">欢迎学习 {{KNOWLEDGE_NAME}}</h1>
            <p class="lead mb-4">通过系统化的学习路径，掌握核心概念和实践技能</p>
            <a href="#learn" class="btn btn-light btn-lg">开始学习</a>
        </div>
    </section>

    <!-- 学习内容 -->
    <section id="learn" class="content-section bg-light">
        <div class="container">
            <h2 class="text-center mb-5">学习内容</h2>
            <div class="row">
                <div class="col-md-4 mb-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <h5 class="card-title">基础概念</h5>
                            <p class="card-text">了解Vue.js的核心概念，包括响应式数据、组件化开发等基础知识。</p>
                            <a href="#" class="btn btn-primary">开始学习</a>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <h5 class="card-title">核心功能</h5>
                            <p class="card-text">掌握Vue.js的核心功能，包括指令系统、生命周期、计算属性等。</p>
                            <a href="#" class="btn btn-primary">开始学习</a>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <h5 class="card-title">高级特性</h5>
                            <p class="card-text">学习Vue Router、Vuex等高级特性，构建复杂的单页应用。</p>
                            <a href="#" class="btn btn-primary">开始学习</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 知识点列表 -->
            <div class="mt-5">
                <h3 class="mb-4">详细知识点</h3>
                {{KNOWLEDGE_POINTS}}
            </div>
        </div>
    </section>

    <!-- 页脚 -->
    <footer class="bg-dark text-white py-4">
        <div class="container text-center">
            <p>&copy; 2024 学习平台. 基于AI技术自动生成.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                var target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({behavior: 'smooth'});
                }
            });
        });
    </script>
</body>
</html>`;

export const mockCssTemplate = `/* 额外的样式文件 */
.hero-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 60vh;
    display: flex;
    align-items: center;
}

.navbar-brand {
    font-weight: bold;
    font-size: 1.5rem;
}

.card {
    transition: all 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.btn-primary {
    background-color: #667eea;
    border-color: #667eea;
}

.btn-primary:hover {
    background-color: #5a67d8;
    border-color: #5a67d8;
}`;