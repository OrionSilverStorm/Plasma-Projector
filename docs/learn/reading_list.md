# Reading list

Ordered from most to least important for this project. Check the citation details before putting them on a slide.

## Core (read the abstract and intro at least)
1. **A. Engel, G. Smith, S. E. Parker**, *Quantum algorithm for the Vlasov equation*, Phys. Rev. A 100, 062315 (2019). arXiv:1907.09418.
   **Our base method.** Section II is the Hermitian rescaling we implement. Read it alongside doc 2.
2. **I. Y. Dodin, E. A. Startsev**, *On applications of quantum computing to plasma simulations*, Phys. Plasmas 28, 092101 (2021). arXiv:2005.14369.
   An honest overview of what quantum can and can't do for plasmas, including the readout problem. Good for the limitations slide.
3. **I. Joseph et al.**, *Quantum computing for fusion energy science applications*, Phys. Plasmas 30, 010501 (2023). arXiv:2212.05054.
   A US fusion community review. Use it for the impact slide and the "why fusion" framing.

## Deeper
4. **A. Ameri, E. Ye, P. Cappellaro, H. Krovi, N. F. Loureiro**, *Quantum algorithm for the linear Vlasov equation with collisions*, Phys. Rev. A 107, 062412 (2023). The next step beyond our model, with gate-complexity analysis.
5. **D. W. Berry, A. M. Childs, R. Kothari**, *Hamiltonian simulation with nearly optimal dependence on all parameters* (2015). The formal basis for "sparse H means poly(n) gates".
6. **S. Jin, N. Liu, Y. Yu**, *Quantum simulation of partial differential equations via Schrödingerisation* (2022). How to handle non-Hermitian (growing-mode) problems: our roadmap.

## Background textbooks
- **F. F. Chen**, *Introduction to Plasma Physics and Controlled Fusion*, ch. 4 (plasma waves) and ch. 7 (kinetic theory and Landau damping, including the surfer picture).
- **Nielsen & Chuang**, *Quantum Computation and Quantum Information*, §4.7 (Hamiltonian simulation and Trotter).
- **Qiskit docs**: `PauliEvolutionGate`, `SuzukiTrotter`, `StatePreparation`, `SparsePauliOp` at docs.quantum.ibm.com.
