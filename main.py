from bridge.intent import Intent
from bridge.solver import Solver
from bridge.coordinator import Coordinator


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


if __name__ == "__main__":
    main()