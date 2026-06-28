from collections import deque

class WaitlistQueue:
    def __init__(self):
        self.queue = deque()

    def enqueue(self, passenger_data):
        self.queue.append(passenger_data)
        print(f"Added to waitlist: {passenger_data.get('name', 'Unknown')}")

    def dequeue(self):
        if self.queue:
            return self.queue.popleft()
        return None

    def peek(self):
        return self.queue[0] if self.queue else None

    def is_empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)

    def get_all(self):
        return list(self.queue)