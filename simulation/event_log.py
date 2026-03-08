import time


class Event:
    def __init__(self, event_type, data=None):
        self.event_type = event_type
        self.timestamp = time.time()
        self.data = data or {}

    def __repr__(self):
        return f"Event({self.event_type}, {self.data})"


class EventLog:
    def __init__(self):
        self.events = []

    def record(self, event_type, data=None):
        event = Event(event_type, data)
        self.events.append(event)
        return event

    def get_by_type(self, event_type):
        return [e for e in self.events if e.event_type == event_type]

    def summary(self):
        print("\n" + "="*50)
        print("EVENT LOG SUMMARY")
        print("="*50)

        counts = {}
        for event in self.events:
            counts[event.event_type] = counts.get(event.event_type, 0) + 1

        for event_type, count in counts.items():
            print(f"  {event_type}: {count}")

        print(f"\nTotal events recorded: {len(self.events)}")
        print("="*50)

    def __repr__(self):
        return f"EventLog(events={len(self.events)})"