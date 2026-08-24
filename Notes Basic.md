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

1. `[C]` Define E[Y|X=x] for discrete random variables. Compute a concrete example: roll two dice, find E[sum | first die = 3].
2. `[C]` State the tower property (law of total expectation) E[E[Y|X]] = E[Y]. Verify it on the dice example above.
3. `[C]` E[Y|X=x] is a number; E[Y|X] is a random variable (a function of X). Explain the distinction and why it matters.
4. `[C]` Show that the function g minimizing E[(Y − g(X))²] is g(X) = E[Y|X]. (The L² projection property — the single most reused fact in all three directions.)
5. `[C]` State and prove the conditional variance decomposition Var(Y) = E[Var(Y|X)] + Var(E[Y|X]). Interpret both terms.
6. `[ML]` The regression function is f(x) = E[Y|X=x]. Why can't we compute it directly from finite data, and what does this force statistical learning to do instead?
7. `[SC]` Define a discrete-time martingale. Show that a fair-coin random walk is a martingale using the tower property.
8. `[SC]` What does "conditioning on the filtration F_t" mean? Give the information interpretation, and explain why E[X_T | F_t] is "the best forecast given what is known at time t."
9. `[LLM]` Write the autoregressive factorization p(x_1,…,x_n) = Π_t p(x_t | x_{<t}). Why does every joint distribution admit this factorization with no modeling assumption? Where does the modeling assumption actually enter in an LLM?
10. `[SC]` Risk-neutral pricing states V_t = E^Q[e^{−r(T−t)} · payoff | F_t]. Unpack this as a conditional expectation statement: what is being conditioned on, and why?
11. `[ML]` The Bayes classifier: what is the optimal prediction in terms of p(y|x)? Show that 0-1 loss leads to the conditional mode and squared loss to the conditional mean.
12. `[LLM]` Show that minimizing average cross-entropy over a corpus is estimating the conditional distributions p(x_t|x_{<t}). With an unrestricted model family and infinite data, what would the model converge to?
13. `[C]` Regression to the mean: using E[Y|X] for jointly distributed (X, Y) with correlation < 1, explain why extreme observations tend to be followed by less extreme ones (fathers' vs sons' heights).
14. `[SC]` Doob martingale: for integrable Z and filtration F_t, show M_t = E[Z|F_t] is a martingale. Connect this to why discounted prices are Q-martingales.
15. `[C]` Capstone: "the regression function", "the discounted price process", and "the next-token head" — write each as a conditional expectation/distribution, then state exactly what differs across the three (conditioning variable, measure, estimation method).

## 2. Linear algebra: matmul · projection · eigendecomposition / SVD

1. `[C]` Give three views of matrix multiplication: rows-times-columns, linear combination of columns, and sum of outer products. Why does the outer-product view matter for blocked computation?

   **A**: If you want to multiply two matrices, you can do it row-times-column element by element, or block by block — the block version is the same formula with blocks playing the role of elements. The block version is legal and gives the exact same answer, because each entry of C is a sum over the shared dimension (C_ij = Σ_l a_il·b_lj) — and a sum can be computed in batches: cut the shared dimension into chunks, compute partial products, accumulate. Batching a sum changes nothing.

   And the block version is faster. Why? If your fast memory can fit either two 1×64 vectors or two 8×8 matrices — same 128 numbers — it's better to load the two 8×8 tiles and finish off all the calculations between these two tiles at once (~1,024 FLOPs, every number reused 8 times), rather than load a long vector, use each number once (~128 FLOPs), kick it out, and load it back again later — because over the whole computation the same data gets re-shipped many times, and the transportation is what's slow. Same total FLOPs either way — the win is memory traffic.

2. `[C]` Count the FLOPs of an (m×k)(k×n) matmul. Why is matmul the dominant cost in both OLS (∼np²) and transformer inference?

   **A**: An (n×k)(k×m) matmul produces an n×m result; each entry is a length-k dot product — k multiplications and k−1 additions ≈ 2k FLOPs — done n·m times, so total ≈ **2knm**. No dimension is squared per se; a square shows up only when the same size occupies two of the three slots.

   **OLS**: forming XᵀX is (p×n)(n×p) → **2np²** — quadratic in the number of features p, linear in samples n. This dominates when n ≫ p; solving the resulting p×p system adds O(p³).

   **Transformer attention**: the score matmul QKᵀ is (n×d)(d×n) → **2n²d**, quadratic in context length n (and the subsequent scores·V is another 2n²d). The MLP blocks are (n×d)(d×4d)-type → ~8nd², linear in n but quadratic in d. So for long context the n² attention term takes over — the arithmetic root of why long context is hard.

3. `[C]` Derive the orthogonal projection of y onto the column space of full-rank X: ŷ = X(XᵀX)⁻¹Xᵀy. What geometric property characterizes the residual y − ŷ?

   **A**: y is the actual data, the real data, and we make a model to predict it — but we can't exactly, we only get an estimate, ŷ. We call the difference e = y − ŷ the error. Meanwhile we have the matrix X — an array of p columns, **each column a vector in n-dimensional space** (one entry per observation), and together the p columns span a **p-dimensional subspace** of that n-dimensional space — the column space, like a surface generated by all the columns.

   We want ‖e‖ small — a large error is a bad fit. How to make it smallest? Make e **perpendicular to the column space**: if e leaned toward any direction in that surface, you could slide ŷ along that direction and get a shorter distance. Perpendicular means Xᵀe = 0. Since e = y − ŷ and ŷ = Xβ̂, unpack: Xᵀ(y − Xβ̂) = 0 → XᵀXβ̂ = Xᵀy → **β̂ = (XᵀX)⁻¹Xᵀy**. Here X and y are collected data — the training set — and we assume it represents reality well.

   With this frozen β̂ we predict on data we've never seen: **ŷ_new = X_new·β̂**, where X_new is the new observations and β̂ = (XᵀX)⁻¹Xᵀy was estimated entirely from the X and y we collected before. Only when X_new is the training X itself does ŷ = X(XᵀX)⁻¹Xᵀy = Hy become a projection — the perpendicularity of residuals is an in-sample property, which is exactly why in-sample fit is optimistic and out-of-sample validation exists.

4. `[ML]` OLS as projection: connect β̂ = (XᵀX)⁻¹Xᵀy to the previous question. What are the normal equations geometrically?

   **A**: The confusion starts with the word **"dimension."** To a normal human being, "dimension" sounds like each one adds another level of complexity, or a different *kind* of direction. And when you say "vector," the usual mental image is an arrow pointing somewhere in a space of 1 or 2 dimensions — so the vector had better contain a little bit of every dimension. Then someone says "y is a vector in n-dimensional space" and it throws people off. The subtlety is that y = {y₁, y₂, y₃, …} is just a **series of observations** (n of them): y₂ is not one layer more complex than y₁, and neither is y₃ to y₂ — they're just another sample. So even though the textbook says "n-dimensional vector," it's horrible wording. I don't care how beautiful it is mathematically — poor wording. Read "dimension" as **one more independent slot in a list**, and it stops being mysterious.

   On the other hand, I get why it has to be this way. In the column picture, people collect data **point by point, not feature by feature**. So if y = {y₁, y₂, y₃, …}, then ŷ had better be something similar — at least the same length, an apple-to-apple comparison element by element — so that you can add and subtract them at all. ŷ₁, ŷ₂, ŷ₃, … are the predicted values sitting in the same slots.

   So now both y and ŷ are vectors in ℝⁿ, and we want them **as close to each other as possible**. First place to be careful: **"close" means small distance, not merely similar direction.** e = y − ŷ is the arrow running from ŷ's tip to y's tip, and what we minimize is its **length**, ‖e‖² = Σᵢ(yᵢ − ŷᵢ)² — which is exactly the sum of squared errors. That's the payoff of this setup: minimizing one arrow's length optimizes all n observation errors **in one shot**.

   Second place to be careful — **the angle story**. If the angle between y and ŷ is 0, then cos θ = 1, and for **centered** vectors cos θ *is* the correlation (uncentered it's only cosine similarity, not correlation). But correlation 1 does **not** mean zero error: ŷ pointing exactly along y at twice the length still has cos θ = 1 and a large ‖e‖ — right direction, wrong scale. Angle governs direction only; distance governs direction **and** scale, and OLS minimizes distance. The angle does earn its keep elsewhere, though: **R² is cos² of the angle between centered y and centered ŷ.**

   To build that ŷ you obviously need all your x observations. By x I mean: if there's only 1 feature, it's one column containing all n observations of it; 2 features means 2 columns of observations, and so on. Each column is weighted by the coefficient belonging to that feature — so p features means p columns and p coefficients. And the whole estimation problem is to **find those p coefficients such that, when the columns are weighted by them, the resulting ŷ is as close to the real y as possible.**

   The set of all vectors reachable by weighting the p columns *is* the column space, so that search is the search of Q3, and its winner is the foot of the perpendicular. **Geometrically, the normal equations XᵀXβ̂ = Xᵀy say Xᵀe = 0: no column can see anything left in the residual** — and β̂ is the recipe (the coordinates) of the landing point ŷ = Xβ̂ in terms of the p columns.

5. `[C]` Define eigenvalues/eigenvectors; compute them for a 2×2 symmetric matrix. State the spectral theorem for symmetric matrices.
6. `[C]` Define positive semidefinite. Show every covariance matrix is PSD, and that PSD implies nonnegative eigenvalues.
7. `[C]` State the SVD A = UΣVᵀ. How does the SVD of X relate to the eigendecomposition of XᵀX? State the Eckart–Young low-rank approximation result.
8. `[ML]` Derive the first principal component as the maximum-variance direction (Rayleigh quotient → top eigenvector of the covariance). Why center first? Covariance-PCA vs correlation-PCA — when does the choice matter?
9. `[SC]` Cholesky factorization: what is it, and how do you use it to turn iid standard normals into correlated normals with a target covariance? (The workhorse of multi-asset Monte Carlo.)
10. `[SC]` PCA on yield curves: which matrix do you eigendecompose, and how do the classic level/slope/curvature factors appear in the loadings?
11. `[ML]` Ridge as spectral shrinkage: using the SVD of X, show ridge multiplies the component along each uᵢ by σᵢ²/(σᵢ² + λ). Why does damping small-singular-value directions fight collinearity and overfitting?
12. `[LLM]` Attention as matmuls: with softmax(z)ᵢ = e^{zᵢ}/Σⱼe^{zⱼ} (taken as given here), write attention(Q,K,V) = softmax(QKᵀ/√d_k)V with explicit shapes for sequence length n. Which computation is O(n²) in time and memory?
13. `[LLM]` Blocked matmul: explain how a large matmul is computed tile-by-tile so working blocks fit in fast memory, accumulating partial sums. Why does tiling reduce slow-memory traffic but not FLOPs? (The mechanical idea under FlashAttention.)
14. `[LLM]` Low-rank adaptation: why can a weight update ΔW (d×d) be usefully approximated as BA with B, A of rank r ≪ d? Connect to Eckart–Young, and compute the parameter savings.
15. `[C]` Capstone: one symmetric matrix, three hats — the return covariance (risk model), XᵀX (regression), and QKᵀ scores (attention). For each, state what its eigenstructure/conditioning means in practice and what goes wrong when it is ill-conditioned (unstable Cholesky / collinear β̂ / degenerate attention).

## 3. Chain rule + Taylor expansion

1. `[C]` Chain rule warm-up: differentiate f(g(h(x))) for a concrete triple; then compute ∇ₓ ||Ax − b||².
2. `[C]` Multivariable chain rule: for f(u(t), v(t)), write df/dt. (This exact pattern reappears as backprop and as Itô's lemma.)
3. `[C]` Write the first- and second-order Taylor expansions of f around x, in one variable and in the gradient–Hessian form.
4. `[C]` Using first-order Taylor, show why gradient descent x ← x − η∇f decreases f for small η. What property of f controls how large η can be?
5. `[C]` Derive Newton's method from the second-order Taylor expansion. When does it beat gradient descent, and what are its two classic failure modes?
6. `[ML]` Define convexity. Show the least-squares loss is convex via its Hessian (PSD, §2). Why does convexity make optimization claims global?
7. `[C]` Derive the logsumexp trick log Σe^{zᵢ} = m + log Σe^{zᵢ−m} with m = max zᵢ. Why does the naive version overflow in fp16? Show softmax(z) = exp(z − logsumexp(z)).
8. `[LLM]` Backprop is the chain rule on a graph: for a two-layer MLP with scalar loss, derive gradients w.r.t. both weight matrices. Why does reverse-mode differentiation cost about the same as the forward pass, and why is that fact what makes deep learning trainable?
9. `[LLM]` Softmax + cross-entropy: with L = −log softmax(z)_y, show ∂L/∂z = p − e_y. Why is this fused form numerically preferable?
10. `[SC]` Greeks are derivatives: define delta, gamma, vega, theta. Write the delta-gamma-theta P&L expansion ΔV ≈ δΔS + ½γ(ΔS)² + θΔt and state when the gamma term dominates.
11. `[SC]` Quadratic variation: argue heuristically that (dW)² = dt — sum squared Brownian increments over a partition and show the sum concentrates at t.
12. `[SC]` State Itô's lemma for f(t, W_t) and derive it heuristically as a second-order Taylor expansion that keeps the (dW)² = dt term. Apply it to d(W_t²).
13. `[SC]` For GBM dS = μS dt + σS dW, use Itô to derive d(log S) and the lognormal solution. Identify exactly which Taylor term produces the −½σ².
14. `[LLM]` Curvature and training: what do the largest Hessian eigenvalues of the loss surface imply for the learning rate? Give the intuition for why Adam-style per-coordinate rescaling helps when curvature is very anisotropic.
15. `[C]` Capstone: the same second-order bookkeeping three ways — delta-gamma expansion, Newton's step, Itô's lemma. For each, name the second-order term you cannot drop and describe what breaks if you do.

## 4. Gaussians & variance scaling laws

1. `[C]` Write the N(μ, σ²) density. Show Gaussians are closed under affine maps and under sums of independent Gaussians.
2. `[C]` Variance algebra: Var(aX), Var(X+Y) with covariance, and — for n iid terms — the mean and standard deviation of the sum and of the average. State the √n law.
3. `[C]` State the CLT. Why do sums of many small independent effects look Gaussian? Give one place it shows up in each of the three directions.
4. `[C]` Why does the standard error of a sample mean shrink as 1/√n? How many times more Monte Carlo samples buy one extra decimal digit of accuracy?
5. `[SC]` Define Brownian motion via independent Gaussian increments with Var(W_{t+s} − W_t) = s. Why must the sd scale as √t? Sketch why paths are nowhere differentiable.
6. `[SC]` Vol annualization: convert daily vol to annual vol via √252. Which independence assumption is buried in this, and how does return autocorrelation break it?
7. `[ML]` Show that MLE under y = f(x) + ε with ε ~ N(0, σ²) is exactly least squares. What loss does Laplace noise produce instead, and when would you prefer it?
8. `[ML]` Derive the bias–variance decomposition of expected squared prediction error. Which term does increasing model complexity move, and in which direction?
9. `[ML]` Multivariate Gaussian: write the density with covariance Σ; describe the level sets via Σ's eigendecomposition (§2). Show the conditional distribution of a bivariate Gaussian is Gaussian with a *linear* conditional mean — the case where the §1 regression function is exactly linear.
10. `[LLM]` Initialization: for y = Wx with d-dimensional x (iid, unit variance) and W entries iid with variance σ_w², compute Var(yᵢ). Why choose σ_w² ≈ 1/d (Xavier/He), and what happens across many layers if you don't?
11. `[LLM]` The 1/√d_k: compute the variance of q·k for iid mean-0, variance-1 entries. What happens to softmax and its gradients when logits have sd √d_k, and how does dividing by √d_k fix it?
12. `[SC]` Fat tails: compare the kurtosis of real returns to Gaussian. Name two mechanisms that generate fat tails (vol clustering/mixtures, jumps) and explain why Gaussian dynamics understate the wings of the implied-vol smile.
13. `[ML]` High-dimensional Gaussians concentrate on a thin shell of radius ≈ √d. Derive the intuition and give one practical consequence for nearest-neighbor methods (the ESL Ch 2 curse of dimensionality).
14. `[LLM]` Why do deep networks need normalization layers (LayerNorm) to keep activation scale controlled across depth? Connect to the layer-by-layer variance bookkeeping of Q10.
15. `[C]` Capstone: collect the square roots — √t (BM), √252 (annualization), 1/√n (MC error), 1/√d_k (attention), 1/√fan-in (init). Show that each is the same additivity-of-variance argument and name the independence assumption each one leans on.

## 5. Likelihood · cross-entropy · KL · change of measure

1. `[C]` Define the likelihood of iid data. Why maximize the log-likelihood instead of the likelihood itself?
2. `[C]` Derive the MLE of p from n coin flips, and of (μ, σ²) from Gaussian data. Is the σ² MLE biased?
3. `[ML]` Logistic regression: write p(y=1|x) = σ(wᵀx), show its negative log-likelihood is the cross-entropy/log-loss, and compute the gradient (same structure as §3 Q9).
4. `[C]` Define entropy H(p). Compute it for fair and biased coins. Which distribution over k outcomes maximizes it?
5. `[C]` Define cross-entropy H(p,q) and KL(p||q) = H(p,q) − H(p). Prove KL ≥ 0 via Jensen. Give a concrete two-point example showing KL is asymmetric.
6. `[C]` Show that maximizing average log-likelihood is (up to a constant) minimizing KL(p̂_data || p_model). What does this objective make the model care about?
7. `[LLM]` The LLM objective is per-token cross-entropy. Define perplexity = exp(average NLL) and interpret it as an effective branching factor. How does teacher forcing turn training into a sum of §1-style conditional estimation problems?
8. `[C]` Define the likelihood ratio Λ(x) = p(x)/q(x). State Neyman–Pearson informally: why is thresholding Λ the optimal way to decide between two hypotheses?
9. `[SC]` Change of measure in discrete space: fair coin P vs biased coin Q over n-flip paths. Compute dQ/dP on a path and verify E^Q[X] = E^P[X · dQ/dP] — reweighting by a likelihood ratio.
10. `[SC]` Importance sampling: derive E_p[f(X)] = E_q[f(X)p(X)/q(X)]. When does it reduce variance, when does it blow up, and why is deep-OTM option pricing the textbook use case?
11. `[SC]` Girsanov at statement level: under an equivalent measure change, Brownian motion gains a drift but keeps its volatility. Why does risk-neutral pricing change μ → r but never σ? Connect dQ/dP to Q9's path likelihood ratio.
12. `[ML]` Why is log-loss a proper scoring rule (honest probabilities optimal)? Contrast evaluating a probabilistic classifier by accuracy vs by log-loss.
13. `[LLM]` Temperature: p_T = softmax(z/T). How does T reshape entropy? Show p_T is an exponential tilting of p₁ — i.e., a reweighting in the same likelihood-ratio family.
14. `[LLM]` RLHF: the objective max E[reward] − β·KL(π || π_ref). Why is the KL anchor there (support control, reward-hacking prevention)? Describe behavior as β → 0 and β → ∞, and relate it to importance-weight degeneracy from Q10.
15. `[C]` Capstone: the likelihood-ratio family portrait — MLE (fit by minimizing KL), Neyman–Pearson (decide by LR), Girsanov (price by LR), importance sampling (integrate by LR), RLHF (regularize by KL). Write down the LR/KL object in each and its role in one sentence.

## 6. Sampling / Monte Carlo

1. `[C]` The crude MC estimator for E[f(X)]: why is it unbiased, and what is its standard error (§4 Q4)?
2. `[C]` Estimate π by uniform darts on a square with an inscribed circle. Compute the estimator's variance — why is this just Bernoulli mean estimation?
3. `[C]` Inverse-transform sampling: show F⁻¹(U) has CDF F for U ~ Uniform(0,1). Use it to sample an exponential.
4. `[C]` Rejection sampling: describe the algorithm, compute the acceptance rate, and explain why it collapses in high dimensions.
5. `[SC]` Simulate GBM two ways: the exact lognormal scheme (§3 Q13) vs Euler–Maruyama on the SDE. Why prefer exact when available, and what bias does Euler introduce?
6. `[SC]` Price a European call by MC under Q with a standard-error bar. Then price an arithmetic-average Asian option — why is MC natural exactly where closed forms fail?
7. `[SC]` Variance reduction: antithetic variates and control variates (e.g., geometric-Asian closed form as control for the arithmetic Asian). When does each help, and how do you measure the gain?
8. `[ML]` Bootstrap: build a confidence interval for a statistic (say, a Sharpe ratio) by resampling. Why does the plug-in principle work, and when does it fail (heavy tails; serial dependence → block bootstrap)?
9. `[ML]` Cross-validation as resampling: what quantity does K-fold CV actually estimate, and for what (the procedure, not the fitted model)? Why does naive CV leak on time series, and what do purging and embargo fix?
10. `[ML]` Bagging: why does averaging models fit on bootstrap resamples reduce variance (§4 Q2), and why does correlation between the models cap the benefit? How do random forests attack that correlation?
11. `[LLM]` Decoding: define greedy, temperature, top-k, and top-p (nucleus) sampling precisely, given final logits z. Why does pure sampling degrade over long generations and greedy become repetitive?
12. `[LLM]` Sampling for uncertainty: self-consistency (sample k reasoning paths, majority-vote) and MC dropout. What is the shared statistical idea, and what does it estimate?
13. `[SC]` Importance sampling as variance reduction (§5 Q10): design a tilted proposal for a rare-event probability (a deep-OTM digital). What is weight degeneracy and how do you diagnose it?
14. `[C]` MCMC at concept level: why is it needed when you can only evaluate an unnormalized density? Sketch Metropolis–Hastings and why detailed balance yields the right stationary distribution. One use per direction.
15. `[C]` Capstone drill: estimate a small tail probability three ways — (a) crude MC, (b) one variance-reduction technique of your choice, (c) importance sampling. For each: the estimator, the unbiasedness argument, and the variance behavior. (The same pattern prices rare payoffs, sizes strategy tail risk, and estimates rare LLM failure rates in evals.)
