import time


class ConfirmationTracker:
    def __init__(self, required_confirmations=3, block_time_seconds=2):
        self.required_confirmations = required_confirmations
        self.block_time_seconds = block_time_seconds
        self.confirmations = 0

    def wait_for_confirmations(self, htlc):
        print(f"\nWaiting for {self.required_confirmations} confirmations...")

        while self.confirmations < self.required_confirmations:
            if htlc.is_expired():
                print("HTLC expired before confirmation threshold reached.")
                return False

            time.sleep(self.block_time_seconds)
            self.confirmations += 1
            print(f"Block mined. Confirmations: {self.confirmations}/{self.required_confirmations}")

        print(f"Confirmation threshold reached. Settlement can proceed.")
        return True

    def __repr__(self):
        return (
            f"ConfirmationTracker("
            f"confirmations={self.confirmations}/"
            f"{self.required_confirmations})"
        )