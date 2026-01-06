// src/api/aiConfig.ts

// 模拟后端数据库
let mockAIConfig = {
  tutor_openai_api_key: 'sk-demo-123456',
  tutor_openai_model: 'gpt-4o',
  tutor_openai_api_base: 'https://api.openai.com/v1',

  tutor_embedding_api_key: 'sk-embed-demo',
  tutor_embedding_api_base: 'https://api.embedding.com/v1',
  tutor_embedding_model: 'Qwen/Qwen3-Embedding-4B',

  tutor_translation_api_key: 'sk-trans-demo',
  tutor_translation_api_base: 'https://api.translate.com/v1',
  tutor_translation_model: 'Qwen/Qwen3-30B-A3B-Instruct',

  enable_rag_service: true,
  enable_sentiment_analysis: true,
  enable_clustering_service: false,
  enable_translation_service: true
}

/**
 * 获取 AI 配置（模拟接口）
 */
export function getAIConfig() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        code: 200,
        message: 'success',
        data: { ...mockAIConfig }
      })
    }, 400)
  })
}

/**
 * 更新 AI 配置（模拟接口）
 */
export function updateAIConfig(data: Record<string, any>) {
  return new Promise((resolve) => {
    setTimeout(() => {
      mockAIConfig = {
        ...mockAIConfig,
        ...data
      }

      resolve({
        code: 200,
        message: '配置更新成功'
      })
    }, 400)
  })
}
