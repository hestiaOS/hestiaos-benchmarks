"""
Diagnostic test-suite for collapse_rank.py — KGA §8 canonical v3.3.

Each test maps to a theorem/proposition/lemma of the frozen §8 source.
These are diagnostic checks, NOT equivalence proofs (cf. §8.11).
"""
import numpy as np
import pytest

import collapse_rank as cr
from collapse_rank import Constraint as C

D = 4
# dimension order: (i, v, f, u) = (0, 1, 2, 3)
c_iv = np.array([1.0, -1.0, 0.0, 0.0])
c_fu = np.array([0.0, 0.0, 1.0, -1.0])
c_ivf = np.array([-0.5, -0.5, 1.0, 0.0])  # x_f - 0.5 x_i - 0.5 x_v

SIGMA = np.array([[2.0, 0.3, 0.0, 0.0],
                  [0.3, 1.0, 0.0, 0.0],
                  [0.0, 0.0, 1.5, 0.2],
                  [0.0, 0.0, 0.2, 1.0]])
M = cr.metric_from_covariance(SIGMA)  # M = Sigma^{-1}


# ---------------------------------------------------------------- Thm 8.1 / Cor 8.2
def test_thm81_rank_nullity():
    cons = [C(c_iv, 0.9)]
    Ct = cr.hard_operator(cons, theta=0.5, d=D)
    assert cr.cdi(Ct) == 1
    assert cr.h0_con_dim(Ct, D) == D - cr.cdi(Ct) == 3


def test_cor82_single_rule_detected():
    cons = [C(c_iv, 0.9), C(c_fu, 0.1)]
    Ct = cr.hard_operator(cons, theta=0.5, d=D)  # only c_iv active
    assert cr.cdi(Ct) == 1 and cr.h0_con_dim(Ct, D) == 3


# ---------------------------------------------------------------- Rmk 8.2 redundancy
def test_rmk82_redundancy_dim():
    # two blocks encoding the SAME constraint -> rank 1, redundancy 1
    cons = [C(c_iv, 0.9), C(c_iv, 0.8)]
    Ct = cr.hard_operator(cons, theta=0.5, d=D)
    assert cr.cdi(Ct) == 1
    assert cr.redundancy_dim(Ct) == Ct.shape[0] - 1 == 1


# ---------------------------------------------------------------- Patch 9 (row space)
def test_patch9_rowspace_not_support():
    # support {c_iv, c_fu} vs {c_iv, c_fu, c_iv+c_fu}: different support, same ker/rank
    base = np.vstack([c_iv, c_fu])
    extra = np.vstack([c_iv, c_fu, c_iv + c_fu])
    assert np.linalg.matrix_rank(base) == np.linalg.matrix_rank(extra) == 2
    assert cr.h0_con_dim(base, D) == cr.h0_con_dim(extra, D) == 2


# ---------------------------------------------------------------- Thm 8.3 onsets
def test_thm83_onsets_reachable_ranks_only():
    cons = [C(c_iv, 0.9), C(c_fu, 0.7), C(c_ivf, 0.4)]
    on = cr.onsets(cons, D)
    assert set(on.keys()) == {1, 2, 3}              # r_max = 3, no theta_4
    assert on[1] == pytest.approx(0.9)              # first dof loss at max weight
    assert on[2] == pytest.approx(0.7)
    assert on[3] == pytest.approx(0.4)


def test_onset_at_zero_weight():
    # r_max counts C_0 (incl. w=0); onset of the 2nd dof loss is theta_2 = 0 (v3.4 fix)
    cons = [C(c_iv, 0.9), C(c_fu, 0.0)]
    assert cr.r_max(cons, D) == 2
    assert cr.onsets(cons, D) == {1: 0.9, 2: 0.0}


def test_thm83_onsets_lipschitz_fixed_templates():
    rng = np.random.default_rng(0)
    cons = [C(c_iv, 0.9), C(c_fu, 0.7), C(c_ivf, 0.4)]
    eps = 0.05
    base = cr.onsets(cons, D)
    for _ in range(50):
        pert = [C(q.A, float(np.clip(q.w + rng.uniform(-eps, eps), 0, 1)), q.name) for q in cons]
        po = cr.onsets(pert, D)
        for k in base:
            assert abs(base[k] - po[k]) <= eps + 1e-9


# ---------------------------------------------------------------- Lemma 8.0 / Patch 7,14
def test_lemma80_gated_preserves_hard_kernel():
    cons = [C(c_iv, 0.9), C(c_fu, 0.2)]  # one active, one inactive at theta=0.5
    theta = 0.5
    Ct = cr.hard_operator(cons, theta, D)
    Lg = cr.gated_soft_laplacian(cons, theta, D, psi=lambda w: 0.5 + w)  # >0 for w>=theta
    assert cr.laplacian_kernel_dim(Lg, D) == cr.h0_con_dim(Ct, D) == 3


def test_lemma80_all_evidence_differs_from_hard():
    cons = [C(c_iv, 0.9), C(c_fu, 0.2)]
    theta = 0.5
    Ct = cr.hard_operator(cons, theta, D)
    La = cr.all_evidence_laplacian(cons, theta, D, h=0.1)
    # logistic positive everywhere -> kernel = intersection of ALL ker c_q (dim 2) != hard (3)
    assert cr.laplacian_kernel_dim(La, D) == 2
    assert cr.laplacian_kernel_dim(La, D) != cr.h0_con_dim(Ct, D)


# ---------------------------------------------------------------- Thm 8.4 SDCI (M-geometry)
def test_thm87_sdci_limits_and_monotonicity():
    cons = cr.normalize_constraints([C(c_iv, 0.9), C(c_fu, 0.8)], M)
    Lg = cr.gated_soft_laplacian(cons, theta=0.5, d=D, psi=lambda w: 1.0)
    # SDCI is monotone DECREASING in tau; taus are decreasing, so vals must INCREASE
    taus = [1.0, 0.1, 0.01, 1e-3]
    vals = [cr.sdci_M(Lg, M, t) for t in taus]
    assert all(vals[i] <= vals[i + 1] + 1e-9 for i in range(len(vals) - 1))
    # tau -> 0 recovers rank of (gated) soft Laplacian = CDI
    assert cr.sdci_M(Lg, M, 1e-6) == pytest.approx(np.linalg.matrix_rank(Lg), abs=1e-3)
    assert 0.0 <= vals[0] <= D


def test_thm84_spectral_stability_M_geometry():
    rng = np.random.default_rng(3)
    cons = cr.normalize_constraints([C(c_iv, 0.9), C(c_fu, 0.8)], M)
    L1 = cr.gated_soft_laplacian(cons, 0.5, D, psi=lambda w: 1.0)
    # PSD-preserving perturbation so Theorem 8.4's hypothesis L2 >= 0 actually holds
    B = rng.normal(0, 0.04, (3, D))
    L2 = L1 + B.T @ B
    assert np.linalg.eigvalsh(L2)[0] >= -1e-12  # L2 is PSD by construction
    tau = 0.5
    lhs = abs(cr.sdci_M(L1, M, tau) - cr.sdci_M(L2, M, tau))
    Mm12 = cr._sym_pow(M, -0.5)
    rhs = (D / tau) * np.linalg.norm(Mm12 @ (L1 - L2) @ Mm12, 2)
    assert lhs <= rhs + 1e-9


def test_sdci_rejects_non_psd():
    # an indefinite L must raise, not silently clip (v3.4 hardening)
    L = np.diag([1.0, -0.5, 0.0, 0.0])
    with pytest.raises(ValueError):
        cr.sdci_M(L, M, tau=0.5)


# ---------------------------------------------------------------- Prop 8.5 higher-order
def test_prop85_higher_order_invisible_to_pairwise():
    cons = [C(c_ivf, 0.9)]  # ternary only, no pairwise edge
    theta = 0.5
    Ct = cr.hard_operator(cons, theta, D)
    assert cr.cdi(Ct) == 1                       # collapse detected by rank
    assert cr.h0_con_dim(Ct, D) == 3
    assert cr.pairwise_beta0(cons, theta, D) == 4  # designated pairwise graph blind


# ---------------------------------------------------------------- Thm 8.6 factor-sheaf
def test_thm86_factor_sheaf_realization():
    for cons in ([C(c_iv, 0.9)],
                 [C(c_ivf, 0.9)],
                 [C(c_iv, 0.9), C(c_fu, 0.8)],
                 [C(np.vstack([c_iv, c_fu]), 0.9)]):  # multi-row block (Patch 13/16)
        theta = 0.5
        Ct = cr.hard_operator(cons, theta, D)
        assert cr.factor_sheaf_h0_dim(cons, theta, D) == cr.h0_con_dim(Ct, D)


# ---------------------------------------------------------------- Patch 11 normalization
def test_patch11_normalization_unit_dual_norm():
    cons = cr.normalize_constraints([C(c_iv, 0.9), C(c_ivf, 0.5)], M)
    for q in cons:
        for row in q.A:
            assert cr.dual_norm(row, M) == pytest.approx(1.0)
    # and c Sigma c^T == ||c||_{M^-1}^2  with M = Sigma^{-1}
    c = c_iv
    assert (c @ SIGMA @ c) == pytest.approx(c @ np.linalg.inv(M) @ c)


# ---------------------------------------------------------------- Patch 10 two energies
def test_patch10_two_energies_distinct_zero_sets():
    cons = [C(c_iv, 0.9), C(c_fu, 0.2)]  # c_fu inactive at theta=0.5
    theta = 0.5
    Lg = cr.gated_soft_laplacian(cons, theta, D, psi=lambda w: 1.0)
    La = cr.all_evidence_laplacian(cons, theta, D, h=0.05)
    x = np.array([1.0, 1.0, 5.0, 7.0])  # satisfies c_iv (x_i=x_v) but NOT c_fu (x_f!=x_u)
    assert cr.energy(x, Lg) == pytest.approx(0.0, abs=1e-9)   # gated zero -> active collapse
    assert cr.energy(x, La) > 1e-6                            # all-evidence sees c_fu pressure


def test_patch11_dimensionless_energy_scale_free():
    cons = [C(c_iv, 0.9)]
    Lg = cr.gated_soft_laplacian(cons, 0.5, D, psi=lambda w: 1.0)
    x = np.array([3.0, 1.0, 2.0, 0.5])
    e1 = cr.energy_dimensionless(x, Lg, M)
    e2 = cr.energy_dimensionless(100 * x, Lg, M)  # scaling x must not change ratio
    assert e1 == pytest.approx(e2)


# ---------------------------------------------------------------- Patch 5 input validation
def test_validation_weight_out_of_range():
    with pytest.raises(ValueError):
        C(c_iv, 1.5)
    with pytest.raises(ValueError):
        C(c_iv, -0.1)


def test_validation_zero_row():
    with pytest.raises(ValueError):
        C(np.zeros(4), 0.5)


def test_validation_dimension_mismatch():
    cons = [C(c_iv, 0.9), C(np.array([1.0, -1.0, 0.0]), 0.8)]  # d=3 vs d=4
    with pytest.raises(ValueError):
        cr.hard_operator(cons, 0.5, d=4)


def test_validation_bad_metric_and_params():
    with pytest.raises(ValueError):
        cr.metric_from_covariance(np.diag([1.0, 0.0, 1.0, 1.0]))  # not PD
    cons = [C(c_iv, 0.9)]
    with pytest.raises(ValueError):
        cr.all_evidence_laplacian(cons, 0.5, D, h=0.0)            # h <= 0
    Lg = cr.gated_soft_laplacian(cons, 0.5, D, psi=lambda w: 1.0)
    with pytest.raises(ValueError):
        cr.sdci_M(Lg, M, tau=0.0)                                 # tau <= 0


def test_validation_gated_psi_must_be_positive():
    cons = [C(c_iv, 0.9)]
    with pytest.raises(ValueError):
        cr.gated_soft_laplacian(cons, 0.5, D, psi=lambda w: 0.0)  # psi <= 0 active


def test_numerical_rank_is_canonical_and_consistent():
    # near-dependent rows: all rank consumers must agree
    near = np.vstack([c_iv, c_iv + 1e-13 * c_fu])
    r = cr.numerical_rank(near)
    assert r == 1
    assert cr.cdi(near) == r
    assert cr.laplacian_kernel_dim(near.T @ near, D) == D - r


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q"]))
