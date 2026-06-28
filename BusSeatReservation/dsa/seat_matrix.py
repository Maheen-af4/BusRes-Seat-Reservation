class SeatMatrix:
    def __init__(self, rows=8, cols=5):
        self.rows = rows
        self.cols = cols
        self.matrix = [[0] * cols for _ in range(rows)]

    def book_seat(self, seat_number):
        row = (seat_number - 1) // self.cols
        col = (seat_number - 1) % self.cols
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if self.matrix[row][col] == 0:
                self.matrix[row][col] = 1
                return True
        return False

    def cancel_seat(self, seat_number):
        row = (seat_number - 1) // self.cols
        col = (seat_number - 1) % self.cols
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.matrix[row][col] = 0

    def is_available(self, seat_number):
        row = (seat_number - 1) // self.cols
        col = (seat_number - 1) % self.cols
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.matrix[row][col] == 0
        return False

    def get_all_available(self):
        available = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.matrix[r][c] == 0:
                    available.append(r * self.cols + c + 1)
        return available

    def display(self):
        print("Seat Matrix (0=Free, 1=Booked):")
        for row in self.matrix:
            print(row)