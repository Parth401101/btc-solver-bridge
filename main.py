from bridge.intent import Intent, IntentState
from bridge.solver import Solver
from bridge.coordinator import Coordinator
from bridge.settlement import SettlementContract
from bridge.timeout import TimeoutHandler
from bitcoin.confirmation import ConfirmationTracker
from simulation.scenarios import (
    scenario_no_valid_bids,
    scenario_solver_offline_reselection,
    scenario_coordinator_censorship,
    scenario_all_solvers_exhausted,
)


def run_happy_path():
    print("\n" + "="*50)
    print("SCENARIO: Happy Path")
    print("="*50)

    solvers = [
        Solver("S1", capital=10, fee_rate=0.01),
        Solver("S2", capital=5, fee_rate=0.005),
        Solver("S3", capital=20, fee_rate=0.02),
    ]

    coordinator = Coordinator(solvers)
    intent = Intent(user_address="user_abc", source_amount_btc=4, max_fee=0.1)

    print("Created:", intent)
    winner = coordinator.select_winner(intent)

    tracker = ConfirmationTracker(required_confirmations=3, block_time_seconds=2)
    confirmed = tracker.wait_for_confirmations(intent.htlc)

    if confirmed:
        contract = SettlementContract()
        contract.settle(intent, tracker)
        print(f"\nFinal Intent State: {intent}")


def run_htlc_expiry():
    print("\n" + "="*50)
    print("SCENARIO: HTLC Expiry — User Griefing")
    print("="*50)

    solvers = [
        Solver("S1", capital=10, fee_rate=0.01),
        Solver("S2", capital=5, fee_rate=0.005),
    ]

    coordinator = Coordinator(solvers)
    intent = Intent(user_address="user_abc", source_amount_btc=4, max_fee=0.1)

    print("Created:", intent)
    winner = coordinator.select_winner(intent)

    print(f"\nSimulating HTLC expiry...")
    intent.htlc.timelock = 0

    timeout_handler = TimeoutHandler()
    reclaimed = timeout_handler.handle_htlc_expiry(intent)

    if reclaimed:
        print(f"\nFinal Intent State: {intent}")


if __name__ == "__main__":
    run_happy_path()
    run_htlc_expiry()
    scenario_no_valid_bids()
    scenario_solver_offline_reselection()
    scenario_coordinator_censorship()
    scenario_all_solvers_exhausted()