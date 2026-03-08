from bridge.intent import IntentState


VALID_TRANSITIONS = {
    IntentState.CREATED: [IntentState.QUOTED, IntentState.EXPIRED],
    IntentState.QUOTED: [IntentState.WINNER_SELECTED, IntentState.EXPIRED],
    IntentState.WINNER_SELECTED: [IntentState.BTC_LOCKED, IntentState.QUOTED, IntentState.EXPIRED],
    IntentState.BTC_LOCKED: [IntentState.SETTLED, IntentState.EXPIRED],
    IntentState.SETTLED: [],
    IntentState.EXPIRED: [],
}


class InvalidTransition(Exception):
    pass


def transition(intent, new_state):
    allowed = VALID_TRANSITIONS.get(intent.state, [])

    if new_state not in allowed:
        raise InvalidTransition(
            f"Invalid transition: {intent.state.value} → {new_state.value}"
        )

    intent.state = new_state