# Architecture: BTC Solver Bridge

## 1. Overview

BTC Solver Bridge is a simulation of a solver-based cross-chain settlement protocol inspired by Garden Finance.

The system enables competitive Bitcoin liquidity provisioning for cross-chain intents using:

- Sealed-bid solver competition
- Centralized but non-custodial coordination
- HTLC-based Bitcoin settlement
- Deterministic EVM-side execution
- Explicit capital and incentive modeling

The primary goal of this simulator is to model:

- Solver competition dynamics
- Capital constraints and liquidity efficiency
- Liveness risks introduced by coordination
- Atomicity guarantees using hashlocks and timelocks
- Economic incentives for rational solvers

> This is not a custodial bridge. No party holds user funds beyond protocol-defined locking rules.

---

## 2. High-Level System Flow

```
User
 │
 │  (1) Publishes Intent
 ▼
Coordinator
 │
 │  (2) Broadcasts Intent to Solvers
 ▼
Solvers
 │
 │  (3) Submit Sealed Bids (fee + ETA)
 ▼
Coordinator
 │
 │  (4) Selects & Announces Winner
 ▼
Winning Solver
 │
 │  (5) Locks BTC via HTLC
 ▼
Confirmation Tracker
 │
 │  (6) Confirms Bitcoin Finality
 ▼
Settlement Contract (EVM)
 │
 │  (7) Releases Destination Asset
 ▼
User receives funds
```

**Key design choice:**

Winner is selected before BTC lock. Capital commitment occurs post-selection.

This avoids escrow bootstrapping complexity and double-lock race conditions.

---

## 3. System Components

### 3.1 Intent — `bridge/intent.py`

Represents a user's request to swap assets cross-chain.

**Fields:**
- `intent_id`
- `user_address`
- `source_amount_btc`
- `destination_asset`
- `deadline`
- `max_fee`

> **Design Note:** In production, intents would be signed. In this simulator, signature verification is omitted for scope control.

---

### 3.2 Coordinator — `bridge/coordinator.py`

The coordinator orchestrates bidding and selection.

**Responsibilities:**
- Validate intents
- Broadcast to registered solvers
- Collect sealed bids
- Select winner
- Announce winner publicly
- Reselect on failure

**Selection Rule:**
```
winner = argmin(fee_rate)
subject to:
    solver.available_capital ≥ intent.source_amount_btc
```

**Trust Model:**
- Non-custodial
- Centralized
- Accountable but censorable

Censorship introduces liveness risk, not fund loss.

> **Future Upgrade Path:** On-chain auction-based solver selection.

---

### 3.3 Solver — `bridge/solver.py`

Solvers are rational liquidity providers.

**Properties:**
- `solver_id`
- `available_capital`
- `fee_rate`
- `reputation_score`

**Behavior:**
- Listens for intents
- Submits bid if profitable
- Locks BTC if selected
- Receives fee on completion
- Suffers reputation penalty if failing to execute

> Solvers do not pre-commit capital before selection.

---

### 3.4 HTLC Simulation — `bitcoin/htlc.py`

Models Bitcoin-side atomicity.

**HTLC Parameters:**
- `hashlock = SHA256(preimage)`
- `timelock`
- `amount`
- `solver_address`

**Safety Guarantees:**
- User receives funds only if preimage revealed
- Solver reclaims BTC after timelock expiry
- No counterparty custody risk

---

### 3.5 Confirmation Tracker — `bitcoin/confirmation.py`

Simulates Bitcoin probabilistic finality.

- Tracks block production
- Emits event after configurable confirmation depth
- Mitigates reorg risk probabilistically

Default threshold: 3 confirmations (configurable)

---

### 3.6 Settlement Contract — `bridge/settlement.py`

Simulates deterministic EVM-side asset release.

**Behavior:**
- Waits for confirmed HTLC
- Verifies parameters match intent
- Transfers destination asset
- Emits settlement completion event

> Assumes deterministic execution (no reorg modeling on EVM side).

---

### 3.7 Capital Manager — `economics/capital.py`

Tracks solver liquidity.

**Responsibilities:**
- Deduct capital when BTC locked
- Restore capital on settlement or reclaim
- Prevent overbidding beyond liquidity

This enforces realistic capital constraints and models opportunity cost.

---

### 3.8 Bidding Engine — `economics/bidding.py`

**Auction Model:**
- First-price sealed bid
- Solvers do not observe competitors' bids
- Coordinator selects lowest valid bid

**Strategic Implication:** Solvers must balance fee competitiveness, capital utilization, and risk exposure.

---

### 3.9 Timeout Handler — `bridge/timeout.py`

Handles all expiry scenarios:

- Solver fails to lock BTC → reselection
- User fails to reveal preimage → solver reclaim
- Intent deadline exceeded → cancellation

Ensures eventual resolution of all states.

---

## 4. Economic Model

Solver expected profit:

```
Profit = Fee - Capital Lock Cost - Risk Cost

Where:
  Fee               = user payment
  Capital Lock Cost = opportunity cost during HTLC duration
  Risk Cost         = probability-weighted loss from delays or failures

Rational participation condition:
  Profit > 0
```

This models solver competition as a capital allocation problem.

---

## 5. Failure Modes Summary

| Failure | Impact | Resolution |
|---|---|---|
| Winner offline | Liveness degradation | Coordinator reselection |
| Coordinator censorship | Centralization risk | Future decentralized auction |
| User griefing | Capital inefficiency | Timelock reclaim |
| EVM delay | Extended capital lock | Timelock buffer |
| Insufficient liquidity | Intent rejection | User retries |

> No failure mode results in permanent fund loss under honest Bitcoin consensus assumptions.

---

## 6. Trust Assumptions

- Coordinator acts honestly in selection.
- Solvers are economically rational.
- Bitcoin finality is probabilistic but bounded by confirmations.
- EVM settlement executes deterministically.

**Trust impacts liveness, not safety of locked funds.**

---

## 7. Upgrade Paths

- On-chain decentralized solver auction
- Solver bonding and slashing
- Reputation-weighted selection
- Reorg-aware settlement logic
- Dynamic risk-adjusted fee modeling

---

## 8. Core Design Philosophy

- Avoid unnecessary escrow complexity.
- Keep capital commitment post-selection.
- Model incentives explicitly.
- Separate safety guarantees from liveness guarantees.
- Document all trust assumptions.

---
