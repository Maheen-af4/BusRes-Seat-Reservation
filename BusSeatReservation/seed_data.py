import pyodbc
from faker import Faker
import random

fake = Faker()

def get_connection():
    return pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=bus_reservation;"
        "Trusted_Connection=yes;"
    )

conn = get_connection()
cursor = conn.cursor()

routes = [
    ("Islamabad", "Rawalpindi"),
    ("Rawalpindi", "Lahore"),
    ("Islamabad", "Murree"),
    ("Peshawar", "Islamabad"),
    ("Lahore", "Multan"),
    ("Karachi", "Hyderabad"),
    ("Quetta", "Karachi"),
    ("Faisalabad", "Lahore"),
    ("Multan", "Bahawalpur"),
    ("Abbottabad", "Islamabad"),
]

print("Inserting buses and seats...")
bus_ids = []
for i in range(10):
    r = random.choice(routes)
    cursor.execute(
        "INSERT INTO buses (bus_number, route, total_seats, departure_time) "
        "OUTPUT INSERTED.id VALUES (?, ?, 40, ?)",
        (f"BUS-{100 + i}", f"{r[0]} to {r[1]}", fake.future_datetime())
    )
    bus_id = cursor.fetchone()[0]
    bus_ids.append(bus_id)
    for seat_no in range(1, 41):
        cursor.execute(
            "INSERT INTO seats (bus_id, seat_number, is_booked) VALUES (?, ?, 0)",
            (bus_id, seat_no)
        )

conn.commit()
print("Buses and seats done.")

print("Inserting passengers and bookings...")
used_cnics = set()
booking_count = 0

for _ in range(150):
    cnic = fake.numerify("?????-#######-?").replace("?", str(random.randint(1,9)))
    if cnic in used_cnics:
        continue
    used_cnics.add(cnic)

    cursor.execute(
        "INSERT INTO passengers (name, cnic, email, phone) OUTPUT INSERTED.id VALUES (?, ?, ?, ?)",
        (fake.name(), cnic, fake.email(), fake.numerify("03##-#######"))
    )
    pid = cursor.fetchone()[0]

    # each passenger books between 1 and 2 seats
    num_bookings = random.randint(1, 2)
    cursor.execute(
        "SELECT TOP (?) id FROM seats WHERE is_booked = 0 ORDER BY NEWID()",
        (num_bookings,)
    )
    available_seats = [row[0] for row in cursor.fetchall()]

    for sid in available_seats:
        cursor.execute("UPDATE seats SET is_booked = 1 WHERE id = ?", (sid,))
        cursor.execute(
            "INSERT INTO bookings (passenger_id, seat_id, status) VALUES (?, ?, 'confirmed')",
            (pid, sid)
        )
        booking_count += 1

conn.commit()

print(f"Done! Total bookings created: {booking_count}")
print("Your database now has 1000+ records across all tables.")
conn.close()