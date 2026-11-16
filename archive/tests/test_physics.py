"""Checks that the quantum circuit reproduces real Landau damping."""
import pytest

from src.config import Params
from src.hamiltonian import field_energy
from src.simulate import classify_stability, fit_damping_rate, run_quantum
from src.theory import landau_prediction


def test_landau_prediction_matches_textbook():
    """Known benchmark: wavenumber 0.5 gives oscillation rate 1.4156 and damping rate -0.1533."""
    wave = landau_prediction(0.5)
    assert wave.real == pytest.approx(1.4156, abs=1e-3)
    assert wave.imag == pytest.approx(-0.1533, abs=1e-3)


@pytest.mark.parametrize("wavenumber", [0.4, 0.5, 0.6])
def test_quantum_damping_rate_matches_theory(wavenumber):
    """The fade rate measured from the circuit is within 10% of Landau's prediction."""
    settings = Params(wavenumber=wavenumber)
    energy = field_energy(run_quantum(settings))
    fit_end = min(settings.end_time, 0.8 * settings.fake_revival_time)
    damping_rate = fit_damping_rate(settings.times, energy, 2.0, fit_end)
    assert damping_rate == pytest.approx(landau_prediction(wavenumber).imag, rel=0.10)


def test_classifier_flags_slow_and_fast_damping():
    """Strongly damped short waves fade by t=8; weakly damped long waves don't."""
    for wavenumber, expected in [(0.7, True), (0.3, False)]:
        settings = Params(wavenumber=wavenumber)
        energy = field_energy(run_quantum(settings))
        assert classify_stability(settings.times, energy, check_time=8.0)["damped"] is expected
