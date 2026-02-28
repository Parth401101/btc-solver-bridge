class CapitalManager:
    def __init__(self, initial_capital):
        self.available_capital = initial_capital

    def can_lock(self, amount):
        return self.available_capital >= amount

    def lock(self, amount):
        if not self.can_lock(amount):
            raise ValueError("Insufficient capital")
        self.available_capital -= amount

    def release(self, amount):
        self.available_capital += amount