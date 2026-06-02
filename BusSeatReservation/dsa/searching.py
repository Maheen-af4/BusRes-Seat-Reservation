def binary_search(sorted_data, key, target):
    low, high = 0, len(sorted_data) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_data[mid][key]
        if str(mid_val) == str(target):
            return sorted_data[mid]
        elif str(mid_val) < str(target):
            low = mid + 1
        else:
            high = mid - 1
    return None

class BookingHashTable:
    def __init__(self, size=3000):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        return hash(str(key)) % self.size

    def insert(self, booking_id, booking_data):
        index = self._hash(booking_id)
        for item in self.table[index]:
            if item[0] == booking_id:
                item[1] = booking_data
                return
        self.table[index].append([booking_id, booking_data])

    def search(self, booking_id):
        index = self._hash(booking_id)
        for item in self.table[index]:
            if item[0] == booking_id:
                return item[1]
        return None

    def delete(self, booking_id):
        index = self._hash(booking_id)
        self.table[index] = [
            item for item in self.table[index]
            if item[0] != booking_id
        ]

    def get_all(self):
        all_items = []
        for bucket in self.table:
            for item in bucket:
                all_items.append(item[1])
        return all_items