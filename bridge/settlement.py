from bridge.intent import IntentState


class SettlementContract:
    def __init__(self):
        self.settlements = []

    def settle(self, intent, tracker):
        if intent.state != IntentState.BTC_LOCKED:
            print("Settlement failed: Intent is not in BTC_LOCKED state.")
            return False

        if intent.htlc is None:
            print("Settlement failed: No HTLC found on intent.")
            return False

        if intent.htlc.is_expired():
            print("Settlement failed: HTLC has expired.")
            intent.state = IntentState.EXPIRED
            return False

        if tracker.confirmations < tracker.required_confirmations:
            print("Settlement failed: Confirmation threshold not reached.")
            return False

        intent.state = IntentState.SETTLED

        self.settlements.append({
            "intent_id": intent.intent_id,
            "solver_id": intent.winning_solver.solver_id,
            "amount": intent.htlc.amount,
        })

        print(f"\nSettlement confirmed.")
        print(f"User {intent.user_address} received {intent.htlc.amount} BTC equivalent.")
        print(f"Solver {intent.winning_solver.solver_id} earned fee.")

        return True

    def __repr__(self):
        return f"SettlementContract(total_settlements={len(self.settlements)})"