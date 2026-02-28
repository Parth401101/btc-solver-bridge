import uuid
from enum import Enum


class IntentState(Enum):
    CREATED = "CREATED"
    QUOTED = "QUOTED"
    WINNER_SELECTED = "WINNER_SELECTED"
    BTC_LOCKED = "BTC_LOCKED"

class Intent:
    def __init__(self, user_address, source_amount_btc, max_fee):
        self.intent_id = str(uuid.uuid4())
        self.user_address = user_address
        self.source_amount_btc = source_amount_btc
        self.max_fee = max_fee
        self.state = IntentState.CREATED
        self.winning_solver = None

    def __repr__(self):
        return (
            f"Intent(id={self.intent_id[:6]}, "
            f"amount={self.source_amount_btc}, "
            f"state={self.state.value})"
        )