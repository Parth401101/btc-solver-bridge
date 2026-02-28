
## 9. Threat Model

### 9.1 Security Goals

The system aims to guarantee:

1. **Safety** — Locked BTC cannot be stolen by any party.
2. **Atomicity** — User receives destination asset if and only if solver can claim BTC.
3. **Eventual Resolution** — All intents resolve to either `Settled` or `Expired`.
4. **Capital Integrity** — Solvers cannot oversubscribe liquidity.

The system does **not** guarantee:
- Fair solver selection (coordinator trust assumption)
- Optimal execution pricing
- Protection from capital inefficiency

---

### 9.2 Adversary Types

#### A. Malicious Solver

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

#### B. Malicious User

**Capabilities:**
- Submits intent but never reveals preimage
- Attempts griefing to lock solver capital

**Attack Goals:**
- Capital exhaustion
- Strategic denial of service

**Mitigations:**
- HTLC timelock refund
- Solver fee compensates risk
- Capital lock duration bounded

**Impact Scope:** Temporary capital inefficiency. No permanent loss.

---

#### C. Malicious Coordinator

**Capabilities:**
- Censor specific solvers
- Always select same solver
- Delay reselection intentionally

**Attack Goals:**
- Centralization
- Collusion
- Market manipulation

**Current Mitigations:**
- Non-custodial design
- Transparent winner announcement

**Future Mitigation:** On-chain decentralized auction

**Impact Scope:** Liveness degradation, market fairness distortion. No custody risk.

---

#### D. Bitcoin Reorg Risk

**Capabilities:**
- Chain reorganization after lock
- Confirmation reversal

**Mitigation:**
- Configurable confirmation depth
- Settlement only after threshold

**Impact Scope:** Delayed settlement. Low-probability double-spend risk (bounded).

---

### 9.3 Attack Surface Summary

| Surface | Risk | Protection |
|---|---|---|
| Bid manipulation | Low | Sealed-bid model |
| Capital oversubscription | Medium | Capital manager enforcement |
| Preimage leakage | Critical | Preimage revealed only after settlement |
| Timeout griefing | Medium | Timelock reclaim |
| Coordinator bias | High (liveness) | Documented trust assumption |

---

### 9.4 Safety vs Liveness Separation

This protocol explicitly separates:

**Safety** — Enforced cryptographically (HTLC + timelock)

**Liveness** — Dependent on coordinator honesty and solver responsiveness

Even under adversarial conditions: **funds remain safe, settlement may slow.**

This distinction is intentional.

---

### 9.5 Out-of-Scope Threats

The simulator does not model:

- Network-level eclipse attacks
- Miner extractable value (MEV)
- Deep Bitcoin reorgs (> confirmation threshold)
- EVM consensus failures
- Private key compromise

These are external to protocol logic.
