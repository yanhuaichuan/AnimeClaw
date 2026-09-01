<div align="center">

# AnimeClaw · 漫剧工厂

**DramaClaw 负责把故事变成视频。**  
**AnimeClaw 负责让故事里的角色真正连续地活在视频里。**

作者：[yanhuaichuan](https://github.com/yanhuaichuan)

[![License](https://img.shields.io/badge/License-Elastic_2.0-blue.svg)](./LICENSES/Elastic-2.0.txt)
[![GitHub](https://img.shields.io/badge/github-yanhuaichuan%2FAnimeClaw-ff7ab6)](https://github.com/yanhuaichuan/AnimeClaw)

**简体中文** · [English](#what-is-animeclaw)

</div>

## 这不是又一个 AIGC 视频平台

AnimeClaw 是基于 [DramaClaw](https://github.com/dramaclaw/dramaclaw) 的**漫剧垂直二次开发**。

DramaClaw 已经打通：

```text
小说 → 故事解析 → 角色 → 分集 → 剧本 → 分镜 → 图片 → 声音 → 视频
```

AnimeClaw 在其上增加，而不是重写：

```text
动漫世界 + 角色圣经 + 角色状态 + 画面连续性
+ 漫画镜头语言 + 演技引擎 + 风格锁 + 长篇 IP 记忆
```

产品目标：

> **让一个人可以连续生产几十集甚至几百集风格统一的 AI 漫剧。**

核心标准不是「生成一张动漫图」，而是：

> **第 1 集的白发、红眼、黑裙、左手红绳，到第 37 集必须还是同一个人。**

## 第一阶段 MVP

进入项目后打开顶部 **漫剧** 工作台，或访问 `/projects/$project/anime`。

1. 写入世界观 / 角色圣经 / 风格锁  
2. 一键种子 **同一角色连续 10 镜 Demo**（苏璃：正面 → 侧面 → 跑步 → 战斗 → 受伤 → 哭泣 → 夜景 → 近景 → 全身 → 回头）  
3. 在 Shot Editor 改表情、姿势、镜头，锁定角色 / 服装 / 场景 / 风格  
4. 连续性检查 + 分层 Prompt  
5. Animatic 预览（分镜 + 对白 + 时长，先验证再花成片钱）  
6. 导出本集 JSON 资产包  

后端全部落在 `{state_dir}/anime/`，**不改 DramaClaw 核心数据库，不重写 Task Center / Gateway**。

```text
POST /api/v1/anime/projects/{project}/demo/ten-shots
GET  /api/v1/anime/projects/{project}/characters/{character}/bible
POST /api/v1/anime/projects/{project}/episodes/{episode}/continuity/check
GET  /api/v1/anime/projects/{project}/episodes/{episode}/preview
POST /api/v1/anime/projects/{project}/episodes/{episode}/export
```

## 快速开始

```bash
git clone https://github.com/yanhuaichuan/AnimeClaw.git
cd AnimeClaw

cp .env.example .env
# 配置模型网关，和 DramaClaw 相同：MODEL / NEWAPI_*

uv sync --group dev
uv run novelvideo api --port 8780

# 前端
cd frontend && pnpm install && pnpm dev
```

或 Docker：

```bash
docker compose up -d --build
```

打开 http://localhost:8080 ，进入项目 → **漫剧**。

## 架构原则

```text
DramaClaw Core          Anime Layer
Story / Asset / Task    Character / Scene / Shot
        └──────────┬──────────┘
                   ▼
         Anime Production Graph
```

- **Reuse / Extend / Adapter**，禁止重写 Core  
- AI 负责理解、规划、建议、生成；规则引擎负责状态、一致性、验证  
- 重要状态必须可追踪：Character State / Scene State / Episode State / Plot Thread  

## 开发任务对照

`src/novelvideo/anime/` 对应规范 TASK-002 … TASK-014

`frontend/src/features/anime/` + `/projects/$project/anime` 对应 TASK-015 … TASK-018

`tests/test_anime_domain.py` / `tests/test_api_anime.py` 对应 TASK-019

## 许可

沿用 DramaClaw / SuperTale CE 的 [Elastic License 2.0](./LICENSES/Elastic-2.0.txt)。  
AnimeClaw 域代码作者为 **yanhuaichuan**。DramaClaw 商标与品牌资产仍归其原权利人。

---

<a name="what-is-animeclaw"></a>

## What is AnimeClaw?

AnimeClaw is not a from-scratch AIGC video platform. It is a **manga-drama vertical** on DramaClaw Core: Character Bible, shot continuity, manga camera language, acting plans, style lock, and long-form IP memory.

The first demo that matters is **the same character across 10 shots**.

Author: **yanhuaichuan** · Repo: https://github.com/yanhuaichuan/AnimeClaw
