"""
hamiltonian.py: turns the plasma equations into a quantum "Hamiltonian" matrix.

THE PHYSICS (Engel, Smith & Parker 2019), in normalised units
-------------------------------------------------------------
Picture the electrons as a crowd with a bell-curve spread of velocities (the `background`).
We add a small `ripple` to that crowd, shaped like a single wave with a given wavenumber.
Two rules then describe what happens (the linearised Vlasov and Ampere equations):

    rate of change of ripple = -i * wavenumber * velocity * ripple  -  velocity * background * field
        (electrons coast along at their own speed, and the electric field pushes them)
    rate of change of field  = sum over velocities of (velocity * ripple * velocity_spacing)
        (moving electrons are an electric current, and currents change the field)

QUANTUM TRICK
-------------
Quantum computers can only apply UNITARY evolutions: new_state = exp(-i * hamiltonian * t) * old_state,
where the hamiltonian matrix is HERMITIAN (it equals its own conjugate transpose). Dividing the
ripple by sqrt(background) and putting velocity on a grid turns the rules above into exactly that:

    state = (field, particle_1, ..., particle_N)
            where particle_j = sqrt(velocity_spacing) * ripple(velocity_j) / sqrt(background(velocity_j))

    hamiltonian[j, j] = wavenumber * velocity_j     coasting: each velocity just rotates its phase
    hamiltonian[0, j] = +i * coupling_j             link between the field and velocity j ...
    hamiltonian[j, 0] = -i * coupling_j             ... its mirror entry, which makes the matrix Hermitian
    with coupling_j = velocity_j * sqrt(background(velocity_j) * velocity_spacing)

The matrix is mostly zeros. It is an "arrowhead": a diagonal plus one full row and one full column.
"""
import numpy as np

from src.config import Params


def background_distribution(velocities: np.ndarray) -> np.ndarray:
    """How many electrons move at each velocity when undisturbed: a bell curve (the "Maxwellian")."""
    return np.exp(-velocities**2 / 2) / np.sqrt(2 * np.pi)


def build_hamiltonian(settings: Params) -> np.ndarray:
    """Build the (2^n x 2^n) Hermitian matrix described in the module docstring."""
    velocities = settings.velocities
    coupling = velocities * np.sqrt(background_distribution(velocities) * settings.velocity_spacing)

    size = settings.n_velocities + 1                                     # +1 because slot 0 holds the field
    hamiltonian = np.zeros((size, size), dtype=complex)
    hamiltonian[1:, 1:] = np.diag(settings.wavenumber * velocities)      # coasting term (diagonal)
    hamiltonian[0, 1:] = 1j * coupling                                   # field <-> particle row
    hamiltonian[1:, 0] = -1j * coupling                                  # mirror column (conjugate of the row)
    return hamiltonian


def initial_state(settings: Params) -> np.ndarray:
    """
    Starting state: a small density ripple shaped like the background itself
    (times a tiny size factor, which disappears when we normalise).

    The field must agree with that ripple through Gauss's law:
        i * wavenumber * field = -(sum of ripple * velocity_spacing)
    (extra electrons in one place create a field around them). Starting with a field and no
    ripple would break Gauss's law and leave a fake field that never decays.
    """
    background = background_distribution(settings.velocities)
    particles = np.sqrt(settings.velocity_spacing * background)          # the rescaling from the docstring, with ripple = background
    field = 1j * np.sum(background * settings.velocity_spacing) / settings.wavenumber   # Gauss's law, same discrete sum
    state = np.concatenate(([field], particles)).astype(complex)
    return state / np.linalg.norm(state)                                 # quantum states have length 1


def field_energy(states: np.ndarray) -> np.ndarray:
    """|field|^2 at every time: the wave's energy. On a quantum computer this is P(measure |0...0>)."""
    return np.abs(states[:, 0]) ** 2
