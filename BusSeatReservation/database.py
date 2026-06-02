import pyodbc

def get_connection():
    return pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=bus_reservation;"
        "Trusted_Connection=yes;"
    )

def get_all_buses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM buses")
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return result

def get_seats_for_bus(bus_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seats WHERE bus_id = ?", (bus_id,))
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return result

def add_passenger(name, cnic, email, phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO passengers (name, cnic, email, phone) OUTPUT INSERTED.id VALUES (?, ?, ?, ?)",
        (name, cnic, email, phone)
    )
    pid = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return pid

def book_seat(passenger_id, seat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE seats SET is_booked = 1 WHERE id = ?", (seat_id,))
    cursor.execute(
        "INSERT INTO bookings (passenger_id, seat_id) VALUES (?, ?)",
        (passenger_id, seat_id)
    )
    conn.commit()
    conn.close()

def cancel_booking(booking_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT seat_id FROM bookings WHERE id = ?", (booking_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE seats SET is_booked = 0 WHERE id = ?", (row[0],))
        cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()

def get_all_bookings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, p.name, p.cnic, s.seat_number, bu.bus_number,
               b.booking_date, b.status
        FROM bookings b
        JOIN passengers p ON b.passenger_id = p.id
        JOIN seats s ON b.seat_id = s.id
        JOIN buses bu ON s.bus_id = bu.id
    """)
    columns = [col[0] for col in cursor.description]
    result = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return result

def get_passenger_by_cnic(cnic):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM passengers WHERE cnic = ?", (cnic,))
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    conn.close()
    return dict(zip(columns, row)) if row else None