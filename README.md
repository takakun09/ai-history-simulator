# AI 历史人物模拟器（Demo）

一个教育场景的 AI 应用原型：**AI 扮演"有立场、可能带偏见的历史人物"**，
学生在对话中追问、质疑，再对照史料自己去判断——训练的是「历史思维」，
而不是「记住史实」。

## 快速开始（零依赖）

需要 Python ≥ 3.11，**无需安装任何第三方包**：

```bash
cd new-chat
python3 -m src.app.server
```

然后打开浏览器：**http://127.0.0.1:8777**

- 学生端：`/`
- 教师端：`/teacher`

## 功能

### 学生端
- 首页展示已发布的历史人物卡片（默认 3 位：诸葛亮、苏格拉底、林肯），每人一张手绘卡通形象。
- 点击卡片 → 进入**对话子页面**：干净清爽的对话框。
- 对话框下方可选择 **API 接口**（离线演示 / OpenAI 兼容 / 本地 Ollama / Anthropic Claude），
  可填模型名、Base URL、API Key（**密钥只存在你自己浏览器的 localStorage，不上传服务器**）。
- 「＋ 新对话」重置会话；右侧面板列出该人物的**可查证史料**与**建议问题**。

### 教师端
- 与学生端相同的对话能力（可点「以学生身份测试」）。
- 管理历史人物：**新建 / 修改 / 删除 / 发布**。
- 核心是编辑 **「限制词 / system prompt」**——即 AI 扮演该人物的行为约束；
  还可编辑时代、开场白、史料清单、建议问题、主题色、形象路径。
- 「保存并发布」后，学生端立即生效。

## API 接口选项

| 接口 | 说明 | 需要 Key |
| --- | --- | --- |
| 离线演示 | 不调用任何模型，返回模拟回复，方便无网演示 | 否 |
| OpenAI 兼容 | OpenAI / DeepSeek / 通义 / 智谱 等，填对应 Base URL 与模型名 | 是 |
| 本地 Ollama | `http://localhost:11434/v1`，需本机已运行 Ollama | 否 |
| Anthropic Claude | 走 Messages API | 是 |

> 提示：把 Base URL 换成任意 OpenAI 兼容服务（如 DeepSeek `https://api.deepseek.com/v1`）即可对接。

## 目录结构

```
new-chat/
├── AGENTS.md              # 项目协作规范
├── pyproject.toml
├── src/app/
│   ├── server.py          # 零依赖 HTTP 服务（静态前端 + API）
│   ├── store.py           # 人物数据持久化（data/figures.json）
│   ├── providers.py       # 多厂商 LLM 接口适配
│   └── seed.py            # 3 个默认人物（含限制词）
├── web/
│   ├── index.html         # 学生端首页
│   ├── chat.html          # 对话子页面
│   ├── teacher.html       # 教师端
│   └── assets/            # 样式、脚本、卡通形象（SVG）
├── data/figures.json      # 运行时生成
└── tests/test_app.py      # 单元测试
```

## 测试

```bash
python3 -m unittest discover -s tests -v
```

## 说明与边界

- **不训练模型**：本项目是「自研前端 + 预训练模型接口 + 提示工程」。
- 人物卡通形象为**手工 SVG**（可替换）。
- 对话数据目前**不落库**，刷新页面即清空；人物配置存于 `data/figures.json`。
- 历史人物为**教学模拟**，允许展现立场与时代局限，不代表史实定论。
