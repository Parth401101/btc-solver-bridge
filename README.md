# BTC Solver Bridge

Simulation of a solver-based Bitcoin bridge — modeling coordinator selection, HTLC locking, settlement guarantees, and failure modes. Architectural research, not production code.

---

## Overview

Bridging Bitcoin liquidity to EVM ecosystems requires careful coordination between users, solvers, and settlement contracts.

This project models a simplified architecture where:

- Users submit bridging intents
- An off-chain coordinator broadcasts intents
- Multiple independent solvers compete to fulfill them
- Bitcoin confirmations are observed
- Settlement is finalized on a simulated EVM contract

The system models intent propagation, solver bidding, BTC locking via simulated HTLCs, confirmation observation, and conditional settlement on an EVM-side contract.

The goal is to explore the architectural structure, coordination mechanics, and failure modes of solver-based bridges.

---

## Design Principles

- Clear trust boundaries
- Explicit non-goals
- Deterministic simulation
- Modular components
- Focus on coordination logic over cryptography

---

## System Components

- **User** — Creates a bridge intent specifying amount, destination, and timeout.
- **Coordinator (Off-chain)** — Broadcasts intents and collects solver bids. Does not custody funds.
- **Solvers (N)** — Compete to fulfill intents, lock BTC, and execute settlement.
- **Bitcoin Layer (Simulated)** — Produces confirmations and models HTLC-based locking.
- **Settlement Contract (Simulated EVM)** — Finalizes value release or triggers refunds.

Full architectural details are documented in `docs/architecture.md`.

---

## Non-Goals

This project does not:

- Implement real Bitcoin scripts
- Deploy real smart contracts
- Provide a frontend interface
- Attempt production-level security
- Design tokenomics
- Replace existing bridge implementations

It is a structural and architectural simulation only.

---

## Project Structure
```
btc-solver-bridge/
├── bridge/
│   ├── intent.py
│   ├── coordinator.py
│   ├── solver.py
│   ├── settlement.py
│   └── timeout.py
├── bitcoin/
│   ├── htlc.py
│   └── confirmation.py
├── economics/
│   ├── bidding.py
│   └── capital.py
├── simulation/
│   ├── runner.py
│   ├── scenarios.py
│   └── logger.py
├── docs/
│   ├── architecture.md
│   ├── threat_model.md
│   ├── failure_modes.md
│   └── state_machine.md
├── tests/
├── main.py
└── README.md
```

---

## Running the Simulation
```bash
python3 main.py
```

Output:
```
==================================================
BTC SOLVER BRIDGE — FULL SIMULATION
==================================================

--- Scenario 1: Happy Path ---
--- Scenario 2: HTLC Expiry ---
--- Scenario 3: Capital Exhaustion ---
--- Scenario 4: Solver Offline ---
--- Scenario 5: Coordinator Censorship ---
--- Scenario 6: All Solvers Exhausted ---

==================================================
SIMULATION SUMMARY
==================================================
  ✅ PASS  Happy Path
  ✅ PASS  HTLC Expiry
  ✅ PASS  Capital Exhaustion
  ✅ PASS  Solver Offline Reselection
  ✅ PASS  Coordinator Censorship
  ✅ PASS  All Solvers Exhausted

6/6 scenarios passed.
==================================================
```

---

## Roadmap

- [x] Architecture specification
- [x] Threat model
- [x] Failure mode analysis
- [x] State machine design
- [x] Intent lifecycle modeling
- [x] Multi-solver competition logic
- [x] HTLC locking simulation
- [x] Confirmation-based settlement handling
- [x] Timeout and refund simulation
- [x] Failure scenario modeling
- [x] Simulation runner with structured logging
- [ ] Test suite
- [ ] Rust core rewrite

---

## Why This Project Exists

Solver-based bridges shift liquidity provisioning from custodial models to competitive, capital-constrained actors coordinated off-chain.

This introduces new architectural patterns:

- Off-chain intent propagation
- Competitive liquidity provisioning
- Probabilistic finality handling
- Cross-domain settlement guarantees

This simulator exists to explore those patterns clearly, structurally, and transparently.