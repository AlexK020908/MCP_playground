# CPSC 440 — Quiz 5 Study Guide  
**Slides-style outline · No formulas**

---

## 1. Representation learning

- **Non-variational autoencoders**
- **Uses of representation learning**
- **MLE ≠ "most useful representation"**
- Vague sense that it might be useful anyway

---

## 2. Image generative models

- **High-level idea:** learning to denoise with a generative model (diffusion) and how it connects to a VAE
- No formulas
- **General idea:** likelihood vs sample quality in high dimensions

---

## 3. Markov chains

- **Chain rule:** factorizing any distribution into a product of conditional 1D distributions
- **Markov assumption** — what it is and why it makes this tractable
- **Resulting model:** a Markov chain
- **Homogeneous vs inhomogeneous chains**
- **MLE** in this setting
- **Ancestral sampling** from Markov chains
- **Computing marginal probabilities** with the Chapman–Kolmogorov (CK) equations
- **Stationary distribution:** definition and basic idea
- **Message passing** in Markov chains
- **Why the mode of a sequence ≠ mode of each marginal**

---

## 4. Viterbi decoding

- **General idea / setup**
- **The algorithm**
- **Computing conditional probabilities:**
  - Conditioning on the **past** → CK equations
  - Conditioning on the **future** → the **forward** algorithm  
  - (Not the forward–backward extension)

---

## 5. MCMC

- **High-level idea**
- **Burning** and **thinning**
- **Detailed balance** condition
- **Metropolis algorithm**
  - The algorithm
  - When it works
  - What “working” means
- **Metropolis–Hastings**
  - The algorithm
- **Gibbs sampling**
  - The algorithm
  - That it’s a special case of Metropolis–Hastings

---

*Use this as a slide-by-slide checklist. After restarting Cursor, run the custom MCP tool `get_quiz_materials(school_name="ubc", course_name="cpsc440", quiz_id="5")` to pull materials from `E:\academics\ubc\cpsc440\quiz\5` (or quiz5) and cross-reference with these topics.*
