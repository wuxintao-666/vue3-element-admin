# 魔搭(ModelScope)平台配置指南

本项目现已支持魔搭(ModelScope)平台，您可以按照以下步骤进行配置。

## 配置步骤

1. 获取魔搭平台Token
   - 访问 [魔搭平台](https://www.modelscope.cn/)
   - 登录后进入个人中心获取API Token

2. 配置环境变量
   - 复制 `.env.example` 文件为 `.env`
   - 将获取的Token填入 `MODELSCOPE_API_KEY` 字段
   - 如需修改其他配置，请参考 `.env.example` 中的说明

3. 运行项目
   - 后端：`python main.py`
   - 前端：`npm run dev`

## 支持的模型

本项目默认使用以下模型：
- 快速模型：`Qwen/Qwen2.5-7B-Instruct`
- 慢速模型：`deepseek-ai/DeepSeek-V3.2`
- 执行器模型：`deepseek-ai/DeepSeek-V3.2`

您可以根据需要在 `.env` 文件中修改这些配置。

## 注意事项

- 魔搭平台的API调用支持 `enable_thinking` 参数，可开启模型的推理过程输出
- 如需启用推理过程，请在 `.env` 文件中设置相应模型支持该功能
- 模型调用时会自动添加 `extra_body={"enable_thinking": True}` 参数以启用推理功能