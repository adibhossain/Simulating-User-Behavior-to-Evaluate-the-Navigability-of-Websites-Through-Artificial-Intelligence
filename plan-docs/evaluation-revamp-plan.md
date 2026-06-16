# Evaluation Revamp Plan — Normalized Scoring, Lostness, and HCI Methods

**Paper:** *Simulating User Behavior to Evaluate the Navigability of Websites Through Artificial Intelligence* (Islam, Hossain, Bilwal, Sircar, Khan — MIST).
**Target section:** **IV. SYSTEM EVALUATION → C. RESULT ANALYSIS** (Tables 2–5) and the related numbers in the **Abstract** and **Conclusion**.
**Purpose of this doc:** A detailed, citable plan to (1) replace the ad-hoc 0–5 “similarity rating” with a principled normalized [0,1] score, (2) add a **lostness** navigation metric, and (3) fold in recognized **HCI evaluation methods** — each with recent, citable references.

---

## 0. What the paper does today (so we know exactly what we are replacing)

In Section IV.C the system’s navigation is compared against each human participant on three tables, then averaged:

| Table | What is compared | Raw quantities |
|-------|------------------|----------------|
| **Table 2** | Report values | Verdict (found/not), Total Clicks, Total Backs, Total Buttons Denied |
| **Table 3** | Order of buttons noticed, per page | Sequence of button labels (system vs user) |
| **Table 4** | Navigation graph | Number of nodes (pages), % of common edges |
| **Table 5** | Aggregate | Mean of the per-table ratings → final score |

**The problem (Requirement 1):** every comparison is mapped to a hand-picked integer “similarity rating out of 5” with no formula — e.g. *“difference of 0 → 5, difference of 1 → 4, difference of 2 or 3 → 3, page not visited → 0, one-button order difference → 4.”* These thresholds are arbitrary, not reproducible, and not defensible to a reviewer. The final headline number (**70.65 %**, i.e. 3.5325/5) inherits that arbitrariness.

**Goal:** keep the *quantitative* comparison idea (system vs user on the same observable parameters) but compute every sub-score with a **published normalization formula** producing a value in **[0, 1]**, then aggregate. Drop all qualitative/subjective bucket rules.

---

## 1. Requirement 1 — Replace the 0–5 rating with normalized [0,1] similarity

### 1.1 Principle
Every parameter the paper already collects is one of three data *types*. Each type gets the correct, citable similarity formula. All formulas output **1 = identical behaviour, 0 = maximally different** — so they are directly comparable and averageable. This is the standard **min–max / unit-interval normalization** idea from data mining (Han, Kamber & Pei) [C5], the same family already used to normalize the regression features in the Button Ordering module.

### 1.2 Formulas per data type

**(a) Binary parameter — Verdict (found / not found).**
Simple match indicator (a 2-element Jaccard / exact-match):
```
sim_verdict = 1 if both found (or both not found), else 0
```

**(b) Scalar count parameters — Total Clicks, Total Backs, Total Buttons Denied, Number of Nodes.**
Use a **normalized absolute difference** (a relative/symmetric error mapped to a similarity). For a system value `s` and user value `u`:
```
sim = 1 − |s − u| / (s + u)          (when s + u > 0; if s = u = 0, define sim = 1)
```
This is bounded in [0,1], symmetric, unit-free, and is the min–max-normalized distance between the two readings [C5]. (Alternative form `1 − |s−u|/max(s,u)` is equally citable; pick one and use it consistently.)

**(c) Ordered sequence parameter — order of buttons noticed (Table 3).**
The button-notice order is a *string of labels*. Compare two orders with the **normalized Levenshtein (edit) distance**, which Yujian & Liu proved is a true metric on [0,1] [C7] (base edit distance: Levenshtein [C8]):
```
sim_order = 1 − Lev(seq_system, seq_user) / max(|seq_system|, |seq_user|)
```
*Did-Not-Visit* falls out naturally: if the user’s sequence for a page is empty, the distance equals the system sequence length → `sim_order = 0`, with no special-case rule needed.
*Optional, if you want to argue about rank order rather than edit operations:* report **Kendall’s τ** rank correlation [C9] rescaled to [0,1] as `(τ+1)/2`.

**(d) Graph parameter — navigation graph (Table 4).**
Two sub-scores:
- **Edge overlap → Jaccard index** of the two edge sets [C10] (the standard graph-similarity measure):
  ```
  sim_edges = |E_system ∩ E_user| / |E_system ∪ E_user|
  ```
- **Node count** → scalar formula (b).

### 1.3 Aggregation
Within a table, average the sub-scores; across tables, average to a per-participant navigability similarity; across participants, average to the headline figure — all already in [0,1], so reportable directly as a percentage:
```
Navigability_Similarity = mean over participants ( mean over tables ( mean of sub-scores ) )
```
(If some parameters matter more, use a **weighted** mean and state the weights — but unweighted is the safest default and needs no justification.)

### 1.4 Worked example — recomputing Participant P1 (uses numbers already in the paper)

**Table 2 (P1):** Verdict found/found; Clicks 6 vs 3; Backs 3 vs 0; Denied 5 vs 4.
```
sim_verdict = 1
sim_clicks  = 1 − |6−3|/(6+3) = 1 − 3/9 = 0.667
sim_backs   = 1 − |3−0|/(3+0) = 1 − 1   = 0.000
sim_denied  = 1 − |5−4|/(5+4) = 1 − 1/9 = 0.889
Table-2 score = (1 + 0.667 + 0 + 0.889)/4 = 0.639      (old rating was 3.75/5 = 0.75)
```
**Table 3 (P1), page “Home”:** system `A→F` vs user `A→B→F` → edit distance 1 (insert B), max length 3.
```
sim_order(Home) = 1 − 1/3 = 0.667                       (old rating was 4/5 = 0.80)
```
**Table 4 (P1):** Nodes 9 vs 6; edges: system 62.5 % common, user 100 % common → Jaccard = 0.625.
```
sim_nodes = 1 − |9−6|/(9+6) = 1 − 3/15 = 0.800
sim_edges = 0.625                                        (old rating was 4/5 = 0.80)
```
> These illustrate the method; recompute every cell from the existing raw values. The headline % will shift (expect lower than 70.65 % because the old buckets were generous) — that is *correct* and more defensible.

---

## 2. Requirement 2 — Add a Lostness score

### 2.1 What it is and why it fits
**Lostness** is the standard HCI metric for how disoriented someone gets while navigating a hypertext/website — exactly the construct this paper is about. It was defined by **Smith (1996)** [C1] and is widely used in web-navigation studies (Gwizdka & Spence) [C2] and UX practice (Tullis & Albert; Sauro & Lewis) [C3][C4]. It turns a navigation path into a single number in **[0, 1]** where **0 = perfectly efficient (not lost)**.

### 2.2 Formula (Smith 1996) [C1]
```
L = sqrt( (N/S − 1)² + (R/N − 1)² )
```
- **R** = minimum number of pages that *must* be visited to complete the task (the optimal path length).
- **S** = total number of pages visited while doing the task, **counting revisits**.
- **N** = number of *distinct* pages visited.

**Interpretation thresholds** (Smith [C1], echoed by Tullis & Albert [C3]):
- `L < 0.4` → user/agent was **not** observably lost.
- `0.4 ≤ L ≤ 0.5` → indeterminate.
- `L > 0.5` → **lost**.

### 2.3 How to compute it here (you already log everything needed)
This system records clicks, backs, and the navigation graph — enough to derive R, S, N for **both** the agent and each participant:
- **R** = shortest path (in pages) from the start page to the target (“Tuna”) page on the demo site = the optimal route length. Compute once per task from the site graph.
- **N** = number of distinct nodes in that run’s navigation graph (already in Table 4).
- **S** = total page visits including repeats ≈ forward clicks that load a new page **+ back navigations + 1 (start page)**. Derive from the click/back log per run.

### 2.4 How to use it in the paper
1. Add a column/table reporting **L_system** and **L_user** per participant, plus the threshold verdict (lost / not lost).
2. Two analytical angles, both valuable:
   - **Navigability of the website:** low L for human users ⇒ the site is navigable; high L ⇒ poor information architecture. This is the metric’s classic use.
   - **Human-likeness of the agent:** compare L_system vs L_user. If the agent’s lostness tracks the users’ lostness, it strengthens the central claim that the agent behaves like a human. You can even fold `1 − |L_sys − L_user|` into the §1 similarity aggregate.

---

## 3. Requirement 3 — HCI evaluation methods to include (with citations)

The paper already *says* it evaluates “effectiveness, efficiency, and user satisfaction” — that wording is literally the **ISO 9241-11** definition of usability [C11][C12]. Right now it is named but not operationalized. Recommendation: anchor the evaluation explicitly in ISO 9241-11 and slot each metric under the matching dimension. Below: what to add, why, and the citation.

| HCI dimension (ISO 9241-11) [C11] | Concrete metric to report | Already have it? | Citation |
|---|---|---|---|
| **Effectiveness** | **Task success / completion rate** (did the agent/user reach “Tuna”?) — formalize the current “Verdict”. | Yes (Verdict) | ISO 9241-11 [C11][C12] |
| **Efficiency** | **Lostness** `L` (Req. 2); plus clicks/backs as navigation effort. | Yes (clicks, backs) | Smith [C1]; Gwizdka & Spence [C2] |
| **Efficiency** | **Navigation-path / order similarity** via normalized Levenshtein or Kendall’s τ. | Yes (Table 3) | Yujian & Liu [C7]; Kendall [C9] |
| **Effectiveness** | **Graph/structure similarity** via Jaccard edge overlap. | Yes (Table 4) | Jaccard [C10] |
| **Satisfaction** | **System Usability Scale (SUS)** — a short post-task questionnaire for the human participants. | No — small new step | Brooke [C13]; Lewis (recent review) [C14] |
| **Satisfaction / load** (optional) | **NASA-TLX** to capture perceived effort/cognitive load during the search task. | No — optional | Hart & Staveland [C15] |

**Recommendation (scope-aware):**
- **Definitely add:** ISO 9241-11 framing [C11] + Lostness [C1] + the normalized similarity metrics [C5][C7][C10]. These need *no* new data — they recompute from logs you already have.
- **Add if you can re-run the user study:** **SUS** [C13][C14] (5-minute questionnaire) to give a real, citable **satisfaction** number instead of only effectiveness/efficiency. This directly fixes the current gap where “satisfaction” is claimed but never measured.
- **Optional:** NASA-TLX [C15] if you want a cognitive-load angle.
- You may also *name* the broader method family (heuristic evaluation, cognitive walkthrough) in Related Work for completeness, but they are not needed for the quantitative results.

---

## 4. Execution plan (step by step)

1. **Lock the formulas.** Adopt §1.2 (a–d) for similarity, §2.2 for lostness. Add a short “Evaluation Metrics” subsection at the start of Section IV defining each formula with its citation.
2. **Recover R, S, N.** From the demo-site graph compute R (optimal path to “Tuna”). From each run’s click/back log compute S and N (N already in Table 4).
3. **Recompute Tables 2–4** cell-by-cell with the new [0,1] formulas (see worked P1 example in §1.4). Replace the “Similarity Rating (out of 5)” column with “Similarity (0–1)”.
4. **Recompute Table 5** as the mean-of-means in [0,1]; report the new headline as a percentage.
5. **Add the Lostness table** (L_system, L_user, verdict) and 2–3 sentences interpreting it per §2.4.
6. **(If re-running study) add SUS**: administer the 10-item SUS after each participant’s task; report the 0–100 SUS score as the satisfaction measure.
7. **Update prose:** rewrite §IV.C to describe formula-based scoring (delete the bucket rules). Update the **Abstract** (“70.65 %”) and **Conclusion** to the recomputed figure.
8. **Add references** [C1]–[C15] to the bibliography (IEEE numbered style, matching the existing list).

---

## 5. Citation list (ready to drop into the bibliography)

**Normalization / similarity metrics**
- **[C5]** J. Han, M. Kamber, and J. Pei, *Data Mining: Concepts and Techniques*, 3rd ed. Morgan Kaufmann, 2011. — min–max / unit-interval normalization.
- **[C7]** L. Yujian and L. Bo, “A normalized Levenshtein distance metric,” *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. 29, no. 6, pp. 1091–1095, 2007. — normalized edit distance as a metric.
- **[C8]** V. I. Levenshtein, “Binary codes capable of correcting deletions, insertions, and reversals,” *Soviet Physics Doklady*, vol. 10, no. 8, pp. 707–710, 1966. — base edit distance.
- **[C9]** M. G. Kendall, “A new measure of rank correlation,” *Biometrika*, vol. 30, no. 1/2, pp. 81–93, 1938. — rank-order similarity (optional for Table 3).
- **[C10]** P. Jaccard, “The distribution of the flora in the alpine zone,” *New Phytologist*, vol. 11, no. 2, pp. 37–50, 1912. — Jaccard index for edge-set overlap.

**Lostness / navigation**
- **[C1]** P. A. Smith, “Towards a practical measure of hypertext usability,” *Interacting with Computers*, vol. 8, no. 4, pp. 365–381, 1996. — original lostness `L` formula and thresholds.
- **[C2]** J. Gwizdka and I. Spence, “Implicit measures of lostness and success in web navigation,” *Interacting with Computers*, vol. 19, no. 3, pp. 357–369, 2007. — lostness applied to web navigation.
- **[C3]** T. Tullis and B. Albert, *Measuring the User Experience: Collecting, Analyzing, and Presenting Usability Metrics*, 2nd ed. Morgan Kaufmann, 2013. — lostness in practice + thresholds. **(recent-ish, widely cited)**
- **[C4]** J. Sauro and J. R. Lewis, *Quantifying the User Experience: Practical Statistics for User Research*, 2nd ed. Morgan Kaufmann, 2016. — normalization & aggregation of UX metrics. **(recent)**

**HCI evaluation framework / satisfaction**
- **[C11]** ISO 9241-11:2018, *Ergonomics of human–system interaction — Part 11: Usability: Definitions and concepts*. — effectiveness/efficiency/satisfaction. **(current standard)**
- **[C12]** N. Bevan, J. Carter, and S. Harker, “ISO 9241-11 revised: What have we learnt about usability since 1998?,” in *HCI International 2015*, Springer, pp. 143–151. **(recent)**
- **[C13]** J. Brooke, “SUS: A quick and dirty usability scale,” in *Usability Evaluation in Industry*, Taylor & Francis, 1996, pp. 189–194. — SUS questionnaire.
- **[C14]** J. R. Lewis, “The System Usability Scale: Past, present, and future,” *Int. J. Human–Computer Interaction*, vol. 34, no. 7, pp. 577–590, 2018. **(recent SUS review)**
- **[C15]** S. G. Hart and L. E. Staveland, “Development of NASA-TLX: Results of empirical and theoretical research,” *Advances in Psychology*, vol. 52, pp. 139–183, 1988. — cognitive-load (optional).

> Practitioner/secondary references that corroborate the lostness thresholds and 0–1 interpretation (not for the bibliography, just for your own checking): MeasuringU “Validating a Lostness Measure”; UXtweak and Loop11 lostness guides.

---

## 6. Notes, risks, and honest caveats

- **The headline number will likely drop** below 70.65 %. The old buckets were lenient (e.g. a clicks difference of 3 still scored 3/5 = 0.6; the new formula gives 0.667 for 6-vs-3 but 0 for 3-vs-0 backs). A lower-but-defensible number is better for review than a high arbitrary one. Frame it as a methodological improvement.
- **Edge case `s = u = 0`** in formula (b): define similarity = 1 (perfect agreement that the count is zero). State this explicitly.
- **Lostness needs S (with revisits)** — make sure the run logs distinguish “new page load” vs “back”. The code already counts `total_clicks` and `total_backs`; confirm these let you reconstruct S precisely, otherwise add a per-step page-visit log.
- **R (optimal path)** must be computed per task/site; for the “Tuna” task on the demo site it is the shortest start→target page distance.
- **Small N (4 participants)** is already a stated limitation; the new metrics don’t fix sample size, but they make each data point rigorous. Consider noting that the normalized metrics make future larger studies directly comparable.
- **Weights:** if you weight tables/parameters, justify the weights or keep them equal. Equal weighting is the default and needs no defense.

---

### TL;DR
1. **Req 1:** swap the 0–5 buckets for unit-interval similarity — normalized abs-difference for counts [C5], normalized Levenshtein for button order [C7][C8], Jaccard for graph edges [C10] — then average. Worked P1 example included.
2. **Req 2:** add **Smith’s lostness** `L = √((N/S−1)² + (R/N−1)²)` [C1][C2][C3] for both agent and users; thresholds 0.4/0.5.
3. **Req 3:** frame the whole evaluation under **ISO 9241-11** [C11][C12]; effectiveness = task success, efficiency = lostness + path similarity, satisfaction = **SUS** [C13][C14] (add if re-running study), optional **NASA-TLX** [C15].
