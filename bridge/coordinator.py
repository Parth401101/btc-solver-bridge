from bridge.intent import IntentState


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
        bids = self.collect_bids(intent)

        if not bids:
            print("No valid bids received.")
            return None

        # First-price sealed bid → lowest fee wins
        winner_bid = min(bids, key=lambda x: x["fee"])
        winner = winner_bid["solver"]

        intent.state = IntentState.WINNER_SELECTED
        intent.winning_solver = winner

        print(f"Winner selected: Solver {winner.solver_id}")
        return winner