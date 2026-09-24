# Notes Basic

The six shared foundations under Stochastic Calculus × ESL/ISL × Transformer/LLM, each expanded into 15 interview questions ordered from basic to advanced. Work each section top-to-bottom: no question requires anything that appears later in its section (cross-section references only point backward, §1 → §6). Answers to be filled in gradually.

**Tags**: `[C]` = common to all three directions · `[SC]` = stochastic calculus · `[ML]` = ESL/ISL · `[LLM]` = transformer/LLM.

## The map

| # | Shared foundation | In Stochastic Calculus | In ESL/ISL | In Transformer/LLM |
|---|---|---|---|---|
| 1 | **Conditional expectation / conditional distribution E[Y\|X]** | Pricing is a conditional expectation: V = E^Q[discounted payoff \| F_t]; the very definition of a martingale | The regression function is defined as E[Y\|X] — the whole book is about approximating it | Next-token prediction = estimating the conditional distribution p(x_t \| x_{<t}); autoregressive factorization |
| 2 | **Linear algebra: matmul · projection · eigendecomposition / SVD** | Cholesky for correlated Brownian motions; PCA factors on curves | OLS as projection geometry; ridge as spectral shrinkage; PCA | Everything is matmul: QKᵀ in attention; LoRA low-rank; FlashAttention tiling |
| 3 | **Chain rule + Taylor expansion (bookkeeping of 1st/2nd derivatives)** | Itô's lemma = a second-order Taylor expansion with (dW)² = dt; Greeks are derivatives of the price | Gradient descent / Newton's method; convexity; logsumexp for numerical stability | Backprop = the chain rule; optimizers; loss-landscape curvature |
| 4 | **Gaussians & variance scaling laws** (how variance moves with time / dimension / sample size) | √t scaling of Brownian motion; lognormal dynamics; vol annualization | Bias-variance decomposition; least squares = Gaussian MLE; noise models | The 1/√d_k in attention is a variance argument; initialization variance; CLT intuition |
| 5 | **Likelihood · cross-entropy · KL · change of measure** (the likelihood-ratio family) | Girsanov: dQ/dP is a likelihood ratio; importance sampling | MLE, deviance, EM; log-loss of logistic regression | Training objective = cross-entropy = KL minimization; the KL penalty in RLHF |
| 6 | **Sampling / Monte Carlo** (replacing integrals and distributions with draws) | MC pricing: simulate paths, average to approximate E^Q[payoff]; variance reduction (antithetic, control variates, importance sampling) | Bootstrap; cross-validation; bagging's random resampling; MCMC | Decoding is sampling from p = softmax(z/T): greedy / top-k / top-p / temperature; RL rollouts; MC dropout |

Note: #5 and #6 are a pair — #5 is how to convert between distributions (likelihood ratios), #6 is how to replace integrals with draws; importance sampling sits exactly at their intersection.

---

## 1. Conditional expectation / conditional distribution E[Y|X]

### 1. `[C]` Define E[Y|X=x] for discrete random variables. Compute a concrete example: roll two dice, find E[sum | first die = 3].

   **A**: E[Y|X=x] comes from an effort to calculate the fair price of an unfinished game. The game was: two teams play, whoever scores 60 wins - now the score is 50 to 20 and the game stops, how to split the payout. People eventually realized the split should be based on **the futures from the current score - the past matters only through where it left the score, nothing else** (the first printed answer, Pacioli 1494, split by points already scored - backward-looking - and at a score of 1:0 his rule hands the leader the entire pot. Absurd.)

   Written as a recipe, that's the definition: keep only the futures compatible with X=x, reweight, average the payoff column: E[Y|X=x] = Σ y·P(Y=y|X=x).

   So back to this question: first die = 3 is the "current score", and we look into the future from here. The remaining future is the second die, whose average payoff is 3.5 (equal weighting, 1/6 each). Because Y = X1 + X2, the average of Y is 3 + 3.5 = **6.5**.

### 2. `[C]` State the tower property (law of total expectation) E[E[Y|X]] = E[Y]. Verify it on the dice example above.

   **A**: the story first. Two players each put 32 pistoles in, whoever wins 3 rounds takes all 64 (each round 50/50, rounds independent). The game stops in the middle - how to split the 64? Say player A leads 2:1. The next round must land on either 3:1 or 2:2. So A **is entitled to 32 no matter what** - even losing puts him at 2:2, worth 32 by symmetry - and the other 32 rides on a 50/50 round. Fair split at 2:1: A takes (64+32)/2 = 48, B takes (0+32)/2 = 16.

   The tower property is this move written as a formula: the price of the game at any node = the probability-weighted average of the prices one round later: E[Y] = Σ_x P(X=x)·E[Y|X=x] = E[E[Y|X]]. Because the same rule holds at **every** node, Pascal could start from the finished positions and step backwards one round at a time - reusing 2:1's 48 inside 2:0, then 2:0's 56 inside 1:0 - instead of enumerating every remaining future like Fermat did. Recursion instead of enumeration: dynamic programming, born 1654.

   Dice check: the pre-roll price of the "sum" game = the average of the slice prices E[Y|X=1], ..., E[Y|X=6], which are 4.5, 5.5, ..., 8.5 (that is, x + 3.5), each weighted 1/6 because the first die is fair (load the die and these weights all change - the slice prices don't move). That gives 3.5 + 3.5 = **7**. Direct computation of the other side: E[sum] = E[X1] + E[X2] = 7. Both sides agree.

### 3. `[C]` E[Y|X=x] is a number; E[Y|X] is a random variable (a function of X). Explain the distinction and why it matters.

   **A**: first, what a rv even is - the whole point of a rv is to assign a cash value to every scenario of a game, so people can compute the fair value of the game by weighting these cash values by their probabilities (this is literally how it was invented - Pascal and Fermat splitting an interrupted pot in 1654).

   Now the actual question. E[Y|X=x] is **one number**: the fair price of the game given the score is x. Pascal computed exactly one of these - the price at score 2:1.

   E[Y|X] is the **whole repricing schedule**: one price for every possible score - "if 1:1, price is A; if 2:1, price is B; if 2:2, price is C...". Look at what this schedule does: it assigns a number to every scenario. By our own definition above, **that makes the schedule itself a random variable** - a new column on the same table. Before the game starts you don't know which score will materialize, so you don't know which price will apply. It's random - but random only through X: the schedule looks at the scenario, reads off the score, and nothing else.

   Why the distinction matters, twice over:

   1. because E[Y|X] is itself a rv, you can average **it** - that's exactly what Q2 did: E[E[Y|X]] = E[Y]. If E[Y|X] were just a number, the outer E would be meaningless. The tower property doesn't even parse without this distinction.

   2. it's the object both worlds actually care about. In ML, the regression function is E[Y|X] **as a function** - the whole ridge line, not one slice's average; the entire book (ESL) is about approximating the schedule, not one number. In pricing, V_t = E^Q[payoff | F_t] is the mid-game price as information unfolds - the repricing schedule running forward in time is the price process. Confusing the number with the schedule is confusing one quote with the pricing rule.

### 4. `[C]` Show that the function g minimizing E[(Y − g(X))²] is g(X) = E[Y|X]. (The L² projection property — the single most reused fact in all three directions.)

   **A — the guessing game**: I pick a random student from the whole school; you guess their height; a wrong guess costs you (miss)². Many rounds; minimize the average fine.

   One-line version: told nothing, report the school average. Told the grade first, report **that grade's** average. "Whatever you're told, report the average within that range" - this strategy has no rival, and it IS the regression function E[Y|X].

   **Skipped step 1 - why is the average the best single guess?** Textbooks wave this through with "obviously". Write it out: you report c, and the average fine is

   ```
   avg[(height − c)²] = avg[height²] − 2c·avg[height] + c²
   ```

   Treat c as the variable: an upward-opening parabola. Differentiate, set to zero: −2·avg[height] + 2c = 0, so the bottom sits at c = avg[height]. Done - nothing but the distributive law and one derivative.

   **Skipped step 2 - told the grade, why can you optimize grade by grade?** Your strategy is now a small table: "grade 1 → report this, grade 2 → report that, ..." - **this table is all that "a function g(X)" means**, nothing deeper. And the total fine splits by grade:

   ```
   total average fine = Σ (share of students in that grade) × (average fine inside that grade)
   ```

   The key: the number you pick for grade 3 appears only in grade 3's term - the grades' accounts don't touch each other. So minimizing grade by grade = minimizing the whole. Inside each grade you're just replaying skipped step 1 → each grade reports its own average. Assembled: the optimal g is "each grade reports its grade average", i.e. E[Y|X].

   **Skipped step 3 - the winner still pays.** Even with the perfect strategy, students inside one grade differ in height - that part of the fine (the within-grade spread) nobody can dodge: the noise floor. Lowering it takes more information, not a better guesser: told the sex as well, the slices get finer and the floor drops - but there is always a floor. (And Q5 is already visible from here: the winner's fine + your excess over the winner = the total spread - exactly Q5's two accounts.)

   One-line close:

   ```
   among all guessing rules g:  avg[(Y − g(X))²] is minimized by
   "each slice reports its own average" = E[Y|X]
   ```

   ---

   **Background I - 1809: a birth certificate issued backwards.** Gauss, in Theoria Motus, needed a justification for least squares. He was not a neutral explorer - he claimed he'd used least squares since 1795, Legendre had published the recipe four years earlier (with purely engineering reasons: easy to compute, unique solution), and a priority fight was brewing. Gauss wasn't looking for the answer; he was retrofitting a weighty birth certificate for an answer already in use. The road was built toward a chosen destination.

   He had two materials. One borrowed: Laplace's inverse-probability machine - "the most probable value", the posterior mode under a flat prior (Laplace had run this machine for thirty years; the name "MLE" waits for Fisher, a century later). One believed: all of Europe averaged repeated measurements, and nobody asked why.

   His move was to run the inference backwards: not "assume an error law → derive the best estimate", but "**take the mean as an axiom, and ask which error law can make it true**". The axiom deserves a slow reading, because its wording hides the engine of the whole argument. Setup: one unknown true value μ, one batch of measurements (y₁,…,yₙ), and two verdict procedures on the table:

   ```
   Procedure A (Europe's habit):    report the batch's own average ȳ
   Procedure B (Laplace's machine): sweep candidate μ's, score each:
       score(μ) = φ(y₁−μ)···φ(yₙ−μ), report the top-scoring candidate
   ```

   Both outputs travel with the batch: batch (10,12,17) has mean 13, batch (3,5) has mean 4; the score's peak moves too. The axiom = **the two procedures are the same function**: ∀ batch, argmax_μ score_batch(μ) = mean(batch). Not one fixed μ optimal for all batches - the peak travels with the batch; the axiom says every batch's peak lands on that batch's own mean, **batch after batch**. This is where the constraining power lives: there is only one φ, yet it must serve every batch's peak at once - only one candidate survives a demand that strict.

   Five steps, with the quantifier cashed in at step ③:

   ```
   ① First-order condition (one batch): differentiate log score, set to zero
      ⟹ Σ g(residualᵢ) = 0,  g = (log φ)'
      - one batch gives one equation: almost no constraint on g
   ② The mean's fingerprint: residuals always sum to zero; conversely,
      any zero-sum tuple is some batch's residuals
   ③ Cash the quantifier: "batch after batch" ⟹ g maps every zero-sum
      tuple to a zero-sum tuple
      n=2, (r,−r) → g is odd;  n=3, (r,s,−r−s) → g(r)+g(s)=g(r+s)
      - Cauchy's functional equation + continuity ⟹ g linear: g(ε) = −2h²ε
   ④ Integrate: log φ = −h²ε² + C ⟹ φ ∝ exp(−h²ε²)   ← the square is born here
   ⑤ Multi-observation likelihood ∝ exp(−h²Σεᵢ²)
      ⟹ maximizing likelihood = minimizing Σεᵢ² ⟹ least squares
   ```

   Watch step ④: the square in the exponent wasn't chosen - it was lifted there by integration. "Residuals sum to zero" is linear; "batch after batch" forces the score function to be linear; integrating a linear function once gives a quadratic. **The square is the integral of the mean.** The normal distribution is born - not observed in any data, but reverse-engineered as the mean's only legal guarantor (a characterization: normal ⟺ the mean is always the most probable value). The price is circularity: using "the mean is right" to prove "squares are right", when they are mechanically the same faith. Contemporaries saw through it.

   **Background II - the aftermath, three acts.** 1810, Laplace launders the custom-made blessing with the CLT: errors are sums of many small effects, hence roughly normal anyway - the certificate turns legitimate. 1823, Gauss retreats and confesses: he defines squared error explicitly as a **loss** (jactura) for the first time, admitting the question has no truth in itself and the choice is guided by convenience - his rival being Laplace's 1774 absolute-value loss (optimum = the median; **L1 predates L2 as a loss by half a century**); he then proves Gauss-Markov, no normality needed. 1930s-40s, the late acquittal: the modern theorem (this question) assumes no distribution at all and moves the axiom into the loss - **the blessing migrates from the distribution into the loss function**; L²'s inner-product geometry retroactively shows the 1823 "arbitrary convenience" was one of a kind: the square is the only loss that grows a projection geometry. The normal's true role also settles: under normality, mean = median = mode, so L1, L2 and "most probable" all agree - **it is the distribution that silences all reasonable criteria**, not the reason the mean is right.

   **Background III - from Gauss's ⑤ to this question's formula: two substitutions.** His Σεᵢ² and E[(Y−g(X))²] look like twins, separated by two moves:

   **Substitution 1: parameters → functions.** His ε is "observation minus a model whose recipe is known and only has blanks to fill" - the thing subtracted is fixed by physical law, the only freedom is a few blanks; g(X) is a free function. The crossing runs through "g = one constant per slice", where his case is "the whole world is one slice" (repeated measurement of one quantity - μ is that lone slice's constant), or "the slice structure compressed by physics into a parameter family". Galton made this crossing in 1886: father/son heights come with no physical law to fill in, so he laid the data out as a cross-table and took each slice's center - **the target changed from a recipe to the slice-center function itself**; the slope-2/3 line was a finding, not an assumption.

   **Substitution 2: sums → expectations.** His Σ is a finite sum over the batch at hand (sample SSE); E is an integral over the joint surface (population MSE) - which he could not even write down: his ontology had no surface. Kolmogorov made this crossing in 1933: the surface becomes a formal object, Radon-Nikodym makes zero-probability slices legal, and the L² projection theorem guarantees the minimizer exists and is unique; iid + LLN then connect the two levels: the batch sum is the plug-in approximation of the surface expectation.

   ```
   Gauss 1809:       min over parameters   Σ_batch (y − recipe(params))²
   Galton 1886:      recipe → one constant per slice     (Substitution 1: functionalize)
   Kolmogorov 1933:  batch sum → expectation over surface (Substitution 2: populationize)
   ──────────────────────────────────────────────────────
   Q4:               min over all g        E[(Y−g(X))²] → minimizer E[Y|X]
   ```

   One line to close: **in 1809 the mean reverse-engineered the normal (the square is the integral of the mean); in 1823 the inventor confessed the square was mere convenience; a century later, convenience turned out to be the only choice with a geometry - and Q4 took the blessing away from the distribution and deposited it in the loss, permanently.**

### 5. `[C]` State and prove the conditional variance decomposition Var(Y) = E[Var(Y|X)] + Var(E[Y|X]). Interpret both terms.

   **A — same school, second theorem.** Same setup as Q4: the whole school's heights, X = grade.

   One-line version: the school's total height spread = (the within-grade spreads, averaged) + (the spread of the grade averages). Two accounts, and they add up exactly - nothing missing, nothing double-counted. R² is just the second account's share of the total.

   Common sense first, two extremes: if every grade were internally uniform (everyone in a grade the same height), all spread would come from grade averages differing; if all grade averages were equal, all spread would be within-grade. Normally both are present. The only non-obvious claim the theorem adds: **the split is exactly additive - there is no third account.**

   **The skipped step - why no third account.** Each student's deviation from the school average walks in two legs:

   ```
   (my height − school avg) = (my height − my grade's avg) + (my grade's avg − school avg)
   ```

   Square both sides, average over the whole school. The square expands into three terms: first leg², second leg², and 2 × (first leg × second leg). Textbooks jump straight to "the cross term is zero". The thought they skip: **fix one grade** - inside it, the second leg (grade avg − school avg) is the same number for every student, a constant, so it pulls out of the average; what's left is the average of the first leg within that grade - deviations around the grade's own average, which average to zero **by definition of an average**. So the cross term dies inside every grade, hence dies overall. What remains:

   ```
   avg[(Y − school avg)²] = avg[(Y − grade avg)²] + avg[(grade avg − school avg)²]
         Var(Y)           =     E[Var(Y|X)]       +      Var(E[Y|X])
   ```

   Interpretation of the two terms:

   - **E[Var(Y|X)]** - within-grade spread, averaged across grades (weighted by grade size). This is Q4's noise floor: the fine even the perfect guesser pays.
   - **Var(E[Y|X])** - how much the grade averages themselves scatter. The part of height that knowing the grade explains. R² = this ÷ total.

   Q4 and Q5 are the same picture read twice: Q4 says "report each grade's average" wins the guessing game; Q5 audits the books - total spread = what the winner still pays + what knowing the grade saved you. (Formally, Q5 is Q4's decomposition with the laziest competitor g = school average entered into the race.)

   Background, two lines: Galton could see both spreads in his 1886 father-son table - the scatter inside each row and the climb of the row medians - but had no quantity that adds. Fisher coined the very word "variance" in 1918 **because** standard deviations don't add and squares do, then ran this identity as an accounting system on farm-trial data: ANOVA is literally this equation applied to yield numbers, and the F-test asks whether the between-group account is too large to be luck.

### 6. `[ML]` The regression function is f(x) = E[Y|X=x]. Why can't we compute it directly from finite data, and what does this force statistical learning to do instead?

   **A**: first, one word needs straightening or the answer runs off track: "expression". The ground truth f(x) = E[Y|X=x] is **not a formula - it's an infinitely long table**: one number per x (that slice's center), assembled into the whole ridge line. It may have no closed form at all - the world is under no obligation to make the ridge look like √x or a polynomial. So the question isn't "why can't we find the formula"; it's more basic: **why can't finite data even pin down the number at each x**.

   The school example shows where the difficulty lives. In Q4/Q5, "grade" had a dozen bins with hundreds of students each - reporting each bin's average was no problem. But real X is continuous. Replace "grade" with "father's height, to the millimeter":

   - **Most slices are empty.** No student's X is exactly 175.382 cm - the slice average becomes 0/0; there is nothing to compute.
   - **The non-empty slices are too thin.** Even with three or five students in a slice, the sample average ≠ the true average - off by noise of order 1/√n. What you computed is "the average of these few darts", not "the slice's true center".
   - **Infinitely many numbers to pin down, finitely many darts.** An infinitely long table, filled with finite information - and with no assumptions, the entries where no dart landed can be anything at all: the data has no say there.

   What this forces statistical learning to do instead: **borrow**. Your slice has no darts, so you need a license to borrow - from the neighbors (smoothness) or from the whole world (a drawing tool / parametric family). Borrow wide and you owe bias; borrow narrow and you pay variance. This is the page on which the entire book (ESL) opens for business.

### 7. `[SC]` Define a discrete-time martingale. Show that a fair-coin random walk is a martingale using the tower property.

### 8. `[SC]` What does "conditioning on the filtration F_t" mean? Give the information interpretation, and explain why E[X_T | F_t] is "the best forecast given what is known at time t."

### 9. `[LLM]` Write the autoregressive factorization p(x_1,…,x_n) = Π_t p(x_t | x_{<t}). Why does every joint distribution admit this factorization with no modeling assumption? Where does the modeling assumption actually enter in an LLM?

### 10. `[SC]` Risk-neutral pricing states V_t = E^Q[e^{−r(T−t)} · payoff | F_t]. Unpack this as a conditional expectation statement: what is being conditioned on, and why?

   **A**: recap the story first. 1654: two players, 32 pistoles each in the pot, first to win 3 rounds takes all 64. The game is interrupted with A leading 2:1 - Pascal split the pot by averaging the payoff over the remaining futures given the score: 48 to A, 16 to B. **The mid-game fair price is a conditional expectation.**

   V_t = E^Q[e^{−r(T−t)} · payoff | F_t] is the same move with three patches:

   - **What is being conditioned on**: F_t is the scoreboard - Pascal's was one number ("A leads 2:1"), a market's is the whole path so far, and it grows with time. That's the filtration. **Why condition at all**: the game isn't over, and the contract must be repriced as information arrives - the conditional expectation IS the mid-game price: average the payoff over the futures still compatible with the scoreboard.

   - **e^{−r(T−t)}**: Pascal's game settled the same evening; an option pays months later, and future money is worth less - discount before averaging. (One line is enough, every interviewer knows what I mean.)

   - **Q**: Pascal got his weights for free - nobody argues with a fair coin's 50/50. Q is **not** anyone's guess of the true odds: it's a doctored set of weights, constructed so that "price = weighted average" admits no free lunch - the risk premium is baked into the weights instead of added on top. (How the doctoring actually works - separate discussion, later.)

   One line to close: Pacioli priced by the past and got it wrong; Pascal priced the futures given the score; finance prices the futures given the path, in discounted money, under doctored weights. Same recipe since 1654.

### 11. `[ML]` The Bayes classifier: what is the optimal prediction in terms of p(y|x)? Show that 0-1 loss leads to the conditional mode and squared loss to the conditional mean.

   **A — the mental model is a table.** Rows = heights (say the dataset only has 160, 165, 170), columns = grades (1-5), each cell = how many students have that height AND that grade. A row's sum = everyone at that height.

   One-line version: told the height, report the grade with the **biggest cell in that row**. That rule is the Bayes classifier, and formally it reads argmax_k p(y=k|x).

   The "show" part takes two lines. Play the guessing game with the new fine - wrong guess costs 1, right guess costs 0. If you report grade k in the 160 row, your average fine is the share of that row NOT in cell k: 1 − (cell k ÷ row sum). Minimizing the fine = maximizing cell k = picking the biggest cell = the conditional **mode**. Under squared loss the same game gave the conditional **mean** (Q4's parabola). The loss picks the summary statistic:

   ```
   squared fine (miss)²    →  report the slice mean      (Q4)
   absolute fine |miss|    →  report the slice median    (Laplace 1774)
   flat fine, wrong = 1    →  report the slice mode      (this question)
   ```

   Four readings of the same table:

   1. **Argmax within a row = the Bayes classifier.** No normalization needed - every cell in the row is divided by the same row sum, so comparing counts and comparing conditional probabilities pick the same winner.
   2. **Row-normalize = p(grade | height)**, the conditional distribution - the slice, classification flavor.
   3. **Column-normalize = p(height | grade)**, the reverse conditional. And here Bayes' theorem collapses into bookkeeping: **the same cell, divided by the row sum or by the column sum** - the flip formula p(A|B) = p(B|A)p(A)/p(B) is just the recipe for rebuilding the row reading out of the column reading. The classifier carries the name Bayes because the classical presentation walks exactly that column-to-row route.
   4. **Per-row, everyone outside the biggest cell gets misclassified.** Row error = (row sum − max cell) ÷ row sum; weight rows by their share and you have the Bayes error - the noise floor of classification, visible cell by cell. Slices where grades overlap heavily = tall floor (ESL ch2's two overlapping clouds: the overlap region is exactly this).

   Two closing notes. First, this is literally Galton's father-son cross-table again: numeric Y, read each row by its **average** = regression; categorical Y, read each row by its **argmax** = classification. Same table, two summaries, chosen by the loss. Second, keep three name-sharers apart: the **Bayes classifier** is a target and a floor (unrunnable - needs the true row compositions); **Naive Bayes** is a runnable approximator of it (assumes features independent within each class to rebuild sparse cells cheaply); **Bayesian statistics** is a worldview about what probability means (beliefs updated prior → posterior). One surname, three jobs.

### 12. `[LLM]` Show that minimizing average cross-entropy over a corpus is estimating the conditional distributions p(x_t|x_{<t}). With an unrestricted model family and infinite data, what would the model converge to?

### 13. `[C]` Regression to the mean: using E[Y|X] for jointly distributed (X, Y) with correlation < 1, explain why extreme observations tend to be followed by less extreme ones (fathers' vs sons' heights).

   **A - first, kill the wrong reading.** This is NOT about fixing x and drawing Y twice: repeated draws inside one slice are independent - the second draw doesn't know the first happened, and nothing compensates. "Last one was extreme, so the next will pull back", said of repeated draws in a fixed slice, is the gambler's fallacy, not regression to the mean.

   The right reading: X itself is the first observation, Y the second - a correlated pair (father's height / son's height, first exam / second exam). The claim: given the first is extreme, the conditional average of the second is less extreme - **measured in each variable's own units of spread**. Standardize both and the whole theorem is one line:

   ```
   E[Y_std | X_std = x] = ρ·x,      |ρ| ≤ 1  always
   ```

   **The skipped step - why (luck doesn't renew).** Each score = level + luck. Now look only at people whose first score was extremely high: they were selected by "score extreme", and among extreme scorers the lucky outnumber the unlucky - level-high-plus-luck-good clears the bar more easily than level-high-plus-luck-bad. So conditioning on an extreme first observation quietly tilts the luck component upward. Second time around: the level carries over, the luck redraws fresh (mean zero) - so the expectation keeps only the level part, which is less than the first score. **Extreme observations carry an inflated share of luck, and luck doesn't renew.**

   Three anchors:

   1. It's a statement about the conditional **average**, not every individual - plenty of sons out-grow extreme fathers.
   2. It's **symmetric in time**: extremely tall sons also have less-tall fathers on average. So it is not a force squeezing the world toward mediocrity (Galton's own first misreading) - the population spread stays constant generation after generation; only the ranking reshuffles. No causality anywhere, pure selection arithmetic.
   3. **The slope caveat.** The raw regression slope β = Cov(X,Y)/Var(X) can exceed 1 - if the sons' spread were double the fathers' and ρ = 0.7, then β = 1.4: "every extra cm of father predicts 1.4 cm of son", which sounds anti-regression. But the theorem lives in standardized units: a +2 σ_X father predicts a +1.4 σ_Y son - less extreme **within his own generation**. Galton got lucky: the two generations' σ matched, so β ≈ ρ ≈ 2/3 and the raw-inch story worked without anyone noticing the assumption.

   The classic trap (Kahneman's flight instructors): praise a great landing - the next one is usually worse; scold a terrible one - the next is usually better; the instructors concluded scolding works and praise backfires. Nothing worked either way: extremes carry inflated luck, and the luck redrew. Same arithmetic behind champion funds turning ordinary the next year and the magazine-cover jinx.

   ---

   **Aside - what does raw covariance even say?** (It entered through β = Cov/Var, and deserves its own paragraph.) The formula:

   ```
   Cov(X,Y) = avg[ (X − mean of X) × (Y − mean of Y) ]
   ```

   is a weighted vote: each observation votes **+** if its two deviations sit on the same side of their means, **−** if opposite sides, and the weight of a vote is the product of the two distances. Cov is the net margin. What's readable: **the sign**. What's not readable: **the magnitude**, twice over -

   - Straight from the formula: replace X by 2X and every product doubles. The relationship didn't change; the number did. Magnitude carries units.
   - Same Cov, different worlds: World A - 100 days, X and Y drift +1/−1 together every day, each vote = 1, Cov = 1. World B - 99 days both flat at their means (vote 0), one day both jump +10 (vote 100), Cov = 100/100 = 1. Daily lockstep and a single joint blow-up are indistinguishable to this number: the formula multiplies frequency-of-agreement by violence-of-agreement and averages them into one figure. (Also the root of why correlation-family models get blamed in crises - steady co-movement and tail co-explosion don't fit in one number.)

   What the formula is actually for - look at its birthplace:

   ```
   Var(X+Y) = avg[((X−μx) + (Y−μy))²] = Var(X) + Var(Y) + 2·avg[(X−μx)(Y−μy)]
   ```

   **Covariance is the 2ab cross term of a squared sum.** It exists because expanding the square forces it into the books; it is what you must track for the variance of any sum - hence any portfolio - to add up. Its job is bookkeeping; the sign's descriptive power is a side effect. Two footnotes: Cov = 0 does not imply independence (X standard normal, Y = X²: Cov = 0, total dependence - covariance only detects the linear channel), and the addability is exactly why risk models store the covariance matrix: portfolio variance w'Σw needs entries you can weight and sum.

### 14. `[SC]` Doob martingale: for integrable Z and filtration F_t, show M_t = E[Z|F_t] is a martingale. Connect this to why discounted prices are Q-martingales.

### 15. `[C]` Capstone: "the regression function", "the discounted price process", and "the next-token head" — write each as a conditional expectation/distribution, then state exactly what differs across the three (conditioning variable, measure, estimation method).

## 2. Linear algebra: matmul · projection · eigendecomposition / SVD

### 1. `[C]` Give three views of matrix multiplication: rows-times-columns, linear combination of columns, and sum of outer products. Why does the outer-product view matter for blocked computation?

   **A**: If you want to multiply two matrices, you can do it row-times-column element by element, or block by block — the block version is the same formula with blocks playing the role of elements. The block version is legal and gives the exact same answer, because each entry of C is a sum over the shared dimension (C_ij = Σ_l a_il·b_lj) — and a sum can be computed in batches: cut the shared dimension into chunks, compute partial products, accumulate. Batching a sum changes nothing.

   And the block version is faster. Why? If your fast memory can fit either two 1×64 vectors or two 8×8 matrices — same 128 numbers — it's better to load the two 8×8 tiles and finish off all the calculations between these two tiles at once (~1,024 FLOPs, every number reused 8 times), rather than load a long vector, use each number once (~128 FLOPs), kick it out, and load it back again later — because over the whole computation the same data gets re-shipped many times, and the transportation is what's slow. Same total FLOPs either way — the win is memory traffic.

### 2. `[C]` Count the FLOPs of an (m×k)(k×n) matmul. Why is matmul the dominant cost in both OLS (∼np²) and transformer inference?

   **A**: An (n×k)(k×m) matmul produces an n×m result; each entry is a length-k dot product — k multiplications and k−1 additions ≈ 2k FLOPs — done n·m times, so total ≈ **2knm**. No dimension is squared per se; a square shows up only when the same size occupies two of the three slots.

   **OLS**: forming XᵀX is (p×n)(n×p) → **2np²** — quadratic in the number of features p, linear in samples n. This dominates when n ≫ p; solving the resulting p×p system adds O(p³).

   **Transformer attention**: the score matmul QKᵀ is (n×d)(d×n) → **2n²d**, quadratic in context length n (and the subsequent scores·V is another 2n²d). The MLP blocks are (n×d)(d×4d)-type → ~8nd², linear in n but quadratic in d. So for long context the n² attention term takes over — the arithmetic root of why long context is hard.

### 3. `[C]` Derive the orthogonal projection of y onto the column space of full-rank X: ŷ = X(XᵀX)⁻¹Xᵀy. What geometric property characterizes the residual y − ŷ?

   **A**: y is the actual data, the real data, and we make a model to predict it — but we can't exactly, we only get an estimate, ŷ. We call the difference e = y − ŷ the error. Meanwhile we have the matrix X — an array of p columns, **each column a vector in n-dimensional space** (one entry per observation), and together the p columns span a **p-dimensional subspace** of that n-dimensional space — the column space, like a surface generated by all the columns.

   We want ‖e‖ small — a large error is a bad fit. How to make it smallest? Make e **perpendicular to the column space**: if e leaned toward any direction in that surface, you could slide ŷ along that direction and get a shorter distance. Perpendicular means Xᵀe = 0. Since e = y − ŷ and ŷ = Xβ̂, unpack: Xᵀ(y − Xβ̂) = 0 → XᵀXβ̂ = Xᵀy → **β̂ = (XᵀX)⁻¹Xᵀy**. Here X and y are collected data — the training set — and we assume it represents reality well.

   With this frozen β̂ we predict on data we've never seen: **ŷ_new = X_new·β̂**, where X_new is the new observations and β̂ = (XᵀX)⁻¹Xᵀy was estimated entirely from the X and y we collected before. Only when X_new is the training X itself does ŷ = X(XᵀX)⁻¹Xᵀy = Hy become a projection — the perpendicularity of residuals is an in-sample property, which is exactly why in-sample fit is optimistic and out-of-sample validation exists.

### 4. `[ML]` OLS as projection: connect β̂ = (XᵀX)⁻¹Xᵀy to the previous question. What are the normal equations geometrically?

   **A**: The confusion starts with the word **"dimension."** To a normal human being, "dimension" sounds like each one adds another level of complexity, or a different *kind* of direction. And when you say "vector," the usual mental image is an arrow pointing somewhere in a space of 1 or 2 dimensions — so the vector had better contain a little bit of every dimension. Then someone says "y is a vector in n-dimensional space" and it throws people off. The subtlety is that y = {y₁, y₂, y₃, …} is just a **series of observations** (n of them): y₂ is not one layer more complex than y₁, and neither is y₃ to y₂ — they're just another sample. So even though the textbook says "n-dimensional vector," it's horrible wording. I don't care how beautiful it is mathematically — poor wording. Read "dimension" as **one more independent slot in a list**, and it stops being mysterious.

   On the other hand, I get why it has to be this way. In the column picture, people collect data **point by point, not feature by feature**. So if y = {y₁, y₂, y₃, …}, then ŷ had better be something similar — at least the same length, an apple-to-apple comparison element by element — so that you can add and subtract them at all. ŷ₁, ŷ₂, ŷ₃, … are the predicted values sitting in the same slots.

   So now both y and ŷ are vectors in ℝⁿ, and we want them **as close to each other as possible**. First place to be careful: **"close" means small distance, not merely similar direction.** e = y − ŷ is the arrow running from ŷ's tip to y's tip, and what we minimize is its **length**, ‖e‖² = Σᵢ(yᵢ − ŷᵢ)² — which is exactly the sum of squared errors. That's the payoff of this setup: minimizing one arrow's length optimizes all n observation errors **in one shot**.

   Second place to be careful — **the angle story**. If the angle between y and ŷ is 0, then cos θ = 1, and for **centered** vectors cos θ *is* the correlation (uncentered it's only cosine similarity, not correlation). But correlation 1 does **not** mean zero error: ŷ pointing exactly along y at twice the length still has cos θ = 1 and a large ‖e‖ — right direction, wrong scale. Angle governs direction only; distance governs direction **and** scale, and OLS minimizes distance. The angle does earn its keep elsewhere, though: **R² is cos² of the angle between centered y and centered ŷ.**

   To build that ŷ you obviously need all your x observations. By x I mean: if there's only 1 feature, it's one column containing all n observations of it; 2 features means 2 columns of observations, and so on. Each column is weighted by the coefficient belonging to that feature — so p features means p columns and p coefficients. And the whole estimation problem is to **find those p coefficients such that, when the columns are weighted by them, the resulting ŷ is as close to the real y as possible.**

   The set of all vectors reachable by weighting the p columns *is* the column space, so that search is the search of Q3, and its winner is the foot of the perpendicular. **Geometrically, the normal equations XᵀXβ̂ = Xᵀy say Xᵀe = 0: no column can see anything left in the residual** — and β̂ is the recipe (the coordinates) of the landing point ŷ = Xβ̂ in terms of the p columns.

### 5. `[C]` Define eigenvalues/eigenvectors; compute them for a 2×2 symmetric matrix. State the spectral theorem for symmetric matrices.

### 6. `[C]` Define positive semidefinite. Show every covariance matrix is PSD, and that PSD implies nonnegative eigenvalues.

### 7. `[C]` State the SVD A = UΣVᵀ. How does the SVD of X relate to the eigendecomposition of XᵀX? State the Eckart–Young low-rank approximation result.

### 8. `[ML]` Derive the first principal component as the maximum-variance direction (Rayleigh quotient → top eigenvector of the covariance). Why center first? Covariance-PCA vs correlation-PCA — when does the choice matter?

### 9. `[SC]` Cholesky factorization: what is it, and how do you use it to turn iid standard normals into correlated normals with a target covariance? (The workhorse of multi-asset Monte Carlo.)

### 10. `[SC]` PCA on yield curves: which matrix do you eigendecompose, and how do the classic level/slope/curvature factors appear in the loadings?

### 11. `[ML]` Ridge as spectral shrinkage: using the SVD of X, show ridge multiplies the component along each uᵢ by σᵢ²/(σᵢ² + λ). Why does damping small-singular-value directions fight collinearity and overfitting?

### 12. `[LLM]` Attention as matmuls: with softmax(z)ᵢ = e^{zᵢ}/Σⱼe^{zⱼ} (taken as given here), write attention(Q,K,V) = softmax(QKᵀ/√d_k)V with explicit shapes for sequence length n. Which computation is O(n²) in time and memory?

### 13. `[LLM]` Blocked matmul: explain how a large matmul is computed tile-by-tile so working blocks fit in fast memory, accumulating partial sums. Why does tiling reduce slow-memory traffic but not FLOPs? (The mechanical idea under FlashAttention.)

### 14. `[LLM]` Low-rank adaptation: why can a weight update ΔW (d×d) be usefully approximated as BA with B, A of rank r ≪ d? Connect to Eckart–Young, and compute the parameter savings.

### 15. `[C]` Capstone: one symmetric matrix, three hats — the return covariance (risk model), XᵀX (regression), and QKᵀ scores (attention). For each, state what its eigenstructure/conditioning means in practice and what goes wrong when it is ill-conditioned (unstable Cholesky / collinear β̂ / degenerate attention).

## 3. Chain rule + Taylor expansion

### 1. `[C]` Chain rule warm-up: differentiate f(g(h(x))) for a concrete triple; then compute ∇ₓ ||Ax − b||².

### 2. `[C]` Multivariable chain rule: for f(u(t), v(t)), write df/dt. (This exact pattern reappears as backprop and as Itô's lemma.)

### 3. `[C]` Write the first- and second-order Taylor expansions of f around x, in one variable and in the gradient–Hessian form.

### 4. `[C]` Using first-order Taylor, show why gradient descent x ← x − η∇f decreases f for small η. What property of f controls how large η can be?

### 5. `[C]` Derive Newton's method from the second-order Taylor expansion. When does it beat gradient descent, and what are its two classic failure modes?

### 6. `[ML]` Define convexity. Show the least-squares loss is convex via its Hessian (PSD, §2). Why does convexity make optimization claims global?

### 7. `[C]` Derive the logsumexp trick log Σe^{zᵢ} = m + log Σe^{zᵢ−m} with m = max zᵢ. Why does the naive version overflow in fp16? Show softmax(z) = exp(z − logsumexp(z)).

### 8. `[LLM]` Backprop is the chain rule on a graph: for a two-layer MLP with scalar loss, derive gradients w.r.t. both weight matrices. Why does reverse-mode differentiation cost about the same as the forward pass, and why is that fact what makes deep learning trainable?

### 9. `[LLM]` Softmax + cross-entropy: with L = −log softmax(z)_y, show ∂L/∂z = p − e_y. Why is this fused form numerically preferable?

### 10. `[SC]` Greeks are derivatives: define delta, gamma, vega, theta. Write the delta-gamma-theta P&L expansion ΔV ≈ δΔS + ½γ(ΔS)² + θΔt and state when the gamma term dominates.

### 11. `[SC]` Quadratic variation: argue heuristically that (dW)² = dt — sum squared Brownian increments over a partition and show the sum concentrates at t.

### 12. `[SC]` State Itô's lemma for f(t, W_t) and derive it heuristically as a second-order Taylor expansion that keeps the (dW)² = dt term. Apply it to d(W_t²).

### 13. `[SC]` For GBM dS = μS dt + σS dW, use Itô to derive d(log S) and the lognormal solution. Identify exactly which Taylor term produces the −½σ².

### 14. `[LLM]` Curvature and training: what do the largest Hessian eigenvalues of the loss surface imply for the learning rate? Give the intuition for why Adam-style per-coordinate rescaling helps when curvature is very anisotropic.

### 15. `[C]` Capstone: the same second-order bookkeeping three ways — delta-gamma expansion, Newton's step, Itô's lemma. For each, name the second-order term you cannot drop and describe what breaks if you do.

## 4. Gaussians & variance scaling laws

### 1. `[C]` Write the N(μ, σ²) density. Show Gaussians are closed under affine maps and under sums of independent Gaussians.

### 2. `[C]` Variance algebra: Var(aX), Var(X+Y) with covariance, and — for n iid terms — the mean and standard deviation of the sum and of the average. State the √n law.

### 3. `[C]` State the CLT. Why do sums of many small independent effects look Gaussian? Give one place it shows up in each of the three directions.

### 4. `[C]` Why does the standard error of a sample mean shrink as 1/√n? How many times more Monte Carlo samples buy one extra decimal digit of accuracy?

### 5. `[SC]` Define Brownian motion via independent Gaussian increments with Var(W_{t+s} − W_t) = s. Why must the sd scale as √t? Sketch why paths are nowhere differentiable.

### 6. `[SC]` Vol annualization: convert daily vol to annual vol via √252. Which independence assumption is buried in this, and how does return autocorrelation break it?

### 7. `[ML]` Show that MLE under y = f(x) + ε with ε ~ N(0, σ²) is exactly least squares. What loss does Laplace noise produce instead, and when would you prefer it?

### 8. `[ML]` Derive the bias–variance decomposition of expected squared prediction error. Which term does increasing model complexity move, and in which direction?

### 9. `[ML]` Multivariate Gaussian: write the density with covariance Σ; describe the level sets via Σ's eigendecomposition (§2). Show the conditional distribution of a bivariate Gaussian is Gaussian with a *linear* conditional mean — the case where the §1 regression function is exactly linear.

### 10. `[LLM]` Initialization: for y = Wx with d-dimensional x (iid, unit variance) and W entries iid with variance σ_w², compute Var(yᵢ). Why choose σ_w² ≈ 1/d (Xavier/He), and what happens across many layers if you don't?

### 11. `[LLM]` The 1/√d_k: compute the variance of q·k for iid mean-0, variance-1 entries. What happens to softmax and its gradients when logits have sd √d_k, and how does dividing by √d_k fix it?

### 12. `[SC]` Fat tails: compare the kurtosis of real returns to Gaussian. Name two mechanisms that generate fat tails (vol clustering/mixtures, jumps) and explain why Gaussian dynamics understate the wings of the implied-vol smile.

### 13. `[ML]` High-dimensional Gaussians concentrate on a thin shell of radius ≈ √d. Derive the intuition and give one practical consequence for nearest-neighbor methods (the ESL Ch 2 curse of dimensionality).

### 14. `[LLM]` Why do deep networks need normalization layers (LayerNorm) to keep activation scale controlled across depth? Connect to the layer-by-layer variance bookkeeping of Q10.

### 15. `[C]` Capstone: collect the square roots — √t (BM), √252 (annualization), 1/√n (MC error), 1/√d_k (attention), 1/√fan-in (init). Show that each is the same additivity-of-variance argument and name the independence assumption each one leans on.

## 5. Likelihood · cross-entropy · KL · change of measure

### 1. `[C]` Define the likelihood of iid data. Why maximize the log-likelihood instead of the likelihood itself?

### 2. `[C]` Derive the MLE of p from n coin flips, and of (μ, σ²) from Gaussian data. Is the σ² MLE biased?

### 3. `[ML]` Logistic regression: write p(y=1|x) = σ(wᵀx), show its negative log-likelihood is the cross-entropy/log-loss, and compute the gradient (same structure as §3 Q9).

### 4. `[C]` Define entropy H(p). Compute it for fair and biased coins. Which distribution over k outcomes maximizes it?

### 5. `[C]` Define cross-entropy H(p,q) and KL(p||q) = H(p,q) − H(p). Prove KL ≥ 0 via Jensen. Give a concrete two-point example showing KL is asymmetric.

### 6. `[C]` Show that maximizing average log-likelihood is (up to a constant) minimizing KL(p̂_data || p_model). What does this objective make the model care about?

### 7. `[LLM]` The LLM objective is per-token cross-entropy. Define perplexity = exp(average NLL) and interpret it as an effective branching factor. How does teacher forcing turn training into a sum of §1-style conditional estimation problems?

### 8. `[C]` Define the likelihood ratio Λ(x) = p(x)/q(x). State Neyman–Pearson informally: why is thresholding Λ the optimal way to decide between two hypotheses?

### 9. `[SC]` Change of measure in discrete space: fair coin P vs biased coin Q over n-flip paths. Compute dQ/dP on a path and verify E^Q[X] = E^P[X · dQ/dP] — reweighting by a likelihood ratio.

### 10. `[SC]` Importance sampling: derive E_p[f(X)] = E_q[f(X)p(X)/q(X)]. When does it reduce variance, when does it blow up, and why is deep-OTM option pricing the textbook use case?

### 11. `[SC]` Girsanov at statement level: under an equivalent measure change, Brownian motion gains a drift but keeps its volatility. Why does risk-neutral pricing change μ → r but never σ? Connect dQ/dP to Q9's path likelihood ratio.

### 12. `[ML]` Why is log-loss a proper scoring rule (honest probabilities optimal)? Contrast evaluating a probabilistic classifier by accuracy vs by log-loss.

### 13. `[LLM]` Temperature: p_T = softmax(z/T). How does T reshape entropy? Show p_T is an exponential tilting of p₁ — i.e., a reweighting in the same likelihood-ratio family.

### 14. `[LLM]` RLHF: the objective max E[reward] − β·KL(π || π_ref). Why is the KL anchor there (support control, reward-hacking prevention)? Describe behavior as β → 0 and β → ∞, and relate it to importance-weight degeneracy from Q10.

### 15. `[C]` Capstone: the likelihood-ratio family portrait — MLE (fit by minimizing KL), Neyman–Pearson (decide by LR), Girsanov (price by LR), importance sampling (integrate by LR), RLHF (regularize by KL). Write down the LR/KL object in each and its role in one sentence.

## 6. Sampling / Monte Carlo

### 1. `[C]` The crude MC estimator for E[f(X)]: why is it unbiased, and what is its standard error (§4 Q4)?

### 2. `[C]` Estimate π by uniform darts on a square with an inscribed circle. Compute the estimator's variance — why is this just Bernoulli mean estimation?

### 3. `[C]` Inverse-transform sampling: show F⁻¹(U) has CDF F for U ~ Uniform(0,1). Use it to sample an exponential.

### 4. `[C]` Rejection sampling: describe the algorithm, compute the acceptance rate, and explain why it collapses in high dimensions.

### 5. `[SC]` Simulate GBM two ways: the exact lognormal scheme (§3 Q13) vs Euler–Maruyama on the SDE. Why prefer exact when available, and what bias does Euler introduce?

### 6. `[SC]` Price a European call by MC under Q with a standard-error bar. Then price an arithmetic-average Asian option — why is MC natural exactly where closed forms fail?

### 7. `[SC]` Variance reduction: antithetic variates and control variates (e.g., geometric-Asian closed form as control for the arithmetic Asian). When does each help, and how do you measure the gain?

### 8. `[ML]` Bootstrap: build a confidence interval for a statistic (say, a Sharpe ratio) by resampling. Why does the plug-in principle work, and when does it fail (heavy tails; serial dependence → block bootstrap)?

### 9. `[ML]` Cross-validation as resampling: what quantity does K-fold CV actually estimate, and for what (the procedure, not the fitted model)? Why does naive CV leak on time series, and what do purging and embargo fix?

### 10. `[ML]` Bagging: why does averaging models fit on bootstrap resamples reduce variance (§4 Q2), and why does correlation between the models cap the benefit? How do random forests attack that correlation?

### 11. `[LLM]` Decoding: define greedy, temperature, top-k, and top-p (nucleus) sampling precisely, given final logits z. Why does pure sampling degrade over long generations and greedy become repetitive?

### 12. `[LLM]` Sampling for uncertainty: self-consistency (sample k reasoning paths, majority-vote) and MC dropout. What is the shared statistical idea, and what does it estimate?

### 13. `[SC]` Importance sampling as variance reduction (§5 Q10): design a tilted proposal for a rare-event probability (a deep-OTM digital). What is weight degeneracy and how do you diagnose it?

### 14. `[C]` MCMC at concept level: why is it needed when you can only evaluate an unnormalized density? Sketch Metropolis–Hastings and why detailed balance yields the right stationary distribution. One use per direction.

### 15. `[C]` Capstone drill: estimate a small tail probability three ways — (a) crude MC, (b) one variance-reduction technique of your choice, (c) importance sampling. For each: the estimator, the unbiasedness argument, and the variance behavior. (The same pattern prices rare payoffs, sizes strategy tail risk, and estimates rare LLM failure rates in evals.)
