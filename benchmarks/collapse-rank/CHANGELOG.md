# CHANGELOG — §8 Constraint-Rank Collapse Detection

## Code implementation — v3.4 (code-hardening, migration candidate)

**Migrates against §8 source:** `section8-constraint-rank.md` v3.3
SHA-256 `dd9cbbb07a72a607047fa4bd4920b00ea5550c2c2791fbb2e59b244255107859`.

**Files / SHA-256 (audit):**
- `collapse_rank.py` — `eec2e16a13bc57b1484fef39d6fc8118738cb6577df7cb7347f1cdc2d2301d91`
- `test_collapse_rank.py` — `fb1d5c348fcf1f8fabb88d98ee9d8ffc37582d51516a967f47cb76212a53b207`

**Environment:** Python 3.10.12, NumPy 2.2.6 · **Tests:** 23/23 pass (`python -m pytest -q`).
**Rank tolerances:** `ATOL=1e-10`, `RTOL=1e-8` (canonical `numerical_rank`), `PSD_TOL=1e-8`.

**v3.4 hardening (closes the six review points):**
1. Zero-weight onset bug fixed — `onsets()` no longer drops `w_q = 0`; consistent with
   `r_max` using $C_0$. (`theta_2 = 0` for $\{c_{iv}@0.9, c_{fu}@0\}$.)
2. SDCI stability test uses a PSD-preserving perturbation $L_2 = L_1 + B^\top B$;
   `sdci_M` now **rejects** non-PSD input instead of silently clipping.
3. Single canonical `numerical_rank(atol, rtol)` used by CDI, kernel bases, Laplacian
   ranks, and the factor-sheaf — no mixed rank rules.
4. CI-safe runner: nonzero exit on failure; the `pytest` shim is registered only via
   `sys.modules` when the real package is absent (never shadows it). Real CI uses
   `python -m pytest -q`.
5. Input validation: $w_q \in [0,1]$ finite; no zero rows; consistent dimensions; PD /
   well-conditioned $\Sigma, M$; $h>0$, $\tau>0$; gated $\psi_h(w)>0$ for active.
6. Provenance: this entry ties the code (with hashes + env) to §8 v3.3.

Status: **migration candidate** — promote to `canonical implementation` after CI runs
real `pytest` in the target environment.

---

## v3.3 — CANONICAL (frozen) — CURRENT

**Frozen file:** `section8-constraint-rank.md`
**SHA-256:** `dd9cbbb07a72a607047fa4bd4920b00ea5550c2c2791fbb2e59b244255107859`
**Size:** 27228 bytes
**Frozen (UTC):** 2026-06-21T22:51:00Z

> Verify before trusting any copy:
> `sha256sum section8-constraint-rank.md` must equal the hash above. A mismatch means
> you are looking at a rendered/cached or edited copy, not the canonical source.

### v3.3 corrections (13–16) — closed

13. **Block cochain grading.** $C^1_\theta = \bigoplus_{q\in E_\theta}\mathbb{R}^{r_q} \cong \mathbb{R}^{m_\theta}$ with $(\delta_\theta x)_q = A_q x$, so
    $H^1_{\mathrm{con}} = \operatorname{coker} C_\theta$ is consistent for multi-row
    blocks (§8.2, §8.4).
14. **Row-space agreement everywhere.** Removed the residual "support equality"
    phrasing in §8.2 and the architectural statement; replaced by: gating with
    identical support (and $\psi_h(w) > 0$ for $w \ge \theta$) is a *sufficient*
    operational rule, exact hard/soft agreement requires *row-space* equality.
15. **Theorem 8.4 in the $M$-geometry.** Bound restated as $\lvert \operatorname{SDCI}^{M}_\tau(L) - \operatorname{SDCI}^{M}_\tau(\widetilde L)\rvert \le \tfrac{4}{\tau}\lVert M^{-1/2}(L-\widetilde L)M^{-1/2}\rVert_2$ (Weyl on the whitened
    operators; verified numerically).
16. **Factor-sheaf local block.** Introduced $P_{I_q}:\mathbb{R}^4\to\mathbb{R}^{I_q}$,
    $\bar A_q \in \mathbb{R}^{r_q\times|I_q|}$, $A_q = \bar A_q P_{I_q}$; stalk
    $\mathcal{F}(q) = \ker \bar A_q$; proof uses $\bar A_q(x|_{I_q}) = 0 \iff A_q x = 0$ (§8.9). Follow-up: Theorem 8.3 statement now ranges $k = 1,\dots,r_{\max}$.

---

## v3.2 — superseded by v3.3

**SHA-256:** `679f0012328dcfb1e10d827875a1f589bbc76fff5be321d2357d0ff931e59d80`
**Size:** 25683 bytes · **Frozen (UTC):** 2026-06-21T21:57:37Z
(Retained for provenance; v3.3 is the canonical source.)

### Patches 1–12 (closed)

1. Non-collapse defined as "no active independent unlicensed constraint of **any
   arity**" — strictly stronger than "pairwise graph has no edge" ($\beta_0 = 4$).
2. Rank-onset filtration $\theta_k$ replaces pseudo-$H_0$-persistence; persistence-
   module/interleaving claims withdrawn to outlook.
3. Mandatory normalization of constraint rows under a score metric.
4. Provable cellular factor-sheaf realization (Thm 8.6), $\Gamma \cong \ker C_\theta$.
5. Corrected $H^1$ semantics: redundancy ($\ker C_\theta^\top$) vs genuine sheaf
   gluing obstructions; conflict detection deferred to the affine extension.
6. Hard/soft architecture: discrete diagnosis ($C_\theta$) vs continuous monitoring
   ($L^{\mathrm{soft}}_{\theta,h}$).
7. Support warning: a logistic gate is positive everywhere and does **not** preserve
   the hard kernel; gated vs all-evidence operators introduced.
8. Scope of Theorem 8.3: stability for **fixed normalized templates** under weight
   perturbation only (Rmk 8.5b).
9. Lemma 8.0 condition corrected to **row-space equality**
   $\operatorname{row} C_{\operatorname{supp}(a^{\mathrm{soft}})} = \operatorname{row} C_\theta^{\mathrm{hard}}$ (support equality sufficient, not necessary).
10. Two soft energies separated: $\mathcal{E}^{\mathrm{gated}}$ (zero-set
    $\ker C_\theta$) vs $\mathcal{E}^{\mathrm{all}}$ (zero-set $\bigcap_q \ker A_q$).
11. Score geometry $M = \Sigma^{-1}$ (Mahalanobis); whitened
    $\widehat L = M^{-1/2} L M^{-1/2}$, $\operatorname{SDCI}^{M}$, and dimensionless
    instance energy $\overline{\mathcal{E}} = x^\top L x / x^\top M x$.
12. $\theta_k$ quantified over reachable ranks $k \le r_{\max} = \operatorname{rank} C_0$; Prop 8.5 stated against the **designated** pairwise-proxy graph (no
    implicit hyperedge-to-clique projection).

### Canonical operators (migration target)

| Operator | Role |
|---|---|
| **Hard** $C_\theta = \operatorname{stack}_q A_q$ | CDI, $H^0_{\mathrm{con}}$, $\theta_k$, factor-graph sheaf |
| **Gated-soft** $L^{\mathrm{gated}}_{\theta,h}$ | SDCI as active-set monitoring (preserves hard kernel) |
| **All-evidence-soft** $L^{\mathrm{all}}_{\theta,h}$ | graduated proxy-pressure monitor (distinct kernel) |

### Invariants pinned for the code/test migration

- $\theta_k$ stability holds **only** for fixed normalized constraint templates under
  weight perturbation $\lVert w - \widetilde w\rVert_\infty \le \varepsilon$ (not for
  estimated constraint coefficients $\alpha,\beta$).
- SDCI and energy geometry are **relative to $M = \Sigma^{-1}$**; raw-Euclidean
  spectra are not calibrated.
- Persistence/interleaving statements remain **outlook only** until a filtered
  factor-graph sheaf with explicit structure maps is defined.

### Verified numerically during review

- Single active rule ⟹ $\operatorname{rank} C_\theta = 1$, $\dim H^0_{\mathrm{con}} = 3$ (old $\bar H^1 = 0$ counterexample resolved).
- Ternary proxy, no pairwise edge ⟹ CDI $= 1$ while $\beta_0 = 4$ (Prop 8.5).
- Factor-sheaf $H^0$ dim $= \dim \ker C_\theta = 3$ (Thm 8.6).
- $\theta_k$ $1$-Lipschitz under $\ell_\infty$ weight perturbation (Thm 8.3).
- Ungated logistic kernel dim $2 \neq 3$ hard; gated $= 3$ (Lemma 8.0 / Patch 7).
- Support $\{c_1,c_2\}$ vs $\{c_1,c_2,c_1{+}c_2\}$: identical kernel/rank (Patch 9).
- $M = \Sigma^{-1}$ gives $\lVert c\rVert_{M^{-1}}^2 = c\,\Sigma\,c^\top$ (Patch 11).

## Next step

Code/test migration against the three operators above; tests are diagnostic checks,
not equivalence proofs (see §8.11).
