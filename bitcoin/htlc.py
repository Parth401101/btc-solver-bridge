import hashlib
import time


class HTLC:
    def __init__(self, amount, timelock_seconds=30):
        self.amount = amount
        self.preimage = "supersecret"
        self.hashlock = hashlib.sha256(self.preimage.encode()).hexdigest()
        self.timelock = time.time() + timelock_seconds
        self.locked = True

    def is_expired(self):
        return time.time() > self.timelock

    def __repr__(self):
        return (
            f"HTLC(amount={self.amount}, "
            f"hashlock={self.hashlock[:8]}..., "
            f"expires_in={int(self.timelock - time.time())}s)"
        )