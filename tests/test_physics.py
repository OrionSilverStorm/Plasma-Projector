"""Checks that the quantum circuit reproduces real Landau damping."""
import pytest

from src.config import Params
from src.hamiltonian import field_energy
from src.simulate import classify_stability, fit_damping_rate, run_quantum
from src.theory import landau_root


def test_landau_root_matches_textbook():
    """Known benchmark: k*lambda_D = 0.5 gives omega = 1.4156 - 0.1533i."""
    omega = landau_root(0.5)
    assert omega.real == pytest.approx(1.4156, abs=1e-3)
    assert omega.imag == pytest.approx(-0.1533, abs=1e-3)


@pytest.mark.parametrize("k", [0.4, 0.5, 0.6])
def test_quantum_damping_rate_matches_theory(k):
    """The decay rate measured from the circuit is within 10% of Landau's prediction."""
    p = Params(k=k)
    energy = field_energy(run_quantum(p))
    gamma = fit_damping_rate(p.times, energy, 2.0, min(p.t_max, 0.8 * p.recurrence_time))
    assert gamma == pytest.approx(landau_root(k).imag, rel=0.10)


def test_classifier_flags_slow_and_fast_damping():
    """Strongly damped short waves fade by t=8; weakly damped long waves don't."""
    for k, expected in [(0.7, True), (0.3, False)]:
        p = Params(k=k)
        energy = field_energy(run_quantum(p))
        assert classify_stability(p.times, energy, t_check=8.0)["damped"] is expected
