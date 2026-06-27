"""
collapse_rank.py — Constraint-rank dimension-collapse detection (KGA §8).

Canonical source: section8-constraint-rank.md, v3.3 (frozen),
SHA-256: dd9cbbb07a72a607047fa4bd4920b00ea5550c2c2791fbb2e59b244255107859
Implementation status: v3.4 (code-hardening; see CHANGELOG.md).

Three canonical operators:
    HARD              C_theta            -> CDI, H0_con, theta_k, factor-sheaf
    GATED-SOFT        L^gated_{theta,h}  -> SDCI as active-set monitoring
    ALL-EVIDENCE-SOFT L^all_{theta,h}    -> graduated proxy-pressure monitor

Conventions:
  * Block constraints A_q in R^{r_q x d} (atomic covector = single row).
  * Score metric M = Sigma^{-1} (Mahalanobis); dual norm ||c||_{M^-1}^2 = c M^-1 c^T = c Sigma c^T.
  * Rows M-normalized: ||c_q||_{M^-1} = 1.
  * SDCI / energy in the M-geometry via whitened Lhat = M^{-1/2} L M^{-1/2}.

A single documented numerical-rank rule (`numerical_rank`, ATOL/RTOL) is used for
CDI, H0_con, kernel bases, Laplacian ranks and the factor-sheaf, so all rank
decisions are consistent. These are diagnostic checks, not equivalence proofs (§8.11).
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

# ---- canonical numerical tolerances (record alongside numpy version in audit metadata)
ATOL = 1e-10
RTOL = 1e-8
PSD_TOL = 1e-8        # eigenvalues below -PSD_TOL are treated as a PSD violation
COND_MAX = 1e12       # reject ill-conditioned metrics
_ZERO = 1e-12


def numerical_rank(A: np.ndarray, *, atol: float = ATOL, rtol: float = RTOL) -> int:
    """Canonical SVD-based rank with a documented threshold `atol + rtol*sigma_max`.

    Used identically by every rank/kernel decision in this module.
    """
    A = np.asarray(A, dtype=float)
    if A.size == 0 or min(A.shape) == 0:
        return 0
    s = np.linalg.svd(A, compute_uv=False)
    if s.size == 0:
        return 0
    threshold = atol + rtol * s[0]
    return int(np.sum(s > threshold))


# --------------------------------------------------------------------------------------
# Constraints (with input validation, Patch 5/v3.4)
# --------------------------------------------------------------------------------------
@dataclass
class Constraint:
    """Deontic proxy constraint q: block A_q in R^{r_q x d}, evidence weight w_q in [0,1]."""
    A: np.ndarray
    w: float
    name: str = ""

    def __post_init__(self):
        self.A = np.atleast_2d(np.asarray(self.A, dtype=float))
        if not np.all(np.isfinite(self.A)):
            raise ValueError(f"constraint {self.name!r}: A must be finite")
        if np.any(np.all(np.abs(self.A) <= _ZERO, axis=1)):
            raise ValueError(f"constraint {self.name!r}: A contains an all-zero row")
        if not np.isfinite(self.w):
            raise ValueError(f"constraint {self.name!r}: w must be finite")
        if not (0.0 <= float(self.w) <= 1.0):
            raise ValueError(f"constraint {self.name!r}: w={self.w} not in [0,1]")
        self.w = float(self.w)

    @property
    def r(self) -> int:
        return self.A.shape[0]

    @property
    def d(self) -> int:
        return self.A.shape[1]

    @property
    def support(self) -> tuple[int, ...]:
        return tuple(int(j) for j in np.flatnonzero(np.any(np.abs(self.A) > _ZERO, axis=0)))


def _check_list(constraints: list[Constraint], d: int) -> None:
    for q in constraints:
        if q.d != d:
            raise ValueError(f"constraint {q.name!r}: dimension {q.d} != expected {d}")


# --------------------------------------------------------------------------------------
# Metric (M = Sigma^{-1}) helpers
# --------------------------------------------------------------------------------------
def metric_from_covariance(Sigma: np.ndarray) -> np.ndarray:
    """Primal score metric M = Sigma^{-1} for empirical covariance Sigma (Patch 11)."""
    Sigma = np.asarray(Sigma, dtype=float)
    if not np.all(np.isfinite(Sigma)):
        raise ValueError("Sigma must be finite")
    ev = np.linalg.eigvalsh((Sigma + Sigma.T) / 2.0)
    if ev[0] <= 0:
        raise ValueError("Sigma must be positive definite")
    if ev[-1] / ev[0] > COND_MAX:
        raise ValueError(f"Sigma ill-conditioned (cond={ev[-1]/ev[0]:.2e} > {COND_MAX:.0e})")
    return np.linalg.inv(Sigma)


def _check_metric(M: np.ndarray) -> np.ndarray:
    M = np.asarray(M, dtype=float)
    ev = np.linalg.eigvalsh((M + M.T) / 2.0)
    if ev[0] <= 0:
        raise ValueError("metric M must be positive definite")
    if ev[-1] / ev[0] > COND_MAX:
        raise ValueError("metric M ill-conditioned")
    return M


def _sym_pow(M: np.ndarray, p: float) -> np.ndarray:
    w, U = np.linalg.eigh((M + M.T) / 2.0)
    return (U * (w ** p)) @ U.T


def dual_norm(c: np.ndarray, M: np.ndarray) -> float:
    """||c||_{M^-1} = sqrt(c M^{-1} c^T)."""
    c = np.ravel(np.asarray(c, dtype=float))
    return float(np.sqrt(c @ np.linalg.solve(M, c)))


def normalize_constraints(constraints: list[Constraint], M: np.ndarray) -> list[Constraint]:
    """Return copies with every row M-normalized: ||c_q||_{M^-1} = 1 (Patches 3, 11)."""
    _check_metric(M)
    out = []
    for q in constraints:
        rows = []
        for row in q.A:
            n = dual_norm(row, M)
            if n <= _ZERO:
                raise ValueError(f"constraint {q.name!r}: row has zero dual norm; cannot normalize")
            rows.append(row / n)
        out.append(Constraint(np.vstack(rows), q.w, q.name))
    return out


# --------------------------------------------------------------------------------------
# HARD operator: C_theta, CDI, H0, theta_k  (Thms 8.1, 8.3; Patches 12, 13)
# --------------------------------------------------------------------------------------
def active(constraints: list[Constraint], theta: float) -> list[Constraint]:
    return [q for q in constraints if q.w >= theta]


def hard_operator(constraints: list[Constraint], theta: float, d: int = 4) -> np.ndarray:
    """C_theta = stack_{q in E_theta} A_q  in  R^{m_theta x d}  (m_theta = sum r_q)."""
    _check_list(constraints, d)
    blocks = [q.A for q in active(constraints, theta)]
    return np.vstack(blocks) if blocks else np.zeros((0, d))


def cdi(C: np.ndarray) -> int:
    """Collapse-Dimension Index = rank C_theta (Thm 8.1), canonical numerical rank."""
    return numerical_rank(C)


def h0_con_dim(C: np.ndarray, d: int = 4) -> int:
    """dim H0_con = d - rank C_theta (Thm 8.1)."""
    return d - cdi(C)


def redundancy_dim(C: np.ndarray) -> int:
    """dim H1_con = m_theta - rank C_theta (Rmk 8.2)."""
    return C.shape[0] - cdi(C)


def r_max(constraints: list[Constraint], d: int = 4) -> int:
    """Maximal reachable rank r_max = rank C_0 (Patch 12); includes w_q = 0 blocks."""
    return cdi(hard_operator(constraints, 0.0, d))


def onsets(constraints: list[Constraint], d: int = 4) -> dict[int, float]:
    """theta_k = sup{theta in [0,1] : rank C_theta >= k}, k = 1..r_max (Patch 12).

    rank changes only at distinct weight values; zero weights ARE candidates because
    E_theta = {q : w_q >= theta} includes them at theta = 0 (v3.4 zero-weight fix).
    """
    _check_list(constraints, d)
    rmax = r_max(constraints, d)
    weights = sorted({q.w for q in constraints}, reverse=True)  # v3.4: keep w == 0
    out: dict[int, float] = {}
    for k in range(1, rmax + 1):
        theta_k = None
        for v in weights:  # descending; first v whose active-set rank >= k is the sup
            if cdi(hard_operator(constraints, v, d)) >= k:
                theta_k = v
                break
        out[k] = theta_k
    return out


# --------------------------------------------------------------------------------------
# SOFT operators: gated & all-evidence Laplacians  (Lemma 8.0; Patches 6, 7, 14)
# --------------------------------------------------------------------------------------
def _laplacian(blocks_weights: list[tuple[np.ndarray, float]], d: int) -> np.ndarray:
    L = np.zeros((d, d))
    for A, a in blocks_weights:
        if a > 0:
            L += a * (A.T @ A)
    return L


def gated_soft_laplacian(constraints, theta, d=4, psi=None) -> np.ndarray:
    """L^gated = sum_{w_q >= theta} psi_h(w_q) A_q^T A_q.

    psi must be > 0 for active w >= theta (Patch 14) so supp = E_theta^hard.
    """
    _check_list(constraints, d)
    if psi is None:
        psi = lambda w: 1.0  # noqa: E731
    bw = []
    for q in constraints:
        if q.w >= theta:
            p = float(psi(q.w))
            if p <= 0:
                raise ValueError(f"gated psi(w={q.w}) = {p} <= 0 for an active constraint")
            bw.append((q.A, p))
        else:
            bw.append((q.A, 0.0))
    return _laplacian(bw, d)


def all_evidence_laplacian(constraints, theta, d=4, h=0.1) -> np.ndarray:
    """L^all = sum_q logistic_{theta,h}(w_q) A_q^T A_q (positive on ALL q; distinct kernel)."""
    _check_list(constraints, d)
    if h <= 0:
        raise ValueError("bandwidth h must be > 0")
    logit = lambda w: 1.0 / (1.0 + np.exp(-(w - theta) / h))  # noqa: E731
    return _laplacian([(q.A, logit(q.w)) for q in constraints], d)


def laplacian_kernel_dim(L: np.ndarray, d: int = 4) -> int:
    return d - numerical_rank(L)


# --------------------------------------------------------------------------------------
# SDCI in the M-geometry  (Thm 8.4; Patch 15)
# --------------------------------------------------------------------------------------
def whiten(L: np.ndarray, M: np.ndarray) -> np.ndarray:
    """Lhat = M^{-1/2} L M^{-1/2}."""
    Mm12 = _sym_pow(_check_metric(M), -0.5)
    return Mm12 @ L @ Mm12


def sdci_M(L: np.ndarray, M: np.ndarray, tau: float, *, psd_tol: float = PSD_TOL) -> float:
    """SDCI^M_tau = tr[ Lhat (Lhat + tau I)^{-1} ] = sum_j lam_j/(lam_j+tau), in [0, d].

    Theorem 8.4 requires L >= 0; a substantially negative eigenvalue is rejected
    rather than silently clipped (v3.4 hardening).
    """
    if tau <= 0:
        raise ValueError("tau must be > 0")
    Lh = whiten(L, M)
    lam = np.linalg.eigvalsh((Lh + Lh.T) / 2.0)
    if np.min(lam) < -psd_tol:
        raise ValueError(f"L must be PSD; min eigenvalue {np.min(lam):.3e} < -{psd_tol:.0e}")
    lam = np.maximum(lam, 0.0)
    return float(np.sum(lam / (lam + tau)))


# --------------------------------------------------------------------------------------
# Energies  (Rmk 8.3, 8.4; Patch 10)
# --------------------------------------------------------------------------------------
def energy(x: np.ndarray, L: np.ndarray) -> float:
    """Raw collapse-realisation energy x^T L x (>= 0). Use L^gated or L^all."""
    x = np.ravel(np.asarray(x, dtype=float))
    return float(x @ L @ x)


def energy_dimensionless(x: np.ndarray, L: np.ndarray, M: np.ndarray) -> float:
    """Ebar = x^T L x / x^T M x (scale-free; Patch 11)."""
    x = np.ravel(np.asarray(x, dtype=float))
    denom = x @ M @ x
    if denom <= _ZERO:
        raise ValueError("x must be nonzero in the M-geometry")
    return float((x @ L @ x) / denom)


# --------------------------------------------------------------------------------------
# Factor-graph cellular sheaf realization  (Thm 8.6; Patch 16)
# --------------------------------------------------------------------------------------
def _kernel_basis(A: np.ndarray) -> np.ndarray:
    """Columns span ker A (A is r x n -> returns n x k), using the canonical rank rule."""
    A = np.asarray(A, dtype=float)
    n = A.shape[1]
    if A.size == 0 or A.shape[0] == 0:
        return np.eye(n)
    u, s, vt = np.linalg.svd(A)
    rank = numerical_rank(A)
    return vt[rank:].T  # n x k


def factor_sheaf_h0_dim(constraints, theta, d=4) -> int:
    """dim H^0(G_theta; F_theta) = dim ker delta^0 (should equal d - rank C_theta).

    F(d)=R, F(q)=ker Abar_q (Abar_q = A_q|_{I_q}), F(q,d)=R,
    rho_{d->(q,d)}=id, rho_{q->(q,d)} = pi_d|_{ker Abar_q}  (Patch 16).
    """
    _check_list(constraints, d)
    acts = active(constraints, theta)
    bases, supports = [], []
    for q in acts:
        I = q.support
        Abar = q.A[:, list(I)]            # r_q x |I_q| (projected block)
        bases.append(_kernel_basis(Abar))
        supports.append(I)
    param_dims = [B.shape[1] for B in bases]
    n_c0 = d + sum(param_dims)
    rows = []
    for qi, (I, B) in enumerate(zip(supports, bases)):
        off = d + sum(param_dims[:qi])
        for a, dim_idx in enumerate(I):
            row = np.zeros(n_c0)
            row[dim_idx] += 1.0
            row[off:off + B.shape[1]] -= B[a, :]
            rows.append(row)
    delta0 = np.vstack(rows) if rows else np.zeros((0, n_c0))
    return n_c0 - numerical_rank(delta0)


# --------------------------------------------------------------------------------------
# Designated pairwise-proxy graph (Prop 8.5; Patch 12)
# --------------------------------------------------------------------------------------
def pairwise_beta0(constraints, theta, d=4) -> int:
    """beta_0 of the DESIGNATED pairwise-proxy graph (only |support|==2 constraints
    contribute edges; higher-arity factors are NOT projected to cliques)."""
    _check_list(constraints, d)
    parent = list(range(d))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for q in active(constraints, theta):
        I = q.support
        if len(I) == 2:
            parent[find(I[0])] = find(I[1])
    return len({find(i) for i in range(d)})
