# BTC Solver Bridge

A simulation of a competitive solver-based Bitcoin bridge architecture inspired by modern intent-based bridge designs such as Garden.

This project focuses on coordination, solver competition, settlement guarantees, and architectural tradeoffs — not production implementation.

---

## Overview

Bridging Bitcoin liquidity to EVM ecosystems requires careful coordination between users, solvers, and settlement contracts.

This project models a simplified architecture where:

- Users submit bridging intents
- An off-chain coordinator broadcasts intents
- Multiple independent solvers compete to fulfill them
- Bitcoin confirmations are observed
- Settlement is finalized on a simulated EVM contract

The goal is to explore the architectural structure and failure modes of solver-based bridges.

---

## Design Principles

- Clear trust boundaries
- Explicit non-goals
- Deterministic simulation
- Modular components
- Focus on coordination logic over cryptography

---

## System Components

- **User** — Creates a bridge intent.
- **Coordinator (Off-chain)** — Broadcasts intents and collects solver bids.
- **Solvers (N)** — Compete to fulfill intents and lock BTC.
- **Bitcoin Layer (Simulated)** — Produces blocks and confirmations.
- **Settlement Contract (Simulated EVM)** — Finalizes value release.

Full architectural details are documented in `docs/architecture.md`.

---

## Non-Goals

This project does not:

- Implement real Bitcoin scripts
- Deploy real smart contracts
- Provide a frontend interface
- Attempt production-level security
- Design tokenomics

It is a structural and architectural simulation only.

---

## Project Structure

btc-solver-bridge/

├── bridge/
│   ├── intent.py
│   ├── coordinator.py
│   ├── solver.py
│   ├── settlement.py
│   └── timeout.py
│
├── bitcoin/
│   ├── htlc.py
│   └── confirmation.py
│
├── economics/
│   ├── bidding.py
│   └── capital.py
│
├── simulation/
│   ├── runner.py
│   └── scenarios.py
│
├── docs/
│   ├── architecture.md
│   └── failure_modes.md
│
├── tests/
│
├── main.py
└── README.md

---

## Roadmap

- [ ] Architecture specification
- [ ] Intent lifecycle modeling
- [ ] Multi-solver competition logic
- [ ] Confirmation-based settlement handling
- [ ] Timeout and failure simulation
- [ ] Metrics and reporting

---

## Why This Project Exists

Solver-based bridges introduce new architectural patterns:

- Off-chain coordination
- Competitive liquidity provisioning
- Probabilistic finality handling
- Cross-domain settlement guarantees

This simulator exists to explore those patterns clearly and structurally.
