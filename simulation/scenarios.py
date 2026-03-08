from bridge.intent import Intent, IntentState
from bridge.solver import Solver
from bridge.coordinator import Coordinator
from bridge.settlement import SettlementContract
from bridge.timeout import TimeoutHandler
from bitcoin.confirmation import ConfirmationTracker


def scenario_no_valid_bids():
    print("\n" + "="*50)
    print("SCENARIO: No Valid Bids — Capital Exhaustion")
    print("="*50)

    solvers = [
        Solver("S1", capital=1, fee_rate=0.01),
        Solver("S2", capital=2, fee_rate=0.005),
    ]

    coordinator = Coordinator(solvers)
    intent = Intent(user_address="user_abc", source_amount_btc=4, max_fee=0.1)

    print("Created:", intent)
    winner = coordinator.select_winner(intent)

    print(f"Final Intent State: {intent}")


def scenario_solver_offline_reselection():
    print("\n" + "="*50)
    print("SCENARIO: Solver Offline — Reselection")
    print("="*50)

    solvers = [
        Solver("S1", capital=10, fee_rate=0.01),
        Solver("S2", capital=5, fee_rate=0.005),
        Solver("S3", capital=20, fee_rate=0.02),
    ]

    coordinator = Coordinator(solvers)
    intent = Intent(user_address="user_abc", source_amount_btc=4, max_fee=0.1)

    print("Created:", intent)

    bids = coordinator.collect_bids(intent)
    winner_bid = min(bids, key=lambda x: x["fee"])
    winner = winner_bid["solver"]

    intent.state = IntentState.WINNER_SELECTED
    intent.winning_solver = winner
    print(f"Winner selected: Solver {winner.solver_id}")

    print(f"\nSimulating Solver {winner.solver_id} going offline...")

    timeout_handler = TimeoutHandler()
    timeout_handler.handle_lock_timeout(intent, coordinator)

    print(f"\nFinal Intent State: {intent}")
    if intent.winning_solver:
        print(f"New Winning Solver: {intent.winning_solver.solver_id}")


def scenario_coordinator_censorship():
    print("\n" + "="*50)
    print("SCENARIO: Coordinator Censorship")
    print("="*50)

    class BiasedCoordinator(Coordinator):
        def collect_bids(self, intent):
            bids = super().collect_bids(intent)
            censored = [b for b in bids if b["solver"].solver_id != "S2"]
            print(f"[CENSORSHIP] S2 censored. "
                  f"Remaining bidders: "
                  f"{[b['solver'].solver_id for b in censored]}")
            return censored

    solvers = [
        Solver("S1", capital=10, fee_rate=0.01),
        Solver("S2", capital=5, fee_rate=0.005),
        Solver("S3", capital=20, fee_rate=0.02),
    ]

    coordinator = BiasedCoordinator(solvers)
    intent = Intent(user_address="user_abc", source_amount_btc=4, max_fee=0.1)

    print("Created:", intent)
    winner = coordinator.select_winner(intent)

    print(f"\nFinal Intent State: {intent}")
    if winner:
        print(f"Winner (without S2): {winner.solver_id}")
        print("Note: S2 had the lowest fee but was censored.")


def scenario_all_solvers_exhausted():
    print("\n" + "="*50)
    print("SCENARIO: All Solvers Capital Exhausted")
    print("="*50)

    solvers = [
        Solver("S1", capital=10, fee_rate=0.01),
        Solver("S2", capital=5, fee_rate=0.005),
    ]

    print("Locking all solver capital with previous intents...")
    solvers[0].capital_manager.lock(10)
    solvers[1].capital_manager.lock(5)

    print(f"S1 capital: {solvers[0].capital_manager.available_capital}")
    print(f"S2 capital: {solvers[1].capital_manager.available_capital}")

    coordinator = Coordinator(solvers)
    intent = Intent(user_address="user_abc", source_amount_btc=4, max_fee=0.1)

    print("\nCreated:", intent)
    winner = coordinator.select_winner(intent)

    print(f"Final Intent State: {intent}")