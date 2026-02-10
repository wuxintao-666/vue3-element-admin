# 课程生成 WebSocket API 使用说明

## 概述

这是一个基于 FastAPI 的 WebSocket API，用于实时生成课程内容。支持实时进度推送、内容生成和用户确认保存。

## WebSocket 端点

```
ws://localhost:8000/ws/generate-course
```

## 使用流程

### 1. 建立连接

客户端建立 WebSocket 连接后，立即发送初始请求：

```json
{
  "knowledge_graph": {
    "nodes": [...],
    "edges": [...]
  },
  "config": {
    "knowledge_graph_file": "data/knowledge/xxx.json"  // 可选
  }
}
```

### 2. 接收进度推送

服务器会推送以下类型的消息：

#### 连接确认
```json
{
  "type": "request_received",
  "task_id": "uuid",
  "message": "请求已接收，开始生成课程..."
}
```

#### 阶段开始
```json
{
  "type": "stage_start",
  "task_id": "uuid",
  "stage": "html_generation",
  "progress": 0,
  "message": "开始生成全局教学HTML..."
}
```

#### 阶段完成
```json
{
  "type": "stage_complete",
  "task_id": "uuid",
  "stage": "html_generation",
  "progress": 20,
  "message": "全局HTML生成完成",
  "data": {
    "html_preview": "...",
    "html_length": 1234
  }
}
```

#### 项目完成（单个知识点或章节）
```json
{
  "type": "item_complete",
  "task_id": "uuid",
  "stage": "knowledge_generation",
  "progress": 45,
  "message": "已完成 5/17 个知识点",
  "data": {
    "item": {
      "id": "1_1",
      "title": "HTML基础"
    },
    "completed": 5,
    "total": 17
  }
}
```

#### 生成完成
```json
{
  "type": "generation_complete",
  "task_id": "uuid",
  "progress": 100,
  "message": "课程生成完成，等待确认",
  "data": {
    "html": "...",
    "knowledge_base": "...",
    "knowledge_points": [...],
    "chapters": [...],
    "summary": {
      "knowledge_count": 17,
      "chapter_count": 4,
      "main_dir": "ai_generation_content/uuid"
    }
  }
}
```

#### 错误消息
```json
{
  "type": "error",
  "task_id": "uuid",
  "message": "生成失败: 错误信息",
  "error": "详细错误堆栈"
}
```

### 3. 用户确认

生成完成后，用户编辑内容，然后发送确认消息：

```json
{
  "type": "confirm",
  "data": {
    "html": "编辑后的HTML",
    "knowledge_points": [...],
    "chapters": [...]
  }
}
```

服务器响应：
```json
{
  "type": "confirmed",
  "task_id": "uuid",
  "message": "内容已确认，保存成功"
}
```

### 4. 取消生成

用户可以随时发送取消消息：

```json
{
  "type": "cancel"
}
```

## 前端示例代码

### Vue 3 示例

```typescript
import { ref, onMounted, onUnmounted } from 'vue'

export function useCourseGeneration() {
  const ws = ref<WebSocket | null>(null)
  const progress = ref(0)
  const stage = ref('')
  const message = ref('')
  const courseData = ref<any>(null)
  const isComplete = ref(false)
  
  const connect = (knowledgeGraph: any, config: any = {}) => {
    return new Promise((resolve, reject) => {
      ws.value = new WebSocket('ws://localhost:8000/ws/generate-course')
      
      ws.value.onopen = () => {
        // 建立连接后立即发送初始请求
        ws.value!.send(JSON.stringify({
          knowledge_graph: knowledgeGraph,
          config: config
        }))
        resolve(true)
      }
      
      ws.value.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        switch(data.type) {
          case 'request_received':
            console.log('请求已接收，开始生成...')
            break
          
          case 'stage_start':
            stage.value = data.stage
            message.value = data.message
            progress.value = data.progress
            break
          
          case 'item_complete':
            progress.value = data.progress
            message.value = data.message
            console.log('完成项目:', data.data.item)
            break
          
          case 'generation_complete':
            isComplete.value = true
            courseData.value = data.data
            message.value = '生成完成，请确认内容'
            break
          
          case 'error':
            console.error('生成错误:', data.message)
            reject(new Error(data.message))
            break
        }
      }
      
      ws.value.onerror = (error) => {
        reject(error)
      }
    })
  }
  
  const confirm = async (editedData: any) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket未连接')
    }
    
    ws.value.send(JSON.stringify({
      type: 'confirm',
      data: editedData
    }))
    
    return new Promise((resolve) => {
      const handler = (event: MessageEvent) => {
        const data = JSON.parse(event.data)
        if (data.type === 'confirmed') {
          ws.value!.removeEventListener('message', handler)
          resolve(data)
        }
      }
      ws.value!.addEventListener('message', handler)
    })
  }
  
  const cancel = () => {
    if (ws.value) {
      ws.value.send(JSON.stringify({ type: 'cancel' }))
      ws.value.close()
    }
  }
  
  onUnmounted(() => {
    if (ws.value) {
      ws.value.close()
    }
  })
  
  return {
    connect,
    confirm,
    cancel,
    progress,
    stage,
    message,
    courseData,
    isComplete
  }
}
```

## 消息类型说明

| 类型 | 说明 | 方向 |
|------|------|------|
| `request_received` | 请求已接收 | 服务器→客户端 |
| `stage_start` | 阶段开始 | 服务器→客户端 |
| `stage_complete` | 阶段完成 | 服务器→客户端 |
| `item_start` | 单个项目开始 | 服务器→客户端 |
| `item_complete` | 单个项目完成 | 服务器→客户端 |
| `item_error` | 单个项目错误 | 服务器→客户端 |
| `generation_complete` | 生成完成 | 服务器→客户端 |
| `error` | 错误 | 服务器→客户端 |
| `confirm` | 用户确认 | 客户端→服务器 |
| `confirmed` | 确认成功 | 服务器→客户端 |
| `cancel` | 取消生成 | 客户端→服务器 |
| `cancelled` | 已取消 | 服务器→客户端 |

## 注意事项

1. **连接管理**：每个连接都有唯一的 `task_id`，用于标识生成任务
2. **进度推送**：服务器会实时推送生成进度，客户端应更新UI
3. **数据大小**：生成完成时会推送完整数据，可能较大，注意处理
4. **错误处理**：应妥善处理各种错误情况
5. **连接断开**：客户端断开连接时，服务器会清理资源

## 启动服务

```bash
cd backend
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 测试

可以使用 WebSocket 客户端工具测试，如：
- Postman
- wscat
- 浏览器控制台

示例（浏览器控制台）：
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/generate-course')
ws.onopen = () => {
  ws.send(JSON.stringify({
    knowledge_graph: { nodes: [], edges: [] },
    config: {}
  }))
}
ws.onmessage = (event) => {
  console.log('收到消息:', JSON.parse(event.data))
}
```
