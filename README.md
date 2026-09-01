<div align="center">

<img src="frontend/public/brand/animeclaw-mark.svg" alt="AnimeClaw" width="88" height="88"/>

# AnimeClaw · 漫剧工厂

**DramaClaw 负责把故事变成视频。**  
**AnimeClaw 负责让故事里的角色真正连续地活在视频里。**

单机自托管的 **AI 漫剧工作室**：从小说到成片走 DramaClaw 流水线，再用角色圣经、连续性检查、漫画镜头语言把长篇 IP 锁住。

作者：[yanhuaichuan](https://github.com/yanhuaichuan)

[![License](https://img.shields.io/badge/License-Elastic_2.0-blue.svg)](./LICENSES/Elastic-2.0.txt)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB)](./pyproject.toml)
[![GitHub](https://img.shields.io/badge/github-yanhuaichuan%2FAnimeClaw-ff7ab6)](https://github.com/yanhuaichuan/AnimeClaw)

**简体中文** · [English](#what-is-animeclaw)

[快速开始](#快速开始) · [产品地图](#产品地图) · [漫剧层](#漫剧层-anime-layer) · [架构](#架构原则) · [文档](#文档)

</div>

---

## 这不是又一个 AIGC 视频平台

AnimeClaw 是基于 [DramaClaw](https://github.com/dramaclaw/dramaclaw) 的**漫剧垂直二次开发**，不是从零再造一套生成平台。

DramaClaw Core 已经打通小说到成片：

```text
小说 → 故事解析 → 角色 → 分集 → 剧本 → 分镜 → 图片 → 声音 → 视频
```

AnimeClaw 在其上 **Reuse / Extend / Adapter**，增加漫剧生产层，而不是重写核心库、任务中心或模型网关：

```text
动漫世界 + 角色圣经 + 角色状态 + 画面连续性
+ 漫画镜头语言 + 演技引擎 + 风格锁 + 长篇 IP 记忆
```

产品目标：

> **让一个人可以连续生产几十集甚至几百集风格统一的 AI 漫剧。**

核心标准不是「生成一张动漫图」，而是：

> **第 1 集的白发、红眼、黑裙、左手红绳，到第 37 集必须还是同一个人。**

## 谁适合用

- 想把网文 / 短篇 / 原创设定做成**连续漫剧**的个人创作者
- 需要**同一角色跨几十集不崩**的小团队或工作室
- 已经会用 DramaClaw 流水线，想补上漫画镜头、演技和风格锁的人
- 希望**单机自托管、数据留在本地、自带模型 key** 的开发者

不适合：把本仓库直接做成对外 SaaS 转售（见 [许可](#许可)）。多租户、计费、团队协作属于企业能力，不在本仓。

## 产品地图

进入项目后，顶栏是 AnimeClaw 的工作台。内部路由键沿用 DramaClaw（如 `xiaji`），**用户看到的是漫剧词表**：

| 界面 | 做什么 | 打开方式 |
| --- | --- | --- |
| **漫剧** | 角色圣经、分镜、连续性、Animatic、导出 | 顶栏漫集菜单 → 漫剧，或 `/projects/$project/anime` |
| **漫画** | 无限画布：节点编排图 / 视频 / 音频 | 顶栏「漫画」 |
| **漫料** | 导入小说、解析章节 | 漫集 → 漫料 |
| **漫塘** | 角色、场景、道具资产库 | 漫集 → 漫塘 |
| **漫镜** | 分集剧本、草图、配音、视频、合成 | 漫集 → 漫镜 |
| **漫格** | 项目级风格模板与参考图 | 漫集 → 漫格 |
| **漫条** | 任务中心：进度、续跑、取消 | 底栏任务状态 |
| **漫导** | 对话式创作助手（按产品开关显示） | 漫集 → 漫导 |
| **漫驿** | 模型渠道 / 工作流路由 | 设置 → 模型配置 |

工作台还带深色 / 白色外观切换，以及可收缩的氛围歌单播放器（本地音频、直链、M3U / JSON；不自动播放）。

## 漫剧层（Anime Layer）

进入项目后打开顶部 **漫剧** 工作台。

### 第一阶段 MVP

1. 写入世界观 / 角色圣经 / 风格锁
2. 一键种子 **同一角色连续 10 镜 Demo**（苏璃：正面 → 侧面 → 跑步 → 战斗 → 受伤 → 哭泣 → 夜景 → 近景 → 全身 → 回头）
3. 在 Shot Editor 改表情、姿势、镜头，锁定角色 / 服装 / 场景 / 风格
4. 连续性检查 + 分层 Prompt
5. Animatic 预览（分镜 + 对白 + 时长，先验证再花成片钱）
6. 导出本集 JSON 资产包

后端全部落在 `{state_dir}/anime/`，**不改 DramaClaw 核心数据库，不重写 Task Center / Gateway**。

### 域模块

| 模块 | 职责 |
| --- | --- |
| `character_bible` | 外貌、服装、标志物，身份不得漂移 |
| `character_state` | 单集伤口、情绪、道具持有 |
| `scene_bible` / `style_bible` | 场景与画风锁 |
| `story_memory` / `plot_threads` | 长篇 IP 与线索记忆 |
| `camera_engine` | 漫画镜头语言 |
| `expression_engine` / `pose_engine` / `acting_engine` | 表情、姿势、演技计划 |
| `continuity_engine` / `anime_qa` | 跨镜一致性与质检 |
| `anime_prompt_builder` | 分层 Prompt |
| `anime_director` / `anime_pipeline` | 导戏建议、10 镜 Demo、导出 |

### REST（`/api/v1/anime`）

```text
GET  /catalog
GET|PUT  /projects/{project}/world
GET|PUT  /projects/{project}/style
GET      /projects/{project}/characters
GET|PUT  /projects/{project}/characters/{character}/bible
GET|PUT  /projects/{project}/scenes[/{scene}]
GET|PUT  /projects/{project}/episodes/{episode}/state
GET|PUT  /projects/{project}/episodes/{episode}/shots[/{shot}]
POST     /projects/{project}/episodes/{episode}/shots/{shot}/acting
POST     /projects/{project}/episodes/{episode}/shots/{shot}/prompt
POST     /projects/{project}/episodes/{episode}/continuity/check
POST     /projects/{project}/episodes/{episode}/director
GET      /projects/{project}/episodes/{episode}/preview
POST     /projects/{project}/episodes/{episode}/export
POST     /projects/{project}/demo/ten-shots
```

## 从小说到成片（DramaClaw Core）

AnimeClaw 完整继承社区版流水线，本机运行、BYO 模型 key，无需 PostgreSQL / Redis。

| 阶段 | 能力 |
| --- | --- |
| 导入 | 小说原稿 → 角色 / 关系 / 时间线知识图谱 |
| 剧本 | 分集、分场、台词、音效；改编 / 直译 / 分镜稿 |
| 资产 | 角色形象、道具三视图、场景库 |
| 画面 | 草图、首帧、风格模板 |
| 成片 | 逐镜视频 + TTS + 字幕合成导出 MP4 |
| 任务 | 长任务进度、断点续跑、取消（进程内执行） |

## 快速开始

### 前置

- **Docker**（试用 / 自托管，推荐）或 **Python 3.11–3.12** + [uv](https://docs.astral.sh/uv/) + Node 20+ + [pnpm](https://pnpm.io/)（本地开发）
- **ffmpeg / ffprobe**（Docker 镜像已带；本地开发需自行安装，见 [ffmpeg 指南](docs/zh/guides/ffmpeg.md)）
- 模型渠道：官方网关 DC key，或 CE 随附的本地 NewAPI

### Docker（推荐）

```bash
git clone https://github.com/yanhuaichuan/AnimeClaw.git
cd AnimeClaw

cp .env.example .env
# 至少把 PROMPT_EXPORT_PASSWORD 改成非默认值。模型 key 在网页里填，不要写进仓库。

docker compose up -d --build
docker compose ps    # api、web 均应 running
```

浏览器打开 **http://localhost:8080** → 设置 → **模型配置 → 官方渠道**，粘贴 DC key 并保存。CE 默认免登录、单本地用户。REST API 在 `http://localhost:8780`（浏览器只访问 `web`，由它反代到 `api`）。

自带上游网关时用 `docker compose -f docker-compose.selfhosted.yml up -d --build`，再在「本地 NewAPI」里配渠道。详见 [配置模型供应商](docs/zh/getting-started/configuring-models.md)。

### 本地开发

```bash
git clone https://github.com/yanhuaichuan/AnimeClaw.git
cd AnimeClaw
cp .env.example .env

uv sync --group dev
uv run novelvideo api --port 8780

cd frontend
pnpm install
pnpm dev          # Vite 默认 :5173，代理 /api/v1 与 /static 到 :8780
```

打开前端后：新建或进入项目 → 顶栏 **漫剧**。项目名可用中文（汉字、字母、数字、下划线，最长 64）。

## 架构原则

```text
Browser  :8080 / :5173
    │
    ▼
FastAPI  :8780          Anime Layer
 DramaClaw Core         Character / Scene / Shot
 Story · Asset · Task   Bible · Continuity · Camera
        └──────────┬──────────┘
                   ▼
         Anime Production Graph
         state/<user>/<project>/
           data.db          ← Core
           anime/*.json     ← AnimeClaw 文件存储
```

- **Reuse / Extend / Adapter**，禁止重写 Core
- AI 负责理解、规划、建议、生成；规则引擎负责状态、一致性、验证
- 重要状态必须可追踪：Character State / Scene State / Episode State / Plot Thread
- 单机 CE：任务在进程内执行，数据全在本地，模型走 OpenAI 兼容网关

更细的分层见 [架构说明](docs/zh/concepts/architecture.md)。

## 仓库结构

```text
src/novelvideo/     Python 引擎（FastAPI）
  api/              REST 路由（含 /api/v1/anime）
  anime/            角色圣经 / 连续性 / 漫画镜头 / 演技
  task_backend/     任务执行
  generators/       图 / 视频 / 音频适配
  freezone/         无限画布
  chat/             漫导
  ports/            端口与适配器（CE 默认实现）
frontend/           React 19 + Vite 工作台
tests/              pytest（默认不含 ee / e2e）
docs/zh · docs/en   安装、模型、自托管、排错
DESIGN.md           视觉规范（与 frontend/src/index.css 对齐）
```

## 开发与测试

```bash
uv run pytest                              # 默认测试集
uv run pytest tests/test_api_anime.py      # 漫剧 API
cd frontend && pnpm test                   # Vitest

pre-commit run --all-files                 # 含 gitleaks
```

`src/novelvideo/anime/` 对应规范 TASK-002 … TASK-014；`frontend/src/features/anime/` 对应 TASK-015 … TASK-018；`tests/test_anime_domain.py` / `tests/test_api_anime.py` 对应 TASK-019。

视觉改动请先读 [DESIGN.md](DESIGN.md)，并保持 `npx @google/design.md lint DESIGN.md` 为 0 errors。

安全：不要提交 provider key、签名 URL、`.env` 或 `frontend/state/` 本地库。模型走环境变量或网页「模型配置」。

## 文档

| 文档 | 内容 |
| --- | --- |
| [快速开始](docs/zh/getting-started/quickstart.md) | Docker 跑起来 |
| [安装指南](docs/zh/getting-started/installation.md) | macOS / Windows / Linux |
| [配置模型](docs/zh/getting-started/configuring-models.md) | 官方渠道 / 本地 NewAPI |
| [功能总览](docs/zh/concepts/features.md) | 流水线能力 |
| [架构](docs/zh/concepts/architecture.md) | 系统怎么运作 |
| [自托管](docs/zh/guides/self-hosting.md) | 部署 / 升级 / 备份 |
| [排错](docs/zh/guides/troubleshooting.md) | 常见故障 |
| [环境变量](docs/zh/reference/environment-variables.md) | 配置速查 |
| [贡献指南](CONTRIBUTING.md) | PR、DCO、行为准则 |
| [English docs](docs/en/README.md) | Same guides in English |

## 许可

沿用 DramaClaw / SuperTale CE 的 [Elastic License 2.0](./LICENSES/Elastic-2.0.txt)（**source available**，不是 OSI 开源）。

你可以：本地 / 自托管运行、修改二次开发、用它为客户交付作品。  
你不可以：把本软件作为托管服务提供给第三方（做成 SaaS 转售）。通俗说明见 [许可证文档](docs/zh/license.md)。

AnimeClaw 域代码作者为 **yanhuaichuan**。DramaClaw 商标与品牌资产仍归其原权利人。

---

<a name="what-is-animeclaw"></a>

## What is AnimeClaw?

AnimeClaw (**漫剧工厂**) is a **manga-drama vertical** on [DramaClaw](https://github.com/dramaclaw/dramaclaw) Core — not another from-scratch AIGC video site.

DramaClaw already runs **novel → parse → characters → episodes → script → boards → images → voice → video** on a single machine (no PostgreSQL / Redis). AnimeClaw adds, without rewriting Core, Task Center, or the model gateway:

- Character Bible, per-episode character state, scene / style lock
- Shot continuity and QA
- Manga camera language, expression / pose / acting plans
- Long-form IP memory and plot threads
- A 10-shot same-character demo (the first demo that actually matters)

The bar is not “generate an anime still”. It is: **the white hair, red eyes, black dress, and red string on the left wrist in episode 1 are still the same person in episode 37.**

### Product surfaces

| UI name | Role |
| --- | --- |
| **漫剧** Anime studio | Bible, shots, continuity, animatic, export (`/projects/$project/anime`) |
| **漫画** Canvas | Infinite node canvas |
| **漫料 / 漫塘 / 漫镜 / 漫格 / 漫条 / 漫导 / 漫驿** | Ingest, assets, episodes, styles, tasks, assistant, model gateway |

Anime state lives in `{state_dir}/anime/` as JSON. Core project data stays in local SQLite.

### Quick start

```bash
git clone https://github.com/yanhuaichuan/AnimeClaw.git
cd AnimeClaw
cp .env.example .env
docker compose up -d --build
# open http://localhost:8080 → Settings → model channel → paste your key
```

Local API: `uv sync --group dev && uv run novelvideo api --port 8780`. Frontend: `cd frontend && pnpm install && pnpm dev`.

Docs: [English documentation hub](docs/en/README.md). License: [Elastic License 2.0](./LICENSES/Elastic-2.0.txt). Author: **[yanhuaichuan](https://github.com/yanhuaichuan)** · <https://github.com/yanhuaichuan/AnimeClaw>
