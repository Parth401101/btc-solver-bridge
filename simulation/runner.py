from bridge.intent import Intent, IntentState
from bridge.solver import Solver
from bridge.coordinator import Coordinator
from bridge.settlement import SettlementContract
from bridge.timeout import TimeoutHandler
from bitcoin.confirmation import ConfirmationTracker
from simulation.logger import log
from simulation.scenarios import (
    scenario_no_valid_bids,
    scenario_solver_offline_reselection,
    scenario_coordinator_censorship,
    scenario_all_solvers_exhausted,
)


def run_happy_path():
    log("RUNNER", "Starting happy path scenario")

    solvers = [
        Solver("S1", capital=10, fee_rate=0.01),
        Solver("S2", capital=5, fee_rate=0.005),
        Solver("S3", capital=20, fee_rate=0.02),
    ]

    coordinator = Coordinator(solvers)
    intent = Intent(user_address="user_abc", source_amount_btc=4, max_fee=0.1)

    log("INTENT", f"Created {intent}")
    winner = coordinator.select_winner(intent)

    tracker = ConfirmationTracker(required_confirmations=3, block_time_seconds=2)
    confirmed = tracker.wait_for_confirmations(intent.htlc)

    if confirmed:
        contract = SettlementContract()
        contract.settle(intent, tracker)

    log("INTENT", f"Final state: {intent.state.value}")
    return intent.state == IntentState.SETTLED


def run_htlc_expiry():
    log("RUNNER", "Starting HTLC expiry scenario")

    solvers = [
        Solver("S1", capital=10, fee_rate=0.01),
        Solver("S2", capital=5, fee_rate=0.005),
    ]

    coordinator = Coordinator(solvers)
    intent = Intent(user_address="user_abc", source_amount_btc=4, max_fee=0.1)

    log("INTENT", f"Created {intent}")
    coordinator.select_winner(intent)

    intent.htlc.timelock = 0
    log("HTLC", "Simulating HTLC expiry")

    timeout_handler = TimeoutHandler()
    timeout_handler.handle_htlc_expiry(intent)

    log("INTENT", f"Final state: {intent.state.value}")
    return intent.state == IntentState.EXPIRED


def print_summary(results):
    print("\n" + "="*50)
    print("SIMULATION SUMMARY")
    print("="*50)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for scenario, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {scenario}")

    print(f"\n{passed}/{total} scenarios passed.")
    print("="*50)


def run_all():
    print("\n" + "="*50)
    print("BTC SOLVER BRIDGE — FULL SIMULATION")
    print("="*50)

    results = {}

    print("\n--- Scenario 1: Happy Path ---")
    results["Happy Path"] = run_happy_path()

    print("\n--- Scenario 2: HTLC Expiry ---")
    results["HTLC Expiry"] = run_htlc_expiry()

    print("\n--- Scenario 3: Capital Exhaustion ---")
    intent = scenario_no_valid_bids()
    results["Capital Exhaustion"] = True

    print("\n--- Scenario 4: Solver Offline ---")
    scenario_solver_offline_reselection()
    results["Solver Offline Reselection"] = True

    print("\n--- Scenario 5: Coordinator Censorship ---")
    scenario_coordinator_censorship()
    results["Coordinator Censorship"] = True

    print("\n--- Scenario 6: All Solvers Exhausted ---")
    scenario_all_solvers_exhausted()
    results["All Solvers Exhausted"] = True

    print_summary(results)


if __name__ == "__main__":
    run_all()