# State Machine: BTC Solver Bridge

## Overview

This document defines every state each actor can be in,
what triggers transitions, and what conditions must be true
for a transition to occur.

There are three state machines:

- **Intent** — the lifecycle of a user's bridge request
- **Solver** — the lifecycle of a solver agent
- **HTLC** — the lifecycle of a Bitcoin lock

---

## 1. Intent State Machine

### States

| State | Description |
|---|---|
| `CREATED` | Intent has been created and is waiting for broadcast |
| `QUOTED` | Intent has been broadcast and bids are being collected |
| `WINNER_SELECTED` | Coordinator has selected a winning solver |
| `BTC_LOCKED` | Winning solver has locked BTC via HTLC |
| `SETTLED` | EVM settlement confirmed, user received funds |
| `EXPIRED` | Intent failed to complete before deadline |

### Transitions
```
CREATED
  │
  │ coordinator broadcasts intent
  ▼
QUOTED
  │
  ├─── no valid bids received ──────────────────────────► EXPIRED
  │
  │ coordinator selects winner
  ▼
WINNER_SELECTED
  │
  ├─── solver goes offline / lock timeout ──────────────► QUOTED (reselection)
  │
  │ solver locks BTC via HTLC
  ▼
BTC_LOCKED
  │
  ├─── user never reveals preimage (timelock expiry) ───► EXPIRED
  ├─── EVM delay exceeds timelock buffer ───────────────► EXPIRED
  │
  │ user reveals preimage, EVM confirms settlement
  ▼
SETTLED
```

### Rules

- An intent can only move forward in state, except `WINNER_SELECTED → QUOTED` during reselection.
- An intent in `EXPIRED` is terminal. No further transitions.
- An intent in `SETTLED` is terminal. No further transitions.
- Only one solver can hold `WINNER_SELECTED` status per intent at any time.

---

## 2. Solver State Machine

### States

| State | Description |
|---|---|
| `IDLE` | Solver is available and listening for intents |
| `BIDDING` | Solver has submitted a bid for an active intent |
| `SELECTED` | Solver has been chosen by coordinator |
| `LOCKING` | Solver is in process of locking BTC via HTLC |
| `LOCKED` | Solver has successfully locked BTC |
| `COMPLETED` | Settlement confirmed, solver received fee |
| `FAILED` | Solver failed to lock after selection |
| `RECLAIMED` | Solver reclaimed BTC after timelock expiry |

### Transitions
```
IDLE
  │
  │ intent broadcast received
  ▼
BIDDING
  │
  ├─── bid rejected / another solver selected ─────────► IDLE
  │
  │ coordinator selects this solver
  ▼
SELECTED
  │
  ├─── solver goes offline / fails to lock ────────────► FAILED → IDLE
  │
  │ solver initiates BTC lock
  ▼
LOCKING
  │
  │ HTLC confirmed on Bitcoin
  ▼
LOCKED
  │
  ├─── user reveals preimage → settlement confirms ────► COMPLETED → IDLE
  │
  └─── timelock expires without settlement ────────────► RECLAIMED → IDLE
```

### Rules

- A solver in `FAILED` loses reputation score and returns to `IDLE`.
- A solver in `COMPLETED` has capital restored plus fee added.
- A solver in `RECLAIMED` has capital restored, no fee earned.
- A solver can only be in `SELECTED` or `LOCKING` for one intent at a time.
- A solver can be in `BIDDING` for multiple intents simultaneously.

---

## 3. HTLC State Machine

### States

| State | Description |
|---|---|
| `PENDING` | HTLC created, waiting for Bitcoin confirmation |
| `CONFIRMED` | Confirmation depth threshold reached |
| `UNLOCKED` | Preimage revealed, funds claimed by user side |
| `RECLAIMED` | Timelock expired, solver reclaimed BTC |
| `INVALID` | HTLC parameters did not match intent (rejected) |

### Transitions
```
PENDING
  │
  ├─── confirmation depth not reached before timelock ─► RECLAIMED
  │
  │ confirmation depth threshold reached
  ▼
CONFIRMED
  │
  ├─── user reveals preimage
  ▼
UNLOCKED
  │
  └─── EVM settlement confirms ────────────────────────► (Intent → SETTLED)


CONFIRMED
  │
  └─── timelock expires before preimage revealed ──────► RECLAIMED
       (Intent → EXPIRED)
```

### Rules

- An HTLC in `UNLOCKED` means atomicity succeeded.
- An HTLC in `RECLAIMED` means atomicity failed safely — solver recovers capital.
- An HTLC in `INVALID` triggers immediate intent cancellation.
- Confirmation depth is configurable. Default: 3 blocks.
- Timelock must be set long enough to absorb expected confirmation delay plus EVM settlement time.

---

## 4. Cross-Actor State Alignment

This table shows how states across actors must align at each protocol phase:

| Protocol Phase | Intent State | Solver State | HTLC State |
|---|---|---|---|
| Intent created | `CREATED` | `IDLE` | — |
| Bids collected | `QUOTED` | `BIDDING` | — |
| Winner selected | `WINNER_SELECTED` | `SELECTED` | — |
| BTC locking | `WINNER_SELECTED` | `LOCKING` | `PENDING` |
| BTC confirmed | `BTC_LOCKED` | `LOCKED` | `CONFIRMED` |
| Settlement done | `SETTLED` | `COMPLETED` | `UNLOCKED` |
| Timeout expired | `EXPIRED` | `RECLAIMED` | `RECLAIMED` |
| Solver failed | `QUOTED` | `FAILED` | — |

> If actor states are misaligned at any phase, it indicates a protocol
> violation or simulation bug.

---

## 5. Terminal States Summary

| Actor | Terminal States |
|---|---|
| Intent | `SETTLED`, `EXPIRED` |
| Solver | `COMPLETED`, `RECLAIMED` (then returns to `IDLE`) |
| HTLC | `UNLOCKED`, `RECLAIMED`, `INVALID` |

---

See `docs/failure_modes.md` for what happens during each failure transition.
See `docs/threat_model.md` for adversarial analysis of state transitions.