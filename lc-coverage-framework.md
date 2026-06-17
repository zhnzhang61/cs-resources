# LC Coverage Framework

按"**人类直觉**"分类的 LeetCode 7 大 bucket framework，配 25 道代表性母题。

> **目标函数**：在面试白板前，能在 30 秒内把陌生题归到一个 bucket，对应到一个写代码模板。
>

---

## 1. 七大 Bucket：按"大脑动作"命名

每个 bucket 对应**一个动词**——面试时按 1→7 心里默念，第几个动作对应得上就用第几个。

**从最贴直觉到最反直觉排列**：

| # | 大脑动作 | Bucket 名 | 一句话识别 |
|---|---|---|---|
| 1 | "**看到啥就做**" | 模拟 & 贪心 | 题给规则，按规则走 |
| 2 | "**沿结构跑一遍**" | 遍历（Tree + Graph + Grid） | 题给树/图/网格，顺着探索 |
| 3 | "**试-失败-退回-再试**" | 回溯 | 题问"所有可能"或"构造满足条件的" |
| 4 | "**框一段 / 缩范围**" | 双指针 / 滑窗 / 二分 | 1D 序列上窗口或答案空间收敛 |
| 5 | "**维护当前最值**" | 堆 / 单调栈 / 单调队列 | 流式或扫描中要随时拿极值 |
| 6 | "**拆成子问题**" | DP | 当前选择依赖之前选择 + 重叠 |
| 7 | "**上专用工具**" | 特化 DS (LRU / Trie / UF / BIT / KMP) | 朴素工具撑不住，要为此设计的结构 |

**直觉密度断层**：1-5 是直觉能引导的，**6-7 必须靠训练**。

**LC 题量分布**（粗估）：

```
Bucket 1: ~30-40%    ← 最大兜底池
Bucket 6: ~15-20%
Bucket 2: ~15%
Bucket 4: ~10-15%
Bucket 5: ~5-10%
Bucket 3: ~5-10%
Bucket 7: ~5%
```

**面试操作启发**：看到题，**先按 #1 试**。"先模拟/贪心试一遍跑不通才升级"是单一最高 ROI 的面试 heuristic。

---

## 2. Bucket 1 的两层结构

Bucket 1 占 LC 30-40%，不细分会沦为"#1 = 题"。压成 **3 个大类 × 2-3 个子项**：

```
Bucket 1：模拟 & 贪心
│
├── 1.A 照着做 (Execute)               ← "题给规则我执行"
│   ├── 1A 纯物理模拟
│   └── 1B 状态机 / 解析
│
├── 1.B 扫一遍 + 维护 (Scan + Maintain) ← "盯着某个指标推进"
│   ├── 1C Running 标量扫描
│   ├── 1D Frontier 贪心
│   └── 1E 区间贪心
│
└── 1.C 想清楚再写 (Analyze + Construct) ← "先证明/计数，再构造"
    ├── 1F 频次驱动构造
    └── 1G 不变量贪心
```

**3 大类对应 3 种时间分配**：

| 大类 | 你在做什么 | 难点在 | 时间感 |
|---|---|---|---|
| **1.A 照着做** | 题面 1:1 翻译成代码 | careful coding + 边界 case | 实现长，思考短 |
| **1.B 扫一遍 + 维护** | 想清楚"维护什么"，然后线性扫 | 选对"维护什么" | 思考中等，实现中等 |
| **1.C 想清楚再写** | 数学/逻辑推导，再 5 行写完 | 找关键观察 | 思考长，实现极短 |

判到第一层就知道**该花时间在脑还是手上**。

### 子项的 trigger 短语

| 子项 | Trigger 短语（看到题面有这些关键词） | 维护什么 / 怎么做 |
|---|---|---|
| 1A 纯物理模拟 | "按规则旋转/移动/翻转"、给清晰执行步骤 | 翻译题面 + 边界控制 |
| 1B 状态机 / 解析 | 解析字符串、validate 格式、按字符更新内部状态 | flag/counter，按 transition 规则更新 |
| 1C Running 标量扫描 | "find max/min of (a op b) with i<j" 之类顺序约束 | 2-4 个 running max/min 标量 |
| 1D Frontier 贪心 | "min count to cover" / "max reach" / 跳跃 | 当前能到的最远 + 下一前沿 |
| 1E 区间贪心 | 给一堆区间，问 max 不重叠 / min 覆盖 / 合并 | 按 start 或 end 排序，扫一遍 |
| 1F 频次驱动构造 | "给频次构造合法序列" / "按字母位置反推" | count[] + 公式 or count + heap |
| 1G 不变量贪心 | 题给操作但**直接模拟会爆炸**，必须分析操作的本质 | 证明可达/不可达 → O(n) 构造 |

---

## 3. 25 道代表性母题

每个 bucket 选 1-7 题作"主题课题"，覆盖该 bucket 主流子模式。**Bucket 1 给了 7 题（每子项 1 道）**，因为它最大。

### Bucket 1 — 模拟 & 贪心（7 题，每子项 1 道）

| # | 子项 | 题 | 难度 | 教什么 |
|---|---|---|---|---|
| 1 | 1A 纯模拟 | [Spiral Matrix (54)](https://leetcode.com/problems/spiral-matrix/) | Medium | 矩阵模拟 + 边界控制 |
| 2 | 1B 状态机 | [Valid Number (65)](https://leetcode.com/problems/valid-number/) | Hard | 字符串 DFA |
| 3 | 1C Running 标量 | [Best Time to Buy/Sell Stock (121)](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | Easy | 维护 minPrice + maxProfit 两个标量 |
| 4 | 1D Frontier | [Jump Game II (45)](https://leetcode.com/problems/jump-game-ii/) | Medium | BFS-style 前沿扩展，跨层 count++ |
| 5 | 1E 区间 | [Non-overlapping Intervals (435)](https://leetcode.com/problems/non-overlapping-intervals/) | Medium | 按右端点排序 + 贪心保留 |
| 6 | 1F 频次驱动 | [Reorganize String (767)](https://leetcode.com/problems/reorganize-string/) | Medium | max-heap + 不能连放同字符 |
| 7 | 1G 不变量 | [Gas Station (134)](https://leetcode.com/problems/gas-station/) | Medium | "前缀和最低点的下一个出发"的不变量证明 |

### Bucket 2 — 遍历（Tree + Graph + Grid）（3 题）

| # | 子项 | 题 | 难度 | 教什么 |
|---|---|---|---|---|
| 8 | Grid | [Number of Islands (200)](https://leetcode.com/problems/number-of-islands/) | Medium | DFS / BFS / 并查集 三解对照 |
| 9 | Graph | [Course Schedule II (210)](https://leetcode.com/problems/course-schedule-ii/) | Medium | 拓扑排序（Kahn 算法） |
| 10 | Tree | [Binary Tree Maximum Path Sum (124)](https://leetcode.com/problems/binary-tree-maximum-path-sum/) | Hard | Tree DP 入门，孩子 return value 合并 |

### Bucket 3 — 回溯（2 题）

| # | 题 | 难度 | 教什么 |
|---|---|---|---|
| 11 | [N-Queens (51)](https://leetcode.com/problems/n-queens/) | Hard | 回溯 + 三集合剪枝 |
| 12 | [Word Search II (212)](https://leetcode.com/problems/word-search-ii/) | Hard | 回溯 + Trie 同时搜多词 |

### Bucket 4 — 双指针 / 滑窗 / 二分（3 题）

| # | 题 | 难度 | 教什么 |
|---|---|---|---|
| 13 | [Trapping Rain Water (42)](https://leetcode.com/problems/trapping-rain-water/) | Hard | 双指针 / 单调栈 / DP 三解 |
| 14 | [Minimum Window Substring (76)](https://leetcode.com/problems/minimum-window-substring/) | Hard | 滑窗 + hash 模板 |
| 15 | [Split Array Largest Sum (410)](https://leetcode.com/problems/split-array-largest-sum/) | Hard | **二分答案**（非自然的思维跳） |

### Bucket 5 — 维护最值（3 题）

| # | 子项 | 题 | 难度 | 教什么 |
|---|---|---|---|---|
| 16 | 堆 | [Merge K Sorted Lists (23)](https://leetcode.com/problems/merge-k-sorted-lists/) | Hard | k 路归并 / 分治两解 |
| 17 | 单调栈 | [Largest Rectangle in Histogram (84)](https://leetcode.com/problems/largest-rectangle-in-histogram/) | Hard | 单调栈找左右第一个更小 |
| 18 | 单调队列 | [Sliding Window Maximum (239)](https://leetcode.com/problems/sliding-window-maximum/) | Hard | 单调队列 |

### Bucket 6 — 动态规划（5 题，覆盖五大 DP 子类）

| # | 子类 | 题 | 难度 | 教什么 |
|---|---|---|---|---|
| 19 | 1D 线性 / 完全背包 | [Coin Change (322)](https://leetcode.com/problems/coin-change/) | Medium | DP 入门，dp[v] = 凑 v 的最少硬币 |
| 20 | 2D 字符串 DP | [Edit Distance (72)](https://leetcode.com/problems/edit-distance/) | Medium | dp[i][j] = 前 i / 前 j 的编辑距离 |
| 21 | 区间 DP | [Burst Balloons (312)](https://leetcode.com/problems/burst-balloons/) | Hard | **反向思考**：最后戳哪个 |
| 22 | 状态 DP | [Best Time to Buy/Sell IV (188)](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/) | Hard | dp[i][j][holding] 三维状态 |
| 23 | 位掩码 DP | [Shortest Path Visiting All Nodes (847)](https://leetcode.com/problems/shortest-path-visiting-all-nodes/) | Hard | 位掩码编码访问集 + BFS |

### Bucket 7 — 特化 DS（2 题）

| # | 题 | 难度 | 教什么 |
|---|---|---|---|
| 24 | [LRU Cache (146)](https://leetcode.com/problems/lru-cache/) | Medium | hash + 双向链表复合设计 |
| 25 | [Range Sum Query 2D - Mutable (308)](https://leetcode.com/problems/range-sum-query-2d-mutable/) | Hard | 2D BIT / 二维线段树 |

---

## 4. 面试时怎么用：三级漏斗

```
Step 1: 默念 7 个 bucket 动词
        "看到啥就做？沿结构跑？试-失败？框/缩？维护最值？拆子问题？上专用工具？"
        ↓ 缩到一个 bucket

Step 2: 如果落在 #1，再默念 3 个大类
        "照着做？扫一遍维护？想清楚再写？"
        ↓ 缩到一个大类

Step 3: 在大类内部定到 2-3 个子项
        ↓ 拿出模板写代码
```

工作记忆全程**只需要 3-7 个标签**，符合大脑短期记忆容量（Miller's 7±2）。

### 跨 bucket 推荐做题顺序

不是按编号 1→7 做，按**直觉容易度 + 依赖关系**：

```
1 模拟贪心 (1.A 子集 → 1.B → 1.C 顺序)
  ↓
2 遍历 (Grid → Graph → Tree 顺序)
  ↓
3 回溯
  ↓
4 框/缩
  ↓
5 维护最值 (堆 → 单调栈 → 单调队列)
  ↓
6 DP (1D → 2D → 区间 → 状态 → 位掩码)
  ↓
7 特化 DS
```

DP 倒数第二做——它是子问题感最难培养的，需要前面所有训练做铺垫。特化 DS 最后——前面积累的 DS 直觉让你能理解为什么需要专用工具。

---

## 5. 反陷阱规则

LC 上最危险的不是不会做，是**把 #1 题升级处理成 #5/#6/#7**。记住这几条反陷阱规则：

| 题面 framing | 错误本能 | 正确 bucket | 反陷阱规则 |
|---|---|---|---|
| "construct a string with constraint" | backtracking (#3) | #1 1F 频次驱动 | 局部约束 + 频次可数 → 先试贪心 |
| "min count to cover [0, n]" | graph 最短路 (#2) | #1 1D Frontier | "覆盖"+"最少"→ 先试区间贪心 |
| "find max/min over triplets/tuples" | DP (#6) | #1 1C Running 标量 | 几个变量就能维护 → #1 |
| "扫一遍字符串" | 遍历 (#2) | #1 1B 状态机 | 1D 线性扫不是 #2，#2 是 follow 结构边 |
| "操作字符串 / 数组" | 模拟 (#1 1A) | #1 1G 不变量 | 直接模拟会爆炸 → 先找操作的不变量 |
| LC tag 是 "Dynamic Programming" | 真 DP (#6) | 可能是 #1 + 简单递推 | LC tag 噪音多，看认知主干 |

---

## 6. 怎么从"知道框架"到"秒选对工具"

framework 不是终点，是**起点**。从 Stage 3（懂框架）→ Stage 4（10 秒识别）靠这 4 个习惯：

1. **Active retrieval**：每题做完关掉解答，48 小时后强迫回忆 trigger → pattern。**Testing effect 决定一切**。
2. **Trigger → pattern 字典**：每题写一行"看到 X 就用 Y"。攒 50-80 条。
3. **5 秒约束过滤**：先看 `n` 的范围，砍掉 70% 候选 paradigm（n ≤ 20 → bitmask，n ≤ 10⁵ → O(n log n) max）。
4. **错题 → 反陷阱规则**：每次踩坑写一条"这种 framing 不要再选错 bucket"。攒 30-50 条。

**100 道有意识做的题 > 500 道无意识刷的题**。

---

## 附录 A：扩展题（每 bucket 4-5 道，做完主 25 接着刷）

### Bucket 1 各子项扩展

| 子项 | 扩展题 |
|---|---|
| 1A 纯模拟 | Spiral Matrix II (59) · Rotate Image (48) · Game of Life (289) · Set Matrix Zeroes (73) |
| 1B 状态机 | String to Integer atoi (8) · Basic Calculator (224) · Decode String (394) · Simplify Path (71) |
| 1C Running 标量 | Maximum Subarray (53) · Maximum Value of an Ordered Triplet II (2874) · Largest 1-Bordered Square (1139) |
| 1D Frontier | Jump Game (55) · Min Taps (1326) · Video Stitching (1024) |
| 1E 区间 | Merge Intervals (56) · Insert Interval (57) · Meeting Rooms II (253) |
| 1F 频次驱动 | Task Scheduler (621) · String Without AAA or BBB (984) · Reconstruct Original Digits (423) |
| 1G 不变量 | Candy (135) · Container With Most Water (11) · Maximum Binary String After Change (1702) |

### Bucket 2 遍历扩展

- Grid：Word Search (79)、Pacific Atlantic Water Flow (417)
- Graph：Network Delay Time (743, Dijkstra)、Connecting Cities Min Cost (1135, MST)、Critical Connections (1192, Tarjan)
- Tree：Validate BST (98)、Binary Tree Cameras (968)、Lowest Common Ancestor (236)

### Bucket 3 扩展
Sudoku Solver (37) · Word Break II (140) · Word Squares (425) · Prefix and Suffix Search (745)

### Bucket 4 扩展
Median of Two Sorted Arrays (4) · Find Median from Data Stream (295) · Subarrays with K Different Integers (992) · Capacity to Ship Packages (1011)

### Bucket 5 扩展
Daily Temperatures (739) · Next Greater Element II (503) · Sum of Subarray Minimums (907) · Top K Frequent Elements (347)

### Bucket 6 DP 扩展
Partition Equal Subset Sum (416, 背包) · Binary Tree Cameras (968, 树形 DP) · Number of Digit One (233, 数位 DP) · Regular Expression Matching (10) · Jump Game VI (1696, 单调队列优化 DP)

### Bucket 7 扩展
Implement Trie (208) · The Skyline Problem (218) · Range Module (715) · Shortest Palindrome (214, KMP)

---

## 附录 B：框架在 10 道随机题上的验证

整理这套 framework 时实际测试过的 10 道题，全部能精确归类到 bucket + 子项：

| 题 | Bucket | Bucket 1 子项 | 第一直觉陷阱 |
|---|---|---|---|
| [Reconstruct Original Digits (423)](https://leetcode.com/problems/reconstruct-original-digits-from-english/) | #1 | 1F 频次驱动 | ad-hoc |
| [Next Greater Element II (503)](https://leetcode.com/problems/next-greater-element-ii/) | #5 | — | 教科书 |
| [Valid Number (65)](https://leetcode.com/problems/valid-number/) | #1 | 1B 状态机 | 状态机直觉 ✓ |
| [K Highest Ranked Items (2146)](https://leetcode.com/problems/k-highest-ranked-items-within-a-price-range/) | #2 | — | grid BFS + 排序 tail |
| [String Without AAA or BBB (984)](https://leetcode.com/problems/string-without-aaa-or-bbb/) | #1 | 1F 频次驱动 | "看着像 search" |
| [Min Taps (1326)](https://leetcode.com/problems/minimum-number-of-taps-to-open-to-water-a-garden/) | #1 | 1D Frontier | "看着像 graph" |
| [Min Frogs Croaking (1419)](https://leetcode.com/problems/minimum-number-of-frogs-croaking/) | #1 | 1B 状态机 | "看着像遍历" |
| [Triplet II (2874)](https://leetcode.com/problems/maximum-value-of-an-ordered-triplet-ii/) | #1 | 1C Running 标量 | "看着像 #5 / #6" |
| [Largest 1-Bordered Square (1139)](https://leetcode.com/problems/largest-1-bordered-square/) | #1 | 1C' 2D Running | "LC 官方 tag = DP" |
| [Maximum Binary String (1702)](https://leetcode.com/problems/maximum-binary-string-after-change/) | #1 | 1G 不变量 | "看着像 search" |

**10 题里 8 道 #1**——印证 LC 题量分布严重偏 #1，"先按 #1 试" 是高 ROI 策略。




