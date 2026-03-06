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

## 3. Component Interaction Map
```
Intent → Coordinator → Solver → HTLC
              │
              ↓
       CapitalManager
              │
              ↓
   ConfirmationTracker → Settlement → User
              │
              ↓
       TimeoutHandler
```

---

## 4. System Components

### 4.1 Intent — `bridge/intent.py`

Represents a user's request to swap assets cross-chain.

**Fields:**
- `intent_id`
- `user_address`
- `source_amount_btc`
- `max_fee`

> **Design Note:** In production, intents would be signed by the user's private key. In this simulator, signature verification is omitted for scope control. Fields like `destination_asset` and `deadline` are planned for future expansion.

---

### 4.2 Coordinator — `bridge/coordinator.py`

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

### 4.3 Solver — `bridge/solver.py`

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

### 4.4 HTLC Simulation — `bitcoin/htlc.py`

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

### 4.5 Confirmation Tracker — `bitcoin/confirmation.py`

Simulates Bitcoin probabilistic finality.

- Tracks block production
- Emits event when confirmation depth threshold is reached
- Settlement contract listens for this event and releases funds
- Mitigates reorg risk probabilistically

Default threshold: 3 confirmations (configurable)

---

### 4.6 Settlement Contract — `bridge/settlement.py`

Simulates deterministic EVM-side asset release.

**Behavior:**
- Waits for confirmation event from ConfirmationTracker
- Verifies HTLC parameters match intent
- Transfers destination asset to user
- Emits settlement completion event

> Assumes deterministic execution. No reorg modeling on EVM side.

---

### 4.7 Capital Manager — `economics/capital.py`

Tracks solver liquidity.

**Responsibilities:**
- Deduct capital when BTC locked
- Restore capital on settlement or reclaim
- Prevent overbidding beyond liquidity

Coordinator depends on CapitalManager to validate solver eligibility before selection.

---

### 4.8 Bidding Engine — `economics/bidding.py`

**Auction Model:**
- First-price sealed bid
- Solvers do not observe competitors' bids
- Coordinator selects lowest valid bid

**Strategic Implication:** Solvers must balance fee competitiveness, capital utilization, and risk exposure.

---

### 4.9 Timeout Handler — `bridge/timeout.py`

Handles all expiry scenarios:

- Solver fails to lock BTC → reselection
- User fails to reveal preimage → solver reclaim
- Intent deadline exceeded → cancellation

Ensures eventual resolution of all states.

---

### 4.10 Simulation Runner — `simulation/runner.py`

Orchestrates full end-to-end simulation runs.

`scenarios.py` injects failure conditions — coordinator down, solver offline, capital exhaustion — to test protocol resilience under adversarial conditions.

---

## 5. Intent State Machine
```
CREATED
  │
  ▼
QUOTED
  │
  ▼
WINNER_SELECTED
  │
  ├──────────────────┐
  ▼                  ▼
BTC_LOCKED        EXPIRED (solver offline / timeout)
  │
  ├──────────────────┐
  ▼                  ▼
SETTLED           EXPIRED (user griefing / EVM delay)
```

See `docs/state_machine.md` for full actor-level state transitions.

---

## 6. Economic Model
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

## 7. Failure Modes Summary

| Failure | Impact | Resolution |
|---|---|---|
| Winner offline | Liveness degradation | Coordinator reselection |
| Coordinator censorship | Centralization risk | Future decentralized auction |
| User griefing | Capital inefficiency | Timelock reclaim |
| EVM delay | Extended capital lock | Timelock buffer |
| Insufficient liquidity | Intent rejection | User retries |

> No failure mode results in permanent fund loss under honest Bitcoin consensus assumptions.

See `docs/failure_modes.md` for full recovery logic.

---

## 8. Trust Assumptions

- Coordinator acts honestly in selection.
- Solvers are economically rational.
- Bitcoin finality is probabilistic but bounded by confirmations.
- EVM settlement executes deterministically.

**Trust impacts liveness, not safety of locked funds.**

---

## 9. Upgrade Paths

- On-chain decentralized solver auction
- Solver bonding and slashing
- Reputation-weighted selection
- Reorg-aware settlement logic
- Dynamic risk-adjusted fee modeling

---

## 10. Core Design Philosophy

- Avoid unnecessary escrow complexity.
- Keep capital commitment post-selection.
- Model incentives explicitly.
- Separate safety guarantees from liveness guarantees.
- Document all trust assumptions.

---

## 11. Glossary

| Term | Definition |
|---|---|
| Intent | A user's request to swap assets cross-chain without specifying execution path |
| Solver | A capital provider that competes to fulfill intents for a fee |
| Coordinator | Off-chain actor that selects winning solver and orchestrates flow |
| HTLC | Hash Time Locked Contract — cryptographic lock ensuring atomic settlement |
| Hashlock | SHA256 hash of a secret preimage; unlocks funds when preimage revealed |
| Timelock | Block height or timestamp after which solver can reclaim locked BTC |
| Confirmation Depth | Number of Bitcoin blocks built on top of a transaction before it's considered final |
| Liveness | The property that the system continues making progress under non-adversarial conditions |

---

See `docs/threat_model.md` for adversarial analysis.
See `docs/failure_modes.md` for recovery logic.
See `docs/state_machine.md` for full state transitions.