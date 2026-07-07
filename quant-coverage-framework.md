# Quant Coverage Framework

量化面试知识框架：**行 = 随机源 (dynamics)，列 = 求解工具 (tool ladder)**，每格填面试高频知识点。

> **目标函数**：面试官抛出任意 stoch calc / pricing 题，30 秒内定位到 (行, 列) 格子，知道该调用哪套数学。

---

## 0. 底座：共享的概率空间

三行 dynamics 共享同一个 filtered probability space **(Ω, F, {F_t}, P)** —— outcome、event、σ-algebra、conditional expectation、filtration 全是公用的。分叉发生在上面一层："这个空间上的基本鞅长什么样"，即 **Lévy–Khintchine 三元组 (b, σ², ν)**（drift、扩散系数、跳测度）：

| Dynamics | 三元组 |
|---|---|
| 扩散 (BM) | (b, σ², **0**) |
| 纯跳 (Poisson) | (0, 0, **λδ₁**) |
| 混合 (jump-diffusion) | 三个分量全开 |

三种噪声不是三棵树，是同一棵树干上三个开关的组合。统一微积分：三者都是 semimartingale，Ito 公式的 semimartingale 版本（quadratic variation = 连续部分 + 跳求和）覆盖全部——BM 版和 Poisson 版都是特例。

## 1. 工具阶梯（列定义）

- **L0 离散概率/组合** — probability space 直觉层，brainteaser 主产区
- **L1 鞅 + 随机分析** — Ito / Girsanov / Feynman-Kac，闭式定价
- **L2 PDE + 数值线性代数** — 有限差分矩阵、三对角求解、PCA、bootstrap
- **L3 MC + 回归/统计学习** — 路径模拟、LSMC、方差缩减、ML

线性代数不单独立轴——它本身就是 L2/L3 的骨架（FD 矩阵、协方差谱分解、回归基底）。

## 2. 主表（dynamics × tool）

每格两层：概念清单 + 📖 阅读地图。**C** = Calin《An Informal Introduction to Stochastic Calculus with Applications》章节；**S-I / S-II** = Shreve《Stochastic Calculus for Finance》卷一（二叉树）/ 卷二（连续时间）；**✍️** = 两本都不含，标注第三来源。

| | **L0 离散概率/组合** | **L1 鞅 + 随机分析** | **L2 PDE + 线性代数** | **L3 MC + 回归/ML** |
|---|---|---|---|---|
| **扩散 (BM)** | 随机游走→BM 极限 (Donsker)、reflection principle、gambler's ruin、ballot problem<br>📖 S-I Ch.5 Random Walk（reflection/first passage）、S-I Ch.2 离散鞅；Donsker/ballot ✍️ Feller Vol.1 | Ito、Girsanov、Feynman-Kac、BS 闭式、⟨W⟩=t、first passage<br>📖 C 3.1–3.2 (BM/GBM)、5.3 (Ito 积分)、6.2 (Ito 公式)、4.11 (quadratic variation)、4.3 (first passage)、9.7 (Feynman-Kac)、10.4 (Girsanov)；BS 闭式 S-II §4.5 + Ch.5 | BS/局部 vol PDE 有限差分（三对角、Crank-Nicolson）、Hull-White 树、收益率曲线 PCA<br>📖 PDE 来源 C 9.4 (Kolmogorov backward) + S-II Ch.6；利率二叉树 S-I Ch.6；FD 数值与 PCA ✍️ Duffy / Wilmott | Euler/Milstein 路径模拟、方差缩减（BS 作 control variate）、**LSMC American**<br>📖 模拟对象 C 3.2 (GBM)、3.5 (Brownian bridge)、8.1 (SDE)；方法 ✍️ Glasserman Ch.3–4；LSMC ✍️ Longstaff-Schwartz (2001) + Glasserman Ch.8 |
| **纯跳 (Poisson)** | thinning/superposition 谜题、无记忆性 brainteaser、到达时刻条件均匀分布<br>📖 C 3.8–3.10（Poisson/interarrival/waiting，无记忆性全在这）；thinning/条件均匀 ✍️ Ross《Stochastic Processes》 | 补偿鞅 N−λt、Poisson 版 Ito、survival prob = e^(−∫λ)、Cox process、intensity 的测度变换<br>📖 C 3.11–3.12、5.7–5.9（Poisson 积分）、6.2.2（跳 Ito）、8.6（Poisson SDE）；测度变换 S-II §11.6；Cox/hazard 应用 ✍️ Lando 前 4 章 | **评级迁移矩阵 = CTMC generator 的矩阵指数**、hazard curve bootstrap（三角线性系统）<br>📖 两本全无 ✍️：CTMC/矩阵指数 Norris《Markov Chains》；hazard bootstrap 实务材料 (Lando/Hull) | default time 逆变换/thinning 模拟、copula 抽 joint default、**importance sampling（违约是稀有事件）**<br>📖 逆变换底子 C 3.9；其余 ✍️：IS Glasserman Ch.4；copula Nelsen 前 3 章 |
| **混合 (jump-diffusion)** | 复合分布（随机个数求和）、Wald 恒等式<br>📖 原料 C 2.11–2.12（和 + 条件期望）；compound Poisson S-II §11.3；Wald ✍️ Ross | Lévy–Khintchine、semimartingale Ito、Merton 闭式（Poisson 加权 BS 和）、**特征函数/Fourier 定价**<br>📖 跳 Ito C 6.2.2；跳过程微积分 + Merton 定价 S-II Ch.11 (§11.5、§11.7)；Lévy–Khintchine/Fourier ✍️ Cont & Tankov | PIDE（积分项破坏稀疏性→难，冷区）、Carr-Madan FFT（Toeplitz 结构）<br>📖 两本全无 ✍️ Cont & Tankov（PIDE 数值章）——冷区可跳 | jump-adapted 模拟（先抽跳时刻、之间填 diffusion bridge）、MLMC<br>📖 两本全无 ✍️ Glasserman（jump-adapted）+ Giles (2008) MLMC |

**热区**（面试火力集中）：扩散行整行、纯跳×L1（credit 面试）、混合×L1 的特征函数定价。
**冷区**：混合×L2（PIDE 工业界都嫌麻烦，面试基本不碰）、纯跳×L0（偶尔出脑筋急转弯）。

**书架结论**：Calin + Shreve 覆盖左两列和纯跳×L1 的机器；**Glasserman** 一本补掉 L3 列；**Cont & Tankov** 补混合行；**Lando** 补纯跳行的 applied 半边。五本书张成全表。

## 3. Asset class 怎么进来

Asset class 不是轴，是**行的参数化**（漂移与边界条件的约束）：

| Asset class | 落在哪行 | 特有约束 |
|---|---|---|
| Equity / vol | 扩散行 | GBM + 随机 vol，无漂移约束 |
| Rates / term structure | 扩散行 | 均值回复 + 整条曲线无套利 (HJM/LMM) |
| Credit | 纯跳行 | intensity / hazard rate，default = stopping time |
| Commodity | 扩散+跳 | 均值回复 + 季节性 + spike |

---

## Reminder：第三根轴 task（面试题从哪来）

完整结构是 **dynamics × tool × task 的 3D 张量**，上表是它在 (dynamics, tool) 平面的投影。Task 轴五个动词，每个任务横穿工具列、有自己的偏好列：

- **Price**（正问题：算 E^Q）— 面试考 L1 闭式；生产上高维/路径依赖被迫落 L3。工具选择由**维度**决定，不是偏好
- **Calibrate**（反问题）— 主场 L2：最小二乘 + Jacobian、Tikhonov、Dupire 反演、curve bootstrap
- **Hedge / Greeks**（微分）— 价格在网格上时 L2 求导免费；生产 XVA 标准是 L3 的 **AAD**
- **Exercise**（最优停时）— 树上 backward induction (L0) → Snell envelope (L1) → LCP/PSOR (L2) → **LSMC** (L3)
- **Aggregate risk**（分布/尾部）— Cholesky/PCA (L2)、全重估 MC VaR + importance sampling (L3)

**用法**：面试官报一个任务（"price this Bermudan"），沿该任务行从左往右扫——有没有闭式 → 维度够不够上网格 → 不行上 MC/LSMC。这个扫描顺序本身就是标准答案的结构。
