# Threat Model: BTC Solver Bridge

## 1. Security Goals

The system aims to guarantee:

1. **Safety** — Locked BTC cannot be stolen by any party.
2. **Atomicity** — User receives destination asset if and only if solver can claim BTC.
3. **Eventual Resolution** — All intents resolve to either `SETTLED` or `EXPIRED`.
4. **Capital Integrity** — Solvers cannot oversubscribe liquidity.

The system does **not** guarantee:
- Fair solver selection (coordinator trust assumption)
- Optimal execution pricing
- Protection from capital inefficiency

---

## 2. Adversary Types

### A. Malicious Solver

**Capabilities:**
- Submits fake competitive bids
- Fails to lock BTC after selection
- Attempts to delay execution strategically

**Attack Goals:**
- Disrupt competitor execution
- Cause liveness degradation
- Manipulate reputation or selection flow

**Mitigations:**
- Capital checks before selection
- Reselection timeout window
- Reputation penalty mechanism
- No preimage access before BTC lock

**Impact Scope:** Liveness only. No direct fund theft possible.

---

### B. Malicious User

**Capabilities:**
- Submits intent but never reveals preimage
- Attempts griefing to lock solver capital indefinitely

**Attack Goals:**
- Capital exhaustion
- Strategic denial of service against solvers

**Mitigations:**
- HTLC timelock refund — solver reclaims BTC after expiry
- Capital lock duration is bounded by timelock
- Solver fee compensates for griefing risk

**Impact Scope:** Temporary capital inefficiency. No permanent loss.

---

### C. Malicious Coordinator

**Capabilities:**
- Censor specific solvers from receiving intents
- Always select same solver regardless of bids
- Delay reselection intentionally after solver failure

**Attack Goals:**
- Centralization of solver market
- Collusion with favored solver
- Market manipulation

**Current Mitigations:**
- Non-custodial design — coordinator never holds funds
- Winner announcement is public and observable

**Future Mitigation:** On-chain decentralized auction removes coordinator trust entirely.

**Impact Scope:** Liveness degradation, market fairness distortion. No custody risk.

---

### D. Coordinator-Solver Collusion

**Capabilities:**
- Coordinator consistently selects a specific solver in exchange for fee sharing
- Colluding solver submits non-competitive bids knowing it will win

**Attack Goals:**
- Eliminate solver competition
- Extract excess fees from users

**Mitigations:**
- Currently none beyond observability
- Future mitigation: verifiable on-chain selection with bid transparency

**Impact Scope:** Degrades economic efficiency. Does not affect fund safety.

---

### E. Bitcoin Reorg Risk

**Capabilities:**
- Chain reorganization after BTC lock
- Confirmation reversal below threshold

**Mitigation:**
- Configurable confirmation depth threshold
- Settlement only triggers after threshold is reached

**Impact Scope:** Delayed settlement. Low-probability double-spend risk, bounded by confirmation depth.

---

### F. Confirmation Tracker Manipulation

**Capabilities:**
- In production, a compromised confirmation tracker could signal
  premature finality before sufficient confirmations exist

**Mitigation:**
- In simulation this is internal and trusted
- In production, confirmation data must come from an independent Bitcoin node

**Impact Scope:** Premature settlement trigger. Mitigated by independent data sourcing.

---

## 3. Attack Surface Summary

| Surface | Risk Level | Protection |
|---|---|---|
| Bid manipulation | Low | Sealed-bid model |
| Capital oversubscription | Medium | Capital manager enforcement |
| Preimage leakage | Critical | Preimage revealed only after EVM settlement confirms |
| Timeout griefing | Medium | Timelock reclaim |
| Coordinator bias | High (liveness) | Documented trust assumption |
| Coordinator-solver collusion | High (economic) | Future on-chain selection |
| Confirmation manipulation | Medium | Independent node requirement |

> **Preimage leakage is Critical** because if the preimage is shared with
> the solver before EVM settlement confirms, the solver can claim BTC
> without the user receiving destination funds — breaking atomicity.

---

## 4. Safety vs Liveness Separation

This protocol explicitly separates:

**Safety** — Enforced cryptographically via HTLC and timelock.
No party can steal funds regardless of coordinator or solver behavior.

**Liveness** — Dependent on coordinator honesty and solver responsiveness.
Adversarial behavior slows settlement but does not cause fund loss.

Even under adversarial conditions:
> Funds remain safe. Settlement may slow.

This distinction is intentional and is the core security property of HTLC-based bridges.

---

## 5. Out-of-Scope Threats

The simulator does not model:

- Network-level eclipse attacks on Bitcoin nodes
- Miner extractable value (MEV) on EVM side
- Deep Bitcoin reorgs beyond confirmation threshold
- EVM consensus failures
- Private key compromise of any actor

These threats are external to protocol logic and outside simulation scope.