# Failure Modes: BTC Solver Bridge

## Overview

This document describes every failure condition the system can encounter,
what triggers it, how the system responds, and what the recovery path is.

Failures are categorized into three layers:

- **Coordination failures** — problems in solver selection
- **Settlement failures** — problems in BTC lock or EVM release
- **Economic failures** — problems in capital or incentive logic

---

## 1. Coordination Failures

### 1.1 Winning Solver Goes Offline

**Trigger:**
Coordinator selects a winner but solver does not lock BTC within timeout window.

**System Response:**
- Coordinator detects timeout
- Intent state reverts to `QUOTED`
- Coordinator runs reselection from remaining valid bids

**Recovery Path:**
```
WINNER_SELECTED → (timeout) → QUOTED → WINNER_SELECTED (new solver)
```

**Impact:** Increased latency. No fund loss.

**Unresolved Risk:**
If all solvers go offline, intent cannot be fulfilled and moves to `EXPIRED`.

---

### 1.2 No Valid Bids Received

**Trigger:**
No solver has sufficient capital or all bids exceed `max_fee`.

**System Response:**
- Coordinator rejects intent
- Intent moves to `EXPIRED`
- User must retry with adjusted parameters

**Recovery Path:**
```
CREATED → EXPIRED
```

**Impact:** Intent failure. User retries. No fund loss.

---

### 1.3 Coordinator Censorship

**Trigger:**
Coordinator ignores specific solvers during broadcast or selection.

**System Response:**
- No automatic recovery in current design
- Censored solvers cannot participate
- Liveness degrades for censored parties

**Recovery Path:**
None in current design.

**Future Mitigation:**
On-chain decentralized auction where coordinator cannot selectively exclude solvers.

**Impact:** Liveness degradation. No fund loss.

---

### 1.4 Coordinator Goes Offline

**Trigger:**
Coordinator becomes unavailable after intent is created but before winner is selected.

**System Response:**
- Intent remains in `CREATED` or `QUOTED` state indefinitely
- No solver is selected
- Intent expires at deadline

**Recovery Path:**
```
CREATED → (deadline exceeded) → EXPIRED
```

**Future Mitigation:**
Redundant coordinator instances or decentralized selection.

**Impact:** Intent failure. No fund loss since no BTC was locked.

---

## 2. Settlement Failures

### 2.1 Solver Fails to Lock BTC After Selection

**Trigger:**
Winning solver is selected but does not produce a valid HTLC lock within timeout.

**System Response:**
- Coordinator reselects next best solver
- Capital is not deducted (lock never happened)
- Reputation penalty applied to failing solver

**Recovery Path:**
```
WINNER_SELECTED → (lock timeout) → QUOTED → WINNER_SELECTED (new solver)
```

**Impact:** Latency increase. Solver reputation penalty.

---

### 2.2 User Never Reveals Preimage (Griefing)

**Trigger:**
Solver locks BTC via HTLC but user never reveals preimage to complete settlement.

**System Response:**
- Settlement contract never receives preimage
- HTLC timelock expires
- Solver reclaims locked BTC via timelock path

**Recovery Path:**
```
BTC_LOCKED → (timelock expiry) → EXPIRED
Solver capital restored via reclaim
```

**Impact:** Temporary capital lockup for solver. No permanent loss.

**Economic Note:**
Solver fee partially compensates for griefing risk.
Rational users do not grief because they lose destination funds.

---

### 2.3 Bitcoin Confirmation Delay

**Trigger:**
Bitcoin network congestion causes confirmation depth threshold to be reached slowly.

**System Response:**
- ConfirmationTracker continues polling
- Settlement is blocked until threshold reached
- HTLC timelock buffer absorbs moderate delays

**Recovery Path:**
```
BTC_LOCKED → (delayed confirmations) → BTC_LOCKED → SETTLED
```

**Impact:** Delayed settlement. If delay exceeds timelock buffer, solver reclaims.

---

### 2.4 Bitcoin Reorg Below Confirmation Threshold

**Trigger:**
A chain reorganization reverses blocks containing the HTLC lock transaction.

**System Response:**
- ConfirmationTracker detects confirmation count drop
- Settlement blocked until depth restored
- If reorg is deep enough, lock is effectively lost

**Recovery Path:**
```
BTC_LOCKED → (reorg detected) → BTC_LOCKED (re-tracking)
```

**Impact:** Settlement delay. Deep reorgs may require solver to re-lock.

**Mitigation:**
Configurable confirmation depth. Higher threshold = lower reorg risk.

---

### 2.5 EVM Settlement Delay

**Trigger:**
EVM network congestion delays settlement contract execution after confirmation.

**System Response:**
- Settlement contract queues execution
- HTLC timelock buffer absorbs delay
- If delay exceeds buffer, solver reclaims BTC

**Recovery Path:**
```
BTC_LOCKED → (EVM delay) → SETTLED or EXPIRED
```

**Impact:** Extended capital lockup. Possible solver reclaim if delay is excessive.

---

## 3. Economic Failures

### 3.1 Solver Capital Exhaustion

**Trigger:**
Solver has committed capital to active HTLCs and cannot bid on new intents.

**System Response:**
- CapitalManager blocks solver from bidding
- Solver excluded from selection until capital is restored
- Other solvers fill the gap

**Recovery Path:**
Capital restored when existing HTLCs settle or timeout.

**Impact:** Temporary solver unavailability. No fund loss.

---

### 3.2 All Solvers Capital Exhausted

**Trigger:**
All registered solvers are fully committed and cannot fulfill new intents.

**System Response:**
- Coordinator receives no valid bids
- Intent moves to `EXPIRED`
- User must retry later

**Recovery Path:**
```
CREATED → EXPIRED
User retries when solver capital restores
```

**Impact:** System-wide liveness degradation. No fund loss.

---

### 3.3 Solver Bids Unprofitably

**Trigger:**
Solver submits a bid where fee does not cover capital lock cost and risk cost.

**System Response:**
- No immediate system response — solver participates at a loss
- Over time, unprofitable solvers exit the market

**Impact:** Economic inefficiency. Healthy competition self-corrects over time.

---

## 4. Failure Mode Summary Table

| Failure | Layer | Trigger | Recovery | Fund Loss |
|---|---|---|---|---|
| Winner offline | Coordination | Lock timeout | Reselection | None |
| No valid bids | Coordination | No capital / fee too low | Intent expires | None |
| Coordinator censorship | Coordination | Biased selection | None (future: on-chain) | None |
| Coordinator offline | Coordination | Unavailability | Intent expires | None |
| Solver fails to lock | Settlement | Lock timeout | Reselection | None |
| User griefing | Settlement | Preimage withheld | Timelock reclaim | None |
| Confirmation delay | Settlement | Network congestion | Wait or reclaim | None |
| Bitcoin reorg | Settlement | Chain reorganization | Re-track confirmations | None |
| EVM delay | Settlement | Network congestion | Wait or reclaim | None |
| Capital exhaustion | Economic | Over-commitment | Wait for restore | None |
| All solvers exhausted | Economic | System overload | Intent expires | None |
| Unprofitable bid | Economic | Miscalculation | Market self-corrects | None |

> Under honest Bitcoin consensus assumptions, no failure mode results
> in permanent fund loss for any party.

---

## 5. Recovery Design Principles

- Every failure must resolve to either `SETTLED` or `EXPIRED`. No intent hangs forever.
- Solver capital is always recoverable via timelock reclaim.
- Coordinator failure affects liveness only, never fund safety.
- Confirmation depth is the primary lever against reorg risk.

---

See `docs/state_machine.md` for full state transition diagrams.
See `docs/threat_model.md` for adversarial analysis of these failures.