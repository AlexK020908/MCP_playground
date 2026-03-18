# CPSC 440 — Quiz 5 Study Guide (Elaborated)  
**UBC · From quiz materials + course outline · Slides-style, no formulas**

---

## 1. Representation learning

### Non-variational autoencoders
- **Autoencoders** encode input into a low-dimensional latent, decode back, and try to match the input.
- **Non-variational** means no probabilistic latent (no VAE-style prior/ELBO); just encode–decode–reconstruct.
- Goal is a **compact representation** that reconstructs well; the latent may or may not be “useful” in other ways.

### Uses of representation learning
- **Interpretable latent factors** (e.g. disentangled factors).
- **More meaningful distance** between inputs in latent space.
- **Easier supervised learning** when downstream tasks use the learned representation.
- Often the main topic of modern ML: many methods (AEs, VAEs, contrastive, etc.) learn representations.

### MLE ≠ "most useful representation"
- **MLE** trains the model to maximize likelihood (or reconstruction); it does **not** explicitly optimize for “useful” or interpretable representations.
- Whether the representation is useful depends on architecture, what SGD finds, and the task—so MLE can give a representation that is good for likelihood but not for your downstream use.

### Vague sense that it might be useful anyway
- In practice, AEs/VAEs often yield representations that help with visualization, clustering, or transfer, even though that isn’t the training objective.
- So there’s a loose intuition that “fitting the data well” can still give something useful, but it’s not guaranteed.

---

## 2. Image generative models

### High-level idea: denoising and connection to VAE
- **Diffusion** (and similar models) learn to **denoise**: given a noisy image, predict and remove noise. Doing this over many steps gives a **generative model** (you generate by iteratively denoising from noise).
- **Connection to VAE:** both use a latent/noise space and a learned mapping (decoder / denoising process). Diffusion can be viewed as a kind of hierarchical latent model where each step is a “layer” of noise; the high-level idea of “learn a generative process in a structured space” is shared with VAEs.

### No formulas
- Keep the story at the level above: denoising over time → generative model; conceptual link to latent variable / VAE-style thinking.

### Likelihood vs sample quality in high dimensions
- **Likelihood** measures how much probability mass the model puts on the data; in high dimensions (e.g. images) it can be dominated by many low-probability regions and not reflect “how good samples look.”
- **Sample quality** is about whether samples are sharp, diverse, and realistic. A model can have high likelihood but blurry or poor samples, or reasonable samples but tricky likelihood (e.g. mode collapse, calibration). So in high dimensions, **likelihood and sample quality can diverge**.

---

## 3. Markov chains

### Chain rule: factorizing any distribution into conditional 1D distributions
- The **chain rule** writes the joint as a product: \(p(x_1)\), then \(p(x_2|x_1)\), then \(p(x_3|x_1,x_2)\), …, then \(p(x_d|x_1,\ldots,x_{d-1})\). So any joint is a product of **univariate conditionals**; each factor is a 1D distribution given the “past.” This turns multivariate density estimation into a sequence of 1D problems, but the conditionals can be huge (e.g. \(p(x_d | x_1,\ldots,x_{d-1})\) has many conditioning variables).

### Markov assumption — what it is and why it makes this tractable
- **Markov property:** \(p(x_j | x_{j-1}, x_{j-2}, \ldots, x_1) = p(x_j | x_{j-1})\). So “given the previous step, the past doesn’t matter.”
- That **reduces each conditional to depend only on the previous variable**, so we only need \(p(x_1)\) and \(p(x_j | x_{j-1})\) for \(j=2,\ldots,d\). Few parameters, tractable inference (e.g. CK equations, Viterbi).

### Resulting model: a Markov chain
- **States** (e.g. rain / not rain), **initial distribution** \(p(x_1)\), and **transition probabilities** \(p(x_j | x_{j-1})\) (same for all \(j\) if homogeneous). The joint is \(p(x_1) \prod_{j=2}^d p(x_j | x_{j-1})\). Used for sequences, time series, and as a building block for inference (e.g. MCMC).

### Homogeneous vs inhomogeneous chains
- **Homogeneous:** same transition \(p(x_j | x_{j-1})\) for all \(j\). Good when “time” doesn’t change the dynamics (e.g. rain day-to-day); parameter tying gives more data per parameter and works for any sequence length.
- **Inhomogeneous:** different \(p(x_j | x_{j-1})\) per \(j\). Good when position matters (e.g. pixels in an image); more flexible but needs many sequences of the same length and can overfit.

### MLE in this setting
- For **discrete** chains with tabular parameters: count transitions. MLE for \(p(x_j = c' | x_{j-1} = c)\) is (number of \(c \to c'\)) / (number of times in \(c\)). Same idea for initial distribution. **Learning is counting.**

### Ancestral sampling from Markov chains
- **Ancestral sampling** uses the chain rule: sample \(x_1 \sim p(x_1)\), then \(x_2 \sim p(x_2|x_1)\), then \(x_3 \sim p(x_3|x_2)\), etc. For a Markov chain this is: sample initial state, then repeatedly sample the next state from the transition distribution. Simple and exact.

### Computing marginal probabilities with the CK equations
- **Chapman–Kolmogorov (CK) equations:** \(p(x_j)\) is computed from \(p(x_{j-1})\) by summing over the previous state: \(p(x_j) = \sum_{x_{j-1}} p(x_j | x_{j-1})\, p(x_{j-1})\). Start from \(p(x_1)\), iterate forward. For discrete chains this is **matrix–vector multiplication** (transition matrix times marginal vector); cost \(O(dk^2)\) for \(d\) steps and \(k\) states.

### Stationary distribution: definition and basic idea
- A **stationary (invariant) distribution** \(\pi\) satisfies: if the marginal at time \(j-1\) is \(\pi\), then after one step the marginal is still \(\pi\). So “marginals don’t change over time.” It does *not* mean the chain stays at one state; the distribution is fixed. Under conditions (e.g. ergodicity), marginals converge to the stationary distribution as \(j \to \infty\). Example: PageRank is the stationary distribution of a “random surfer” Markov chain.

### Message passing in Markov chains
- **Message passing** is computing quantities (e.g. marginals, conditionals) by passing “messages” along the chain. **Forward messages** (CK-style): from time 1 toward \(d\). **Backward messages**: from \(d\) toward 1. Used for marginals, conditionals, and in algorithms like forward–backward (not required for this quiz).

### Why the mode of a sequence ≠ mode of each marginal
- The **mode of the sequence** is \(\arg\max_{x_1,\ldots,x_d} p(x_1,\ldots,x_d)\) (jointly best assignment). The **mode of each marginal** is \(\arg\max_{x_j} p(x_j)\) per \(j\). Taking the per-step marginal modes can give a **sequence that has probability zero** (e.g. incompatible transitions). Example: most likely at time 1 might be “catch-bus,” at time 2 “miss-class,” but \(p(\text{miss-class} | \text{catch-bus}) = 0\), so (catch-bus, miss-class) is not the mode of the joint. Decoding must consider the **joint** (e.g. Viterbi).

---

## 4. Viterbi decoding

### General idea / setup
- **Decoding** = find the sequence \(x_1,\ldots,x_d\) that **maximizes the joint probability** \(p(x_1,\ldots,x_d)\). Used in Markov chains (and HMMs) for “most likely path.” You cannot just take the mode of each marginal; you need the global maximizer.

### The algorithm
- **Viterbi** is **dynamic programming**:
  1. **Sub-problem:** \(M_j(x_j)\) = maximum probability of any sequence up to time \(j\) that **ends in** state \(x_j\).
  2. **Base:** \(M_1(x_1) = p(x_1)\).
  3. **Recursion:** \(M_j(x_j) = \max_{x_{j-1}} \, p(x_j | x_{j-1})\, M_{j-1}(x_{j-1})\). Store the **argmax** \(x_{j-1}\) for each \((j, x_j)\) (backpointer).
  4. **Best final state:** \(\arg\max_{x_d} M_d(x_d)\).
  5. **Backtrack:** from the best \(x_d\), follow backpointers to get \(x_{d-1}, x_{d-2}, \ldots, x_1\).
- Cost \(O(dk^2)\) instead of enumerating all \(k^d\) sequences.

### Computing conditional probabilities
- **Conditioning on the past** (e.g. \(p(x_{10} | x_3)\)): Fix \(x_3\). Then run the **CK equations starting from time 3**: \(p(x_4|x_3)\) is the transition; \(p(x_5|x_3) = \sum_{x_4} p(x_5|x_4)p(x_4|x_3)\); repeat to get \(p(x_{10}|x_3)\). Same idea as marginals, but “start” at the conditioning time.
- **Conditioning on the future** (e.g. \(p(x_3 | x_7)\)): Reduce to \(p(x_3, x_7)\) and normalize. Compute \(p(x_7, x_3)\) with a **forward** recursion: base \(p(x_{j+1}, x_j) = p(x_{j+1}|x_j)p(x_j)\) (with \(p(x_j)\) from CK); then \(p(x_k, x_j) = \sum_{x_{k-1}} p(x_k|x_{k-1})\, p(x_{k-1}, x_j)\). So “forward messages” from \(j\) toward \(k\).
- **Not the forward–backward extension:** You only need the forward pass for \(p(x_j | x_k)\) with \(k > j\); the full forward–backward algorithm (with backward messages too) is for computing *all* conditionals \(p(x_j | \text{all data})\) at once—out of scope for this quiz.

---

## 5. MCMC

### High-level idea
- We want **Monte Carlo** estimates for \(\mathbb{E}[g(X)]\) under \(p\), but we **can’t sample i.i.d. from \(p\)**.
- **MCMC:** Build a **Markov chain** whose **stationary distribution is \(p\)**. Run the chain for a long time; later samples are (approximately) from \(p\). Use those samples in the Monte Carlo estimator. So: design chain → run it → use samples.

### Burn-in and thinning
- **Burn-in:** Discard the first many samples when the chain is far from stationarity. Reduces bias.
- **Thinning:** Keep only every \(k\)-th sample to reduce correlation between samples used in the estimate. Trade-off: fewer samples vs. less dependence.

### Detailed balance condition
- **Detailed balance (reversibility):** \(\pi(s)\, q(s \to s') = \pi(s')\, q(s' \to s)\) for the chain’s transition \(q\) and distribution \(\pi\). If this holds, then \(\pi\) is the **stationary distribution**. MCMC algorithms (Metropolis, Metropolis–Hastings, Gibbs) are designed so that \(p\) satisfies detailed balance with the chain’s transition.

### Metropolis algorithm
- **Setup:** You can evaluate \(p\) only up to a constant (unnormalized \(\tilde{p}\)).
- **Steps:** Start at \(x^{(0)}\). Repeat: (1) Propose \(\hat{x}\) by adding zero-mean Gaussian noise to current \(x\). (2) Draw \(u \sim \text{Uniform}(0,1)\). (3) If \(u \le \tilde{p}(\hat{x}) / \tilde{p}(x)\), **accept**: set next state to \(\hat{x}\); else **reject**: keep \(x\). Proposals that increase density are always accepted; ones that decrease it are accepted with probability equal to the density ratio.
- **When it works:** For continuous \(p\) with positive density, the chain has \(p\) as stationary distribution and converges. “Working” means: after enough steps, the distribution of the current state is close to \(p\), so Monte Carlo estimates are valid (possibly after burn-in and thinning).

### Metropolis–Hastings
- **General proposal** \(q(\hat{x} | x)\) (not necessarily symmetric). **Accept** with probability \(\min\bigl(1,\, \frac{\tilde{p}(\hat{x})}{\tilde{p}(x)} \cdot \frac{q(x | \hat{x})}{q(\hat{x} | x)}\bigr)\). The extra ratio corrects for asymmetric \(q\) so that detailed balance holds with \(p\). Metropolis is the case where \(q\) is symmetric (e.g. Gaussian centered at current state).
- **Algorithm:** Propose from \(q\), accept/reject with the above probability; if reject, keep current state. Under weak conditions (e.g. \(q\) positive where \(p\) is positive), the chain has \(p\) as stationary distribution.

### Gibbs sampling
- **Algorithm:** Start at some \(x\). Repeat: pick a variable index \(j\); resample \(x_j\) from the **conditional** \(p(x_j \mid x_1,\ldots,x_{j-1}, x_{j+1},\ldots,x_d)\) (all other variables fixed). Other coordinates stay the same. Often variables are updated in a fixed order (e.g. 1, 2, …, d, 1, 2, …).
- **Special case of Metropolis–Hastings:** The “proposal” is the conditional; the acceptance probability is 1, so every Gibbs move is accepted. So Gibbs is M–H with a particular \(q\) that always accepts.

---

*Sources: Quiz 5 materials (16-markov-chains.pdf, 17-msg-passing.pdf, 18-mcmc.pdf) and CPSC440 outline. Use this as your main study doc; refer back to the slides for examples (rain, CS grad, getting to class, PageRank, etc.).*
