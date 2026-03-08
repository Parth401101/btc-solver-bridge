from economics.capital import CapitalManager
from bitcoin.htlc import HTLC
from bridge.intent import IntentState
from bridge.state_machine import transition


class Solver:
    def __init__(self, solver_id, capital, fee_rate):
        self.solver_id = solver_id
        self.capital_manager = CapitalManager(capital)
        self.fee_rate = fee_rate
        self.reputation_score = 100

    def can_bid(self, intent):
        return self.capital_manager.can_lock(intent.source_amount_btc)

    def generate_bid(self, intent):
        if not self.can_bid(intent):
            return None
        fee = intent.source_amount_btc * self.fee_rate
        return {
            "solver": self,
            "fee": fee
        }

    def lock_btc(self, intent):
        if not self.capital_manager.can_lock(intent.source_amount_btc):
            raise ValueError("Insufficient capital to lock")

        self.capital_manager.lock(intent.source_amount_btc)
        htlc = HTLC(intent.source_amount_btc)

        transition(intent, IntentState.BTC_LOCKED)
        intent.htlc = htlc

        print(f"Solver {self.solver_id} locked BTC: {htlc}")
        return htlc

    def __repr__(self):
        return (
            f"Solver(id={self.solver_id}, "
            f"capital={self.capital_manager.available_capital}, "
            f"fee_rate={self.fee_rate})"
        )