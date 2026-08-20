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


# 数学/金融教材精读模板

把一节稠密的数学教材（定义-定理-证明体）拆成可攻的主题，并且**每个主题都强制回答"这对定价框架意味着什么 / 如果它不成立会怎样"**——逼出 quant 干货，而不是停在数学复述。

> **目标函数**：读完一节后，既能在白板上复述定义，又能回答面试官的"so what / what breaks if not"。
> **首次实践**：Shreve《Stochastic Calculus for Finance II》§1.1（见 [quant-coverage-framework.md](quant-coverage-framework.md) L0→L1 关卡）。

---

## 流程

### 第 0 步（仅扫描版 PDF 需要）：OCR 符号勘误表

稠密数学扫描件的乱码会直接导致误读。先建一张"OCR 显示 → 实际符号"对照表再动笔。Shreve 扫描件实例：

| OCR 显示 | 实际符号 |
|---|---|
| `il` / `fl` / `n` | Ω |
| `.r` / `:F` | 𝓕（σ-algebra） |
| `JP` / `IP'` | ℙ |
| `u-algebra` | σ-algebra |
| `!`（p = ! 处） | ½ |
| `2(23)` | 2^(2³)=256（上标丢失） |
| `Ali` / `AIIH` | Aᶜ / 补集记号丢失 |

工具：装 `poppler`（`brew install poppler`），`pdftotext -layout -f <首页> -l <末页> file.pdf out.txt`；先扫页找目标节的物理页码（`pdftotext` 每页 grep 节标题）。

### 第 1 步：拆主题

按"一个定义/一个例子/一个论证单元"切，通常 5–8 块。不要按书的小节号切——一个 Example 里常含多个独立主题（如 Shreve Example 1.1.4 前半是 filtration 阶梯、后半是奇异测度，得拆开）。

### 第 2 步：每主题标起止 wording

引用**原文首句 + 末句**作为锚点（配行号/公式号），让读者能回到原文精确定位。格式：起「…」｜迄「…」。

### 第 3 步：原文解读

- 复述该单元的**论证链**（不是逐句翻译，是"他为什么这样安排"）
- **标注模糊/被 OCR 破坏的符号定义**
- **补作者藏起来的背景定理**：留意 "it turns out" / "one can show" —— 这些短语后面往往藏着一个大定理（Carathéodory 延拓、Kolmogorov 延拓、SLLN…）。点名它、给一句背景，但不展开证明。

### 第 4 步：定价框架意义 ← 核心增值

把这段数学映射到现代衍生品定价里的一个具体对象或操作：样本空间↔路径空间、σ-algebra↔可写进 term sheet 的事件、测度↔Arrow-Debreu 价格、可数可加↔极限定价一致性/数值收敛牌照、等价测度↔Girsanov 合法边界、a.s.↔复制对冲的成立方式。**能落到一个 desk 常识或一条平价关系上最好。**

### 第 5 步：若不成立的后果

去掉该条件，链条哪里塌？映射到一个**金融失败模式**：补集不封闭→CDS/risky-bond 平价写不出；只有有限可加→doubling-strategy 悖论 + MCT/DCT 塌；各层赋值不自洽→calendar arbitrage / 校准无解；测度奇异→给不可能事件定正价（套利）。这一步把抽象公理变成"为什么它必须成立"的经济学答案。

---

## 输出骨架（每主题一块）

```
## 主题 N：<标题>（书页 x–y ｜ 行号）
**起**：「原文首句」 ｜ **迄**：「原文末句」
**原文解读**：论证链 + 符号定义 + 背景定理（点名 "it turns out" 背后的大定理）
**定价框架意义**：映射到路径空间/测度/对冲的具体对象
**若不成立**：去掉条件后的金融失败模式
```

## 质检清单

- [ ] 每个"it turns out / one can show"都点名了背后的定理
- [ ] 每个主题的"定价意义"落到了具体对象（不是泛泛"很重要"）
- [ ] 每个主题的"若不成立"给了一个**带金融内容**的失败模式，不只是"数学崩溃"
- [ ] 符号勘误表覆盖了原文所有非标准/乱码记号
- [ ] 起止 wording 可让读者精确回到原文

