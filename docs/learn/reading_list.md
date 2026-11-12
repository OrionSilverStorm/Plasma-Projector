# Reading list

Most important first. Abstract and introduction are usually enough. Check citations before using them on slides.

## Core
1. **Engel, Smith & Parker**, *Quantum algorithm for the Vlasov equation*, Phys. Rev. A 100, 062315 (2019). arXiv:1907.09418. **Our method**; section II is the rescaling trick (doc 2, step 3).
2. **Dodin & Startsev**, *On applications of quantum computing to plasma simulations*, Phys. Plasmas 28, 092101 (2021). arXiv:2005.14369. Balanced overview, including readout. For the limitations slide.
3. **Joseph et al.**, *Quantum computing for fusion energy science applications*, Phys. Plasmas 30, 010501 (2023). arXiv:2212.05054. Fusion-community review. For the "why fusion" slide.

## Deeper
4. **Ameri, Ye, Cappellaro, Krovi & Loureiro**, *Quantum algorithm for the linear Vlasov equation with collisions*, Phys. Rev. A 107, 062412 (2023). Adds collisions and gate counts.
5. **Berry, Childs & Kothari**, *Hamiltonian simulation with nearly optimal dependence on all parameters* (2015). Formal basis for "mostly-zero matrix → polynomial gates". Cite, don't study.
6. **Jin, Liu & Yu**, *Quantum simulation of partial differential equations via Schrödingerisation* (2022). Handling growing waves: our roadmap.

## Textbooks
- **F. F. Chen**, *Introduction to Plasma Physics and Controlled Fusion*: ch. 4 (plasma waves), ch. 7 (Landau damping).
- **Nielsen & Chuang**, *Quantum Computation and Quantum Information*: ch. 1–2 (qubits), §4.7 (Trotter).
- **Qiskit docs** (docs.quantum.ibm.com): `PauliEvolutionGate`, `SuzukiTrotter`, `StatePreparation`, `SparsePauliOp`.
