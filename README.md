# MiniCode

**MiniCode 是一个本地运行的多 Agent 编程助手。** 它保留 PM → Architect → Developer 流程，并把 Developer 从一次性代码文本生成升级为可多轮检查、编辑和执行项目任务的 Agent。

MiniCode 参考了当前 Codex 与 Claude Code 的公开 Agent 工作流：项目指令、工具调用、受控工作区、操作审批和可恢复会话。它是独立项目，不是 Codex 或 Claude Code 的官方实现。

[English README](README_EN.md) · [架构说明](docs/architecture.md) · [安全边界](docs/security.md) · [能力对照](docs/modernization.md) · [GitHub 上传清单](docs/github-upload.md)

## 当前能力

- **三阶段协作**：PM 生成 PRD，Architect 产出架构方案，Developer 在选定工作区直接实现代码。
- **双厂商 API**：OpenAI Responses API、Anthropic Messages API；也可用 OpenAI-compatible Chat Completions 服务。
- **项目上下文**：加载仓库根目录的 `AGENTS.md`、`CLAUDE.md`，以及 `.minicode/skills/*/SKILL.md`。
- **项目工具**：列目录、读文件、搜索文本、写文件、精确编辑、运行 shell 命令。
- **逐项审批**：写文件、编辑文件和执行命令默认询问；只有明确指定 `--yes` 才会自动批准。
- **会话恢复**：对话和工具结果存放在 `~/.minicode/sessions/`，可用会话 ID 继续工作。
- **产物**：代码写入选定工作区；PRD 和架构文档保存在 `~/.minicode/runs/<session-id>/`。

## 环境要求

- Python 3.11 或更高版本
- 一个可用的 OpenAI API、Anthropic API 或兼容服务账号
- 对 OpenAI-compatible 服务，需要提供支持工具调用的 Chat Completions 接口

## 安装

```bash
git clone https://github.com/quantumtool/minicode.git
cd minicode
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell：

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

### 从 GitHub 下载 wheel 安装

发布 `v0.2.0` 后，也可以直接安装 GitHub Release 中的通用 Python wheel（Python 3.11+）：

```bash
python -m pip install "https://github.com/quantumtool/minicode/releases/download/v0.2.0/minicode_agent-0.2.0-py3-none-any.whl"
```

安装后按下方说明配置模型凭据，然后运行 `minicode --help` 查看命令。Windows 用户可以在 PowerShell 中执行同一条安装命令。

## 配置模型

编辑本机的 `.env`，不要把真实密钥提交到 Git。MiniCode 依次读取当前工作目录的 `.env`、`~/.minicode/.env` 和源码仓库根目录的 `.env`；也可以用 `MINICODE_ENV_FILE` 指定单独配置文件。已有进程环境变量优先于文件内容。

### OpenAI Responses API

```dotenv
MINICODE_PROVIDER=openai
MINICODE_MODEL=<你的 OpenAI API 模型名>
MINICODE_OPENAI_API=responses
OPENAI_API_KEY=<你的 API key>
```

### Anthropic Messages API

```dotenv
MINICODE_PROVIDER=anthropic
MINICODE_MODEL=<你的 Anthropic API 模型名>
ANTHROPIC_API_KEY=<你的 API key>
```

### OpenAI-compatible 服务

```dotenv
MINICODE_PROVIDER=openai
MINICODE_MODEL=<服务支持的模型名>
MINICODE_OPENAI_API=chat_completions
OPENAI_API_KEY=<服务商 API key>
OPENAI_BASE_URL=<兼容服务的 API base URL>
```

模型名称由服务商账号和接口决定，MiniCode 不硬编码某个易过时的“最新模型”。OpenAI 官方 API 默认走 Responses API；配置自定义 `OPENAI_BASE_URL` 时默认改走 Chat Completions，也可显式选择接口模式。

可选运行设置：

```dotenv
MINICODE_MAX_TURNS=24
MINICODE_MAX_OUTPUT_TOKENS=8192
MINICODE_COMMAND_TIMEOUT=45
```

## 使用

在要修改的项目目录中运行：

```bash
minicode run "给登录页增加密码重置流程" --workspace .
```

也可以从源码目录运行：

```bash
python -m minicode run "创建一个待办事项 Web 应用" --workspace /path/to/project
```

只生成需求和架构文档，不调用 Developer 修改项目：

```bash
minicode plan "创建一个待办事项 Web 应用" --workspace .
```

查看本地会话并继续：

```bash
minicode sessions
minicode resume <session-id> "补上移动端布局并更新运行说明"
minicode forget <session-id>
```

每次写入和命令都会显示审批提示。`--yes` 会跳过这些提示：

```bash
minicode run "实现需求" --workspace /path/to/disposable-worktree --yes
```

`--yes` **不是沙箱**。shell 命令仍会以当前操作系统用户身份执行，并可能访问工作区外的文件、网络和凭证。只在一次性隔离环境中使用。

## 项目指令与技能

- `AGENTS.md`：Codex 风格项目说明。
- `CLAUDE.md`：Claude Code 风格项目说明。
- `.minicode/skills/<skill-name>/SKILL.md`：需要随项目共享的流程说明。

MiniCode 将这些内容作为模型上下文；操作审批仍由 MiniCode 工具层单独控制。不要在这些文件或源代码中存放 API 密钥。

## 开发

```bash
python -m pip install -e .
minicode --help
```

首次贡献前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 当前范围

MiniCode 已实现本地模型工具循环和基础权限提示，但没有 Codex 的沙箱、远程托管 Agent 或完整子 Agent 运行时，也没有 Claude Code 的完整权限规则、Hooks、MCP、插件、浏览器/电脑工具或原生 CLI 登录。详细对照见[能力对照](docs/modernization.md)与[安全边界](docs/security.md)。

## GitHub 凭证说明

仓库早期公开提交中包含过 `.env` 文件。当前版本会忽略本地密钥文件，但从当前版本删除文件不会清除历史提交中的内容。若旧值是真实密钥，请先在对应服务商处撤销并重发；重新发布前还应评估是否需要清理 Git 历史，见 [SECURITY.md](SECURITY.md)。
