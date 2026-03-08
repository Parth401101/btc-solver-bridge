from bridge.intent import IntentState


class TimeoutHandler:
    def __init__(self, lock_timeout_seconds=10):
        self.lock_timeout_seconds = lock_timeout_seconds

    def handle_lock_timeout(self, intent, coordinator):
        if intent.state != IntentState.WINNER_SELECTED:
            return False

        print(f"\n[TIMEOUT] Solver {intent.winning_solver.solver_id} "
              f"failed to lock BTC in time.")

        intent.winning_solver.reputation_score -= 20
        print(f"[TIMEOUT] Reputation penalty applied. "
              f"New score: {intent.winning_solver.reputation_score}")

        intent.winning_solver = None
        intent.state = IntentState.QUOTED

        print(f"[TIMEOUT] Reselecting solver...")
        new_winner = coordinator.select_winner(intent)

        if new_winner is None:
            intent.state = IntentState.EXPIRED
            print(f"[TIMEOUT] No solvers available. Intent expired.")
            return False

        return True

    def handle_htlc_expiry(self, intent):
        if intent.state != IntentState.BTC_LOCKED:
            return False

        if not intent.htlc.is_expired():
            return False

        print(f"\n[TIMEOUT] HTLC expired. Solver reclaiming BTC...")

        intent.winning_solver.capital_manager.release(intent.htlc.amount)

        print(f"[TIMEOUT] Solver {intent.winning_solver.solver_id} "
              f"reclaimed {intent.htlc.amount} BTC.")
        print(f"[TIMEOUT] Solver capital restored: "
              f"{intent.winning_solver.capital_manager.available_capital}")

        intent.state = IntentState.EXPIRED
        intent.htlc.locked = False

        return True

    def __repr__(self):
        return f"TimeoutHandler(lock_timeout={self.lock_timeout_seconds}s)"