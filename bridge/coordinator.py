from bridge.intent import IntentState
from bridge.state_machine import transition


class Coordinator:
    def __init__(self, solvers):
        self.solvers = solvers

    def collect_bids(self, intent):
        bids = []
        for solver in self.solvers:
            bid = solver.generate_bid(intent)
            if bid and bid["fee"] <= intent.max_fee:
                bids.append(bid)
        return bids

    def select_winner(self, intent):
        if intent.state != IntentState.QUOTED:
            transition(intent, IntentState.QUOTED)

        bids = self.collect_bids(intent)

        if not bids:
            print("No valid bids received. Intent expired.")
            transition(intent, IntentState.EXPIRED)
            return None

        winner_bid = min(bids, key=lambda x: x["fee"])
        winner = winner_bid["solver"]

        transition(intent, IntentState.WINNER_SELECTED)
        intent.winning_solver = winner

        print(f"Winner selected: Solver {winner.solver_id} "
              f"(fee={winner_bid['fee']:.4f})")

        winner.lock_btc(intent)
        return winner