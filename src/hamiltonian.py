"""
hamiltonian.py: turns the plasma equations into a quantum "Hamiltonian" matrix H.

THE PHYSICS (Engel, Smith & Parker 2019), in normalised units
-------------------------------------------------------------
Take a small ripple in the electron velocity distribution, f = F0(v) + f1, with one
wavenumber k. The linearised Vlasov equation (particles) plus Ampere's law (field) give:

    d f1/dt = -i k v f1  -  v F0(v) E        (particles stream, and the field pushes them)
    d E /dt =  integral( v f1 dv )            (moving electrons form a current that changes E)

QUANTUM TRICK
-------------
Quantum computers can only apply UNITARY evolutions, psi(t) = exp(-i H t) psi(0), where H is
HERMITIAN (H equals its own conjugate transpose). Rescaling g = f1 / sqrt(F0) and putting v on
a grid turns the equations above into exactly that form:

    d psi/dt = -i H psi,      psi = (E, u_1, ..., u_Nv),   u_j = sqrt(dv) * g(v_j)

    H[j, j] = k v_j                    streaming: each velocity just spins its phase
    H[0, j] = +i a_j                   coupling between the field and velocity j ...
    H[j, 0] = -i a_j                   ... the conjugate entry, which makes H Hermitian
    with a_j = v_j * sqrt(F0(v_j) * dv)

H is mostly zeros. It is an "arrowhead" matrix: a diagonal plus one full row and one full column.
"""
import numpy as np

from src.config import Params


def maxwellian(v: np.ndarray) -> np.ndarray:
    """Background thermal distribution F0(v), a bell curve with unit thermal speed."""
    return np.exp(-v**2 / 2) / np.sqrt(2 * np.pi)


def build_hamiltonian(p: Params) -> np.ndarray:
    """Build the (2^n x 2^n) Hermitian matrix H described in the module docstring."""
    v = p.velocities
    a = v * np.sqrt(maxwellian(v) * p.dv)          # field <-> velocity coupling strengths

    size = p.n_v + 1                                # +1 because index 0 holds E
    H = np.zeros((size, size), dtype=complex)
    H[1:, 1:] = np.diag(p.k * v)                    # streaming term (diagonal)
    H[0, 1:] = 1j * a                               # coupling row
    H[1:, 0] = -1j * a                              # coupling column (conjugate of the row)
    return H


def initial_state(p: Params) -> np.ndarray:
    """
    Starting state psi(0): a small density ripple f1 = F0 (times epsilon, which drops out on normalising).

    The field must agree with that ripple through Gauss's law: i k E = -integral(f1 dv).
    Starting with E alone would break Gauss's law and leave a fake non-decaying field.
    """
    f0 = maxwellian(p.velocities)
    u = np.sqrt(p.dv * f0)                          # u_j = sqrt(dv) * f1/sqrt(F0) = sqrt(dv * F0)
    E = 1j * np.sum(f0 * p.dv) / p.k                # Gauss's law, using the same discrete sum
    psi = np.concatenate(([E], u)).astype(complex)
    return psi / np.linalg.norm(psi)                # quantum states have length 1


def field_energy(states: np.ndarray) -> np.ndarray:
    """|E(t)|^2, the wave's electric field energy. On a quantum computer this is P(measure |0...0>)."""
    return np.abs(states[:, 0]) ** 2
