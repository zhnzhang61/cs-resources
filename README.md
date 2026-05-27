# AI Resources

我零零散散收集的 AI 相关资源截图，按主题分类整理。每条都附原图缩略图 + 原始链接（搜得到的尽量给到一手来源；只看到二手转载的标 `[二手]`；信息不够找的标 `TBD`）。

> 索引建于 2026-05-27，共 24 张图。

---

## 目录

1. [自己的设计稿 / 笔记](#1-自己的设计稿--笔记)
2. [Transformer / 基础原理 科普图](#2-transformer--基础原理-科普图)
3. [ML 系统 / AI Infra 知识图谱](#3-ml-系统--ai-infra-知识图谱)
4. [Agent 框架与架构](#4-agent-框架与架构)
5. [Claude / Claude Code 生态](#5-claude--claude-code-生态)
6. [RL / Agentic-RL 项目](#6-rl--agentic-rl-项目)
7. [本地模型 / 模型发布](#7-本地模型--模型发布)
8. [AI 工具](#8-ai-工具)
9. [书 / 课](#9-书--课)
10. [面试 / 求职](#10-面试--求职)
11. [写作 / 商业 视角](#11-写作--商业-视角)
12. [Meme / 趣图](#12-meme--趣图)

---

## 1. 自己的设计稿 / 笔记

### 1.1 个人记忆架构手写图（PersonalCoach 相关）

<img src="images/personal-memory-architecture-handnote.png" width="420">

- **来源**：自己在 Apple Notes "Computer Science Notebook" 里画的草图，2026-04-12 09:52
- **内容**：Agent 三种 memory 的关系图——Semantic Memory（user info）/ Episodic Memory（summary of what's actually going on）/ Procedural Memory（know-how / real world）；连线 Conversation、Action、Feedback、Function、Preference
- **链接**：本地手稿，无外链

### 1.2 个人 Agent 架构图

<img src="images/personal-agent-architecture-diagram.png" width="420">

- **来源**：自己画的 Agent 系统分层图
- **内容**：User & Interaction Layer（MacOS/iOS/iPadOS、Human-in-the-Loop）→ Agent Framework / Orchestration（Manager Supervisor、Study Assistant、Financial Advisor、Running Agent）→ Call Model（Multi-modal VLM/LLM Reasoning Loop、Local MLX / Remote Cloud Inference）→ Capabilities & Context（Memory & Data Management、MCP Tools Hub、LoRA Fine-tuning、RL）→ Engineering Flow / Infrastructure Base（MLX on Mac/PC、Git-like Rollback）
- **链接**：自己的设计稿，无外链

---

## 2. Transformer / 基础原理 科普图

四张 10 宫格中文长图，同一作者风格，是我见过把 Transformer 讲得最直观的一组（金句 + 类比图 + 小总结）。一手作者 TBD，多半出自小红书/公众号同一账号。

### 2.1 Transformer / BERT / GPT 是什么关系

<img src="images/infographic-transformer-bert-gpt.jpg" width="420">

- 10 panel：核心定位、为什么容易混、GPT 走哪条路、BERT 走哪条路、为啥现在更常听到 GPT、它们各分支演化、"现在的大模型"到底是怎么来的、一句话三者关系总结
- 链接：TBD（科普长图，未在搜索中定位到原账号）

### 2.2 Transformer 不只是 Attention：FFN / 残差 / 归一化在干啥

<img src="images/infographic-transformer-ffn-residual-norm.jpg" width="420">

- 10 panel：为什么不只有 attention、为什么只靠 attention 不够、FFN 到底做什么、为什么 FFN 这么重要、残差链接在哪里、归一化又干嘛、一个完整 Transformer block 长啥样、为什么这些组件一起出现效果会更强、人为什么会相信 attention、最后总结
- 链接：TBD

### 2.3 为什么 Transformer 要用多头注意力

<img src="images/infographic-multi-head-attention.jpg" width="420">

- 10 panel：单头不够的原因、多头注意力到底是什么、多个分头看入话是什么、为什么要把投影到不同空间、多头注意力到底带来了什么能力提升、是不是头越多越好、多头最后怎么汇总、为什么 Transformer 设计重要在多头、最后总结
- 链接：TBD

### 2.4 Q / K / V 为什么不是故弄玄虚

<img src="images/infographic-qkv-attention.jpg" width="420">

- 10 panel：把 attention 拆成"找谁/拿什么"、为什么不能只用一组表示、Q / K / V 各是什么、为什么要拆成三套、Q K V 是不是三个完全不同的东西、为什么这套设计会让 attention 更强、最后总结
- 链接：TBD（小红书 ID 在图右下：3603020...，需要原作者确认）

---

## 3. ML 系统 / AI Infra 知识图谱

### 3.1 LLM 量化全景图（PTQ / QAT / FP4 / TP-PP-DP）

<img src="images/mindmap-llm-quantization.jpg" width="420">

- **内容**：量化基础（FP32/FP16/BF16 → INT8/INT4/FP4/FP8）、PTQ vs QAT、主流 PTQ 算法（SmoothQuant、GPTQ、AWQ、FP8、FP4/NVFP4）、大模型量化难点、量化 + 分布式（TP/PP/DP）、推理引擎（vLLM / SGLang / TensorRT-LLM / DeepSpeed-MII）、岗位边界
- 小红书 ID：961198512...（图右下）
- 链接：TBD（原小红书帖未在搜索中定位）

### 3.2 AI Infra 全栈思维导图

<img src="images/mindmap-ai-infra-stack.jpg" width="420">

- **内容**：底层硬件与异构计算（NVLink/CXL/RDMA/InfiniBand）、分布式训练系统（DeepSpeed/Megatron/FSDP）、高效推理引擎（Triton/vLLM/TGI）、云原生与算力调度（K8s/KubeFlow）、数据与存储（Milvus/FAISS）、MLOps/LLMOps、AI 安全与隐私计算、新兴方向（Agent Infra、TVM/MLIR、绿色 AI）
- 小红书 ID：568858672...
- 链接：TBD

---

## 4. Agent 框架与架构

### 4.1 Claude Agent SDK vs LangChain / LangGraph 对比表

<img src="images/claude-agent-sdk-vs-langchain.jpg" width="420">

- **内容**：核心对比表（2025–2026 社区共识），维度包括主要目标、模型支持、抽象层级、Agent Loop、工具/集成、上下文管理、生产可靠性、多 Agent 支持、开发体验、最佳场景、缺点、2026 年社区观点
- **链接**：TBD（ChatGPT 输出截图，原对话不可索引）

### 4.2 Minimal / Goal-Aware / Autonomous Agent Loop 三者结构对比

<img src="images/chatgpt-agent-loop-comparison.jpg" width="420">

- **内容**：ChatGPT 对话截图——比较三种 Agent 架构在闭环 / Goal 检测 / 规划 / 记忆 / 生命周期五个维度上的差异（Minimal：只闭环；Goal-Aware：加目标驱动；Autonomous：全开 + 内部控制）
- **链接**：ChatGPT 对话，无公开链接

### 4.3 openai/openai-agents-python（GitHub）

<img src="images/github-openai-agents-python.jpg" width="420">

- **内容**：OpenAI 官方多 Agent 框架仓库截图，21.8k stars。看点：`.agents/skills/`、`.codex/`、`AGENTS.md`、`CLAUDE.md`、`PLANS.md`
- **链接**：<https://github.com/openai/openai-agents-python>
- **文档**：<https://openai.github.io/openai-agents-python/>

---

## 5. Claude / Claude Code 生态

### 5.1 「我常雇佣的十大 Claude Skills」

<img src="images/xhs-top-10-claude-skills.png" width="420">

- **作者**：小红书 @羊拱机树
- **内容**：10 个常用 Claude Skills——Rube MCP Connector、Superpowers、Document Suite、Theme Factory、Algorithmic Art、Slack GIF Creator、Webapp Testing、MCP Builder、Brand Guidelines、Systematic Debugging
- **链接**：TBD（小红书原帖未拿到 share link）

---

## 6. RL / Agentic-RL 项目

### 6.1 RL & Agentic-RL 项目推荐（4 个）

<img src="images/xhs-rl-agentic-rl-projects.png" width="420">

- **作者**：小红书 @RLer
- **内容**：四个开源、能装到简历的项目
  1. **TinyZero** — 最小可复现的 DeepSeek-R1 思维链涌现：<https://github.com/Jiayi-Pan/TinyZero>（框架：verl）
  2. **Search-R1** — Agentic-RL 开山鼻祖，提升 LLM 调用搜索引擎能力：<https://github.com/PeterGriffinJin/Search-R1>（verl）
  3. **ReTool** — 字符级 RL 引导 LLM 用外部计算工具完成推理：<https://github.com/ReTool-RL/ReTool>（verl + 代码沙箱）
  4. **RLVER** — 腾讯多轮场景用户模拟器 + 奖励裁判：<https://github.com/Tencent/digitalhuman/tree/main/RLVER>（论文 <https://arxiv.org/abs/2507.03112>）

---

## 7. 本地模型 / 模型发布

### 7.1 Gemma 4 E4B + Opus Reasoning + Claude Code（融合本地模型）

<img src="images/xhs-gemma4-e4b-local-claude.png" width="420">

- **作者**：小红书 @小红薯 F2E86FAF
- **内容**：Gemma 4 E4B + Opus 推理 + Claude Code LoRA 已合并入权重的 mlx-4bit 模型，10.5 GB，可配合 OpenHarness / OpenClaw / Hermes Agent 跑全本地 Agent
- **链接**：
  - HuggingFace 模型：<https://huggingface.co/deadbydawn101/gemma-4-E4B-Agentic-Opus-Reasoning-GeminiCLI-mlx-4bit>
  - Gemma 4 官方介绍：<https://huggingface.co/blog/gemma4>
  - OpenClaw + Gemma 4 配置教程：<https://lushbinary.com/blog/openclaw-gemma-4-local-ai-agent-ollama-setup-guide-2026/>
  - Claude Code + Gemma 4 实测：<https://medium.com/@tentenco/i-tried-gemma-4-on-claude-code-and-found-googles-free-coding-beast-e1618fc808c3>

### 7.2 Qwen3.6-35B-A3B 发布

<img src="images/xhs-qwen3-6-35b-a3b-release.png" width="420">

- **作者**：小红书 @千问大模型 (Qwen 官方)
- **内容**：Qwen3.6-35B-A3B 开源——MoE 架构，350 亿总参数，30 亿激活，256 内部专家，每次推理激活 8 路由 + 1 共享。SWE-bench Pro 64.3，超越 GPT-5.4 / Gemini 3.1 Pro。Hugging Face / ModelScope 都有，阿里云 Bailian API `qwen3.6-flash`
- **链接**：
  - 知乎深度解析：<https://zhuanlan.zhihu.com/p/2029254385411137922>
  - IT之家发布报道：<https://www.ithome.com/0/940/079.htm>
  - 模型 datacard：<https://www.datalearner.com/ai-models/pretrained-models/qwen3-6-35b-a3b>

---

## 8. AI 工具

### 8.1 markitdown — 把一切转 markdown

<img src="images/xhs-markitdown-intro.png" width="420">

- **作者**：小红书 @朱卫军 AI
- **内容**：Microsoft 出品，把 pdf / ppt / word / excel / 图 / 音 / 视频转 markdown，喂给 AI 模型解析更省 token；GitHub 9 万 star
- **链接**：<https://github.com/microsoft/markitdown>

### 8.2 llmfit — 一行命令告诉你电脑能跑哪个本地模型

<img src="images/xhs-llmfit-local-model-tool.png" width="420">

- **作者**：小红书 @11111
- **内容**：自动检测 CPU / RAM / GPU / VRAM，按"质量、速度、适配度、上下文长度"打分；支持 Ollama / llama.cpp / MLX 三大本地推理框架，含 TUI 界面
- **链接**：
  - GitHub：<https://github.com/AlexsJones/llmfit>
  - 官网：<https://www.llmfit.org/>

### 8.3 Lightpanda — AI 自动化无头浏览器

<img src="images/xhs-lightpanda-headless-browser.jpg" width="420">

- **来源**：小红书 @Github 小怪兽（GitHub 热门项目周榜 · 3 月第 4 周 · #3）
- **内容**：用 Zig 写的开源无头浏览器，内存占用比 Chrome 低 9 倍、执行快 11 倍，兼容 Playwright / Puppeteer；适合爬虫 / 测试 / 训练数据采集；9k stars
- **链接**：<https://github.com/lightpanda-io/browser>

### 8.4 CC / Codex 本地代理网关

<img src="images/xhs-cc-codex-proxy-gateway.png" width="420">

- **来源**：抖音 @睡觉的大提琴
- **内容**：本地 Claude Code / Codex / Gemini CLI 多账号自动切换网关
- **链接**：图里 URL 模糊（疑似 `coder-for-me/CCProxyAPI` 或 `OUProxyAPI`），TBD —— **需要你确认是哪个仓库**

---

## 9. 书 / 课

### 9.1 《AI Systems Performance Engineering》(Chris Fregly, O'Reilly, 2025)

<img src="images/book-ai-systems-performance-engineering.png" width="420">

- **作者**：小红书 @每日 ComputerScience 推荐
- **内容**：1058 页 O'Reilly 大书，登顶 Computer Hardware & Architecture 榜首，覆盖 CUDA kernel 优化 / 分布式训练 / 多节点推理 / 算法-硬件-软件协同优化，附 175+ 条 ready-to-use 优化清单。作者背景：Netflix / Databricks / AWS
- **链接**：
  - Amazon：<https://www.amazon.com/Systems-Performance-Engineering-Optimizing-Inference/dp/B0F47689K8>
  - 作者随书 GitHub：<https://github.com/cfregly/ai-performance-engineering>
  - Google Books：<https://books.google.com/books?id=RemWEQAAQBAJ>

### 9.2 Stanford CS146S：The Modern Software Developer (Fall 2025)

<img src="images/stanford-cs146s-modern-software-developer.jpg" width="420">

- **内容**：Stanford 把 vibe coding 正式纳入课程，覆盖 LLM 基础、Agent 架构、Context Engineering、Security、自动构建、生产运维全链路；讲师 Mihail Eric
- **链接**：
  - 课程网站：<https://themodernsoftware.dev/>
  - 作业仓库：<https://github.com/mihail911/modern-software-dev-assignments>
  - 课程视频 (YouTube)：<https://www.youtube.com/playlist?list=PLxpwjSdVZQ97L8hAGqTYUeOJqnKVSu3pb>
  - 课程总结博客：<https://akjamie.github.io/post/2026-02-23-stanford-cs146s-summary/>

---

## 10. 面试 / 求职

### 10.1 字节二面 ML 系统八连问

<img src="images/bytedance-ml-interview-questions.jpg" width="420">

- **来源**：小红书 (rednote ID 4139436216)
- **内容**：字节二面（8 × 30 min 高压）：linear attn 手撕、MoE 手撕、MHA 手撕、MLA 手撕、上面的访存计算、DeepSeek V3 结构伪代码 + 参数量 + 推理访存手算、堆排序、reduce 优化
- **链接**：TBD（小红书原帖未拿到 share link）

---

## 11. 写作 / 商业 视角

### 11.1 Anthropic 怎么挑提示词题目（@Ylva 的商业笔记 拆解）

<img src="images/xhs-anthropic-ylva-writing-tip.png" width="420">

- **作者**：小红书 @Ylva 的商业笔记
- **内容**：拆解 Anthropic（图里是 Amanda Askell 的播客访谈截图）选题目的方法——选"自己理解到位但读者大概率没搞清"的概念，用比喻把它讲完整。可用于工作文章选题、文章结构搭建
- **原始访谈链接**：
  - YouTube：<https://www.youtube.com/watch?v=0GaKJ4Fp2x4>
  - Newcomer Podcast：<https://podcast.newcomer.co/episode/amanda-askell-on-ai-consciousness-claude-amp-silicon-valleys-biggest-fear>
  - Spotify：<https://open.spotify.com/episode/70QP4rIc35PxHJNXiWAC8Y>
- **小红书原帖**：TBD

---

## 12. Meme / 趣图

### 12.1 "Generate an image of how I treated you, no sugar coating"

<img src="images/meme-chatgpt-how-i-treated-you.jpg" width="420">

- **内容**：网络流行 prompt——让 ChatGPT 生成"你平时怎么对待我的"图。结果是一个被随手拎起的破烂发光小机器人。属于 2026 年 AI meme 浪潮
- **链接**：TBD（来源小红书转发）

---

## 待你确认的 TBD 项

下面这些图没找到一手原帖，需要你确认或补链接：

1. §2.1–2.4 四张 Transformer 科普长图，是同一作者的系列。**你还记得是从哪个公众号 / 小红书号存的吗？**
2. §3.1 LLM 量化全景图 + §3.2 AI Infra 思维导图——两张小红书思维导图，**作者账号？**
3. §5.1 @羊拱机树 的「十大 Claude Skills」帖子链接
4. §8.4 CC/Codex 网关——**仓库实际名是什么？** 图里 URL 模糊不清
5. §10.1 字节二面贴的小红书原帖
6. §11.1 Ylva 的商业笔记 那条小红书的链接（视频访谈本身已找到）
7. §12.1 meme 来源
