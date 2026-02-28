from economics.capital import CapitalManager


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

    def __repr__(self):
        return f"Solver(id={self.solver_id}, capital={self.capital_manager.available_capital})"