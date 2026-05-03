# MiniCode

MiniCode 是一个以最小可行形式（MVP）实现的 **Multi-Agent 驱动 AI Coding Agent 工具**。

它模拟一个完整的软件开发团队（产品经理 / 架构师 / 工程师），
将用户的自然语言需求自动转化为可运行的项目代码。

---

## ✨ 核心特性

* 🤖 多 Agent 协作（PM / Architect / Developer）
* 🧠 基于大模型自动生成需求与架构
* 🏗 自动生成项目代码（支持文件拆分为真实文件）
* ⚡ 从想法到代码的一键生成流程

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/quantumtool/minicode.git
cd minicode
```

---

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

---

### 4. 配置环境变量

在项目根目录 `.env` 文件中填入你的大模型API KEY：

```env
OPENAI_API_KEY=你的API_KEY
OPENAI_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat
```

---

### 5. 运行项目

```bash
python main.py "你的产品需求"
```

示例：

```bash
python main.py "做一个待办事项 Web 应用"
```

---

## 📁 项目结构

```
minicode/
├── main.py              # 程序入口
├── minicode/
│   ├── agents/         # 多 Agent 实现
│   ├── team.py         # Agent 调度
│   ├── llm.py          # 大模型调用
│   └── workspace.py    # 文件生成
├── outputs/            # 自动生成项目
├── requirements.txt
└── README.md
```

---

## 🧠 系统架构

MiniCode 采用顺序式 Multi-Agent Pipeline：

```
User Input
   ↓
PM Agent（需求分析）
   ↓
Architect Agent（架构设计）
   ↓
Developer Agent（代码生成）
   ↓
Project Output（真实文件）
```

---

## 📦 输出结果

运行后生成在：

```
outputs/时间戳_项目名/
```

包含：

* `prd.md`（需求文档）
* `architecture.md`（架构设计）
* `app/`（生成的真实项目代码）

---

## 🔥 未来计划

* [ ] 多 Agent 并行协作（Multi-Agent System）
* [ ] 自动运行与报错修复（Self-Healing）
* [ ] Web UI 界面
* [ ] 工具链集成（Shell / Git / Browser）

---

## ⚠️ 注意事项

* `.env` 文件不会上传到 GitHub（已加入 `.gitignore`）
* 请妥善保管 API Key
* 首次运行建议使用简单需求测试

---

## 📌 项目定位

MiniCode 不是一个完整产品，而是一个：

> 👉 面向 Multi-Agent AI 编程范式的最小原型系统

---

## 👨‍💻 Author

* Huang Chenlin
