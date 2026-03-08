from bridge.intent import Intent
from bridge.solver import Solver
from bridge.coordinator import Coordinator
from bitcoin.confirmation import ConfirmationTracker


def main():
    solvers = [
        Solver("S1", capital=10, fee_rate=0.01),
        Solver("S2", capital=5, fee_rate=0.005),
        Solver("S3", capital=20, fee_rate=0.02),
    ]

    coordinator = Coordinator(solvers)

    intent = Intent(
        user_address="user_abc",
        source_amount_btc=4,
        max_fee=0.1
    )

    print("Created:", intent)

    winner = coordinator.select_winner(intent)

    print("Final Intent State:", intent)
    print("Winning Solver:", winner)
    print("HTLC:", intent.htlc)
    print(f"Solver remaining capital: {winner.capital_manager.available_capital}")

    tracker = ConfirmationTracker(required_confirmations=3, block_time_seconds=2)
    confirmed = tracker.wait_for_confirmations(intent.htlc)

    if confirmed:
        print(f"\nBitcoin finality reached. {tracker}")
    else:
        print("\nHTLC expired. Settlement aborted.")


if __name__ == "__main__":
    main()