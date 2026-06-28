import pyodbc
import random
import string
from datetime import datetime

def get_connection():
    return pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=bus_reservation;"
        "Trusted_Connection=yes;"
    )

def ensure_schema():
    """Schema already applied via schema_update.sql ΓÇö safe no-op."""
    pass

def add_user_id_to_bookings():
    """Add user_id column to bookings if missing."""
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME='bookings' AND COLUMN_NAME='user_id'
        )
        ALTER TABLE bookings ADD user_id INT NULL
    """)
    conn.commit(); conn.close()

def sync_seats_from_bookings():
    """Sync seats.is_booked from actual confirmed bookings ΓÇö fixes seeded data."""
    conn = get_connection(); cursor = conn.cursor()
    # Reset all seats to not booked
    cursor.execute("UPDATE seats SET is_booked=0")
    # Mark booked for all confirmed/waitlisted bookings that have a seat_id
    cursor.execute("""
        UPDATE seats SET is_booked=1
        WHERE id IN (
            SELECT seat_id FROM bookings
            WHERE seat_id IS NOT NULL
              AND status IN ('confirmed')
        )
    """)
    conn.commit(); conn.close()

def _rows(cursor):
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]

def _gen_ref(prefix, length=10):
    return prefix + ''.join(random.choices(string.ascii_uppercase+string.digits, k=length))

# ΓöÇΓöÇ AUTH ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
ADMIN_USERNAME   = "Maheen"
ADMIN_PASSWORD   = "maple"
MANAGER_USERNAME = "Kinza"
MANAGER_PASSWORD = "maple"

def login_user(username, password, role):
    # Hardcoded admin
    if role == "admin":
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return {"id":0,"username":ADMIN_USERNAME,"role":"admin","email":"admin@busres.com"}
        return None
    # Hardcoded manager
    if role == "manager":
        if username == MANAGER_USERNAME and password == MANAGER_PASSWORD:
            return {"id":-1,"username":MANAGER_USERNAME,"role":"manager","email":"manager@busres.com"}
        return None
    # DB passengers
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND role = ?",
                   (username, role))
    row = cursor.fetchone()
    conn.close()
    if row:
        cols = [c[0] for c in cursor.description]
        user = dict(zip(cols, row))
        if user["password"] != password:
            return None
        return user
    return None

def create_user(username, password, role, email=""):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close(); return False, "Username already taken."
    cursor.execute(
        "INSERT INTO users (username,password,role,email) OUTPUT INSERTED.id VALUES (?,?,?,?)",
        (username, password, role, email))
    uid = cursor.fetchone()[0]
    conn.commit(); conn.close()
    return True, {"id":uid,"username":username,"role":role,"email":email}

def change_password(user_id, role, current_pw, new_pw):
    if role == "admin":
        if current_pw != ADMIN_PASSWORD: return False, "Current password incorrect."
        return True, ""
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    if not row or row[0] != current_pw:
        conn.close(); return False, "Current password incorrect."
    cursor.execute("UPDATE users SET password=? WHERE id=?", (new_pw, user_id))
    conn.commit(); conn.close(); return True, ""

def get_all_users():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT id,username,role,email,created_at FROM users ORDER BY role,username")
    result = _rows(cursor); conn.close(); return result

def delete_user(user_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit(); conn.close()

# ΓöÇΓöÇ BUSES ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
def get_all_buses():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM buses ORDER BY id")
    result = _rows(cursor); conn.close(); return result

def get_buses_with_stats():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, b.bus_number, b.route, b.departure_time,
               b.total_seats, ISNULL(b.price,1500) AS price,
               COUNT(CASE WHEN s.is_booked=1 THEN 1 END) AS booked,
               b.total_seats-COUNT(CASE WHEN s.is_booked=1 THEN 1 END) AS available
        FROM buses b LEFT JOIN seats s ON s.bus_id=b.id
        GROUP BY b.id,b.bus_number,b.route,b.departure_time,b.total_seats,b.price
        ORDER BY b.id
    """)
    result = _rows(cursor); conn.close(); return result

def get_seats_for_bus(bus_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM seats WHERE bus_id=?", (bus_id,))
    result = _rows(cursor); conn.close(); return result

def add_bus(bus_number, route, departure_time, total_seats, price=1500):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO buses (bus_number,route,departure_time,total_seats,price) "
        "OUTPUT INSERTED.id VALUES (?,?,?,?,?)",
        (bus_number, route, departure_time, total_seats, price))
    bid = cursor.fetchone()[0]
    for sn in range(1, total_seats+1):
        cursor.execute("INSERT INTO seats (bus_id,seat_number,is_booked) VALUES (?,?,0)", (bid,sn))
    conn.commit(); conn.close(); return bid

def update_bus(bus_id, bus_number, route, departure_time, total_seats, price):
    conn = get_connection(); cursor = conn.cursor()
    # Get current seat count
    cursor.execute("SELECT COUNT(*) FROM seats WHERE bus_id=?", (bus_id,))
    current_seats = cursor.fetchone()[0]
    # Add missing seats if total increased
    if total_seats > current_seats:
        for sn in range(current_seats + 1, total_seats + 1):
            cursor.execute(
                "INSERT INTO seats (bus_id,seat_number,is_booked) VALUES (?,?,0)",
                (bus_id, sn))
    cursor.execute(
        "UPDATE buses SET bus_number=?,route=?,departure_time=?,total_seats=?,price=? WHERE id=?",
        (bus_number, route, departure_time, total_seats, price, bus_id))
    conn.commit(); conn.close()

def delete_bus(bus_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("DELETE FROM payments WHERE booking_id IN (SELECT id FROM bookings WHERE seat_id IN (SELECT id FROM seats WHERE bus_id=?))",(bus_id,))
    cursor.execute("DELETE FROM bookings WHERE seat_id IN (SELECT id FROM seats WHERE bus_id=?)",(bus_id,))
    cursor.execute("DELETE FROM seats WHERE bus_id=?", (bus_id,))
    cursor.execute("DELETE FROM buses WHERE id=?", (bus_id,))
    conn.commit(); conn.close()

# ΓöÇΓöÇ PASSENGERS ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
def add_passenger(name, cnic, email, phone):
    conn = get_connection(); cursor = conn.cursor()
    # If passenger with this CNIC already exists, return their id
    cursor.execute("SELECT id FROM passengers WHERE cnic=?", (cnic,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row[0]
    # Otherwise insert new passenger
    cursor.execute(
        "INSERT INTO passengers (name,cnic,email,phone) OUTPUT INSERTED.id VALUES (?,?,?,?)",
        (name, cnic, email, phone))
    pid = cursor.fetchone()[0]; conn.commit(); conn.close(); return pid

def get_passenger_by_cnic(cnic):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.cnic, p.email, p.phone, MAX(b.user_id) as user_id 
        FROM passengers p
        LEFT JOIN bookings b ON b.passenger_id = p.id
        WHERE p.cnic = ?
        GROUP BY p.id, p.name, p.cnic, p.email, p.phone
    """, (cnic,))
    row = cursor.fetchone(); conn.close()
    if row:
        cols = [c[0] for c in cursor.description]
        return dict(zip(cols, row))
    return None

def get_passenger_id_by_name(name):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT id FROM passengers WHERE name=?", (name,))
    row = cursor.fetchone(); conn.close()
    return row[0] if row else None

# ΓöÇΓöÇ BOOKINGS ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
def book_seat(passenger_id, seat_id, user_id=None, cnic=None):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("UPDATE seats SET is_booked=1 WHERE id=?", (seat_id,))
    cursor.execute(
        "INSERT INTO bookings (passenger_id,seat_id,status,user_id) OUTPUT INSERTED.id VALUES (?,?,'confirmed',?)",
        (passenger_id, seat_id, user_id))
    bid = cursor.fetchone()[0]; 
    conn.commit(); conn.close(); return bid

def cancel_booking(booking_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT seat_id FROM bookings WHERE id=?", (booking_id,))
    row = cursor.fetchone()
    if row and row[0]:
        cursor.execute("UPDATE seats SET is_booked=0 WHERE id=?", (row[0],))
    cursor.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,))
    conn.commit(); conn.close()

def update_booking_status(booking_id, new_status):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT seat_id FROM bookings WHERE id=?", (booking_id,))
    row = cursor.fetchone()
    if row and row[0]:
        if new_status == "cancelled":
            cursor.execute("UPDATE seats SET is_booked=0 WHERE id=?", (row[0],))
        elif new_status == "confirmed":
            cursor.execute("UPDATE seats SET is_booked=1 WHERE id=?", (row[0],))
    cursor.execute("UPDATE bookings SET status=? WHERE id=?", (new_status, booking_id))
    conn.commit(); conn.close()

def get_all_bookings():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, p.name, p.cnic,
               COALESCE(CAST(s.seat_number AS VARCHAR),'N/A') AS seat_number,
               COALESCE(bu.bus_number,
                   (SELECT bus_number FROM buses WHERE id=b.bus_id_override),'N/A') AS bus_number,
               b.booking_date, b.status
        FROM bookings b
        JOIN passengers p ON b.passenger_id=p.id
        LEFT JOIN seats s ON b.seat_id=s.id
        LEFT JOIN buses bu ON s.bus_id=bu.id
        ORDER BY b.id
    """)
    result = _rows(cursor); conn.close(); return result

def get_bookings_for_user(user_id):
    """Get bookings directly by user_id ΓÇö most reliable method."""
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id,
               COALESCE(bu.bus_number, 'N/A')  AS bus_number,
               COALESCE(bu.route, 'N/A')        AS route,
               b.booking_date, b.status,
               COALESCE(CAST(s.seat_number AS VARCHAR),'N/A') AS seat_number,
               ISNULL(pm.promo_code,'')          AS promo_code,
               ISNULL(pm.amount_paid, 1500)      AS amount_paid,
               p.name AS passenger_name
        FROM bookings b
        JOIN passengers p   ON b.passenger_id = p.id
        LEFT JOIN seats s   ON b.seat_id      = s.id
        LEFT JOIN buses bu  ON s.bus_id        = bu.id
        LEFT JOIN payments pm ON pm.booking_id = b.id
        WHERE b.user_id = ?
          AND b.status != 'waitlisted'
        ORDER BY b.id DESC
    """, (user_id,))
    result = _rows(cursor); conn.close(); return result

def get_waitlist_for_user(user_id):
    """Get waitlist entries directly by user_id."""
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id,
               COALESCE(bu.bus_number,
                   (SELECT bus_number FROM buses WHERE id=b.bus_id_override),'N/A') AS bus_number,
               COALESCE(bu.route,
                   (SELECT route FROM buses WHERE id=b.bus_id_override),'N/A') AS route,
               b.booking_date,
               ROW_NUMBER() OVER (PARTITION BY b.bus_id_override ORDER BY b.id) AS position
        FROM bookings b
        JOIN passengers p ON b.passenger_id = p.id
        LEFT JOIN buses bu ON bu.id = b.bus_id_override
        WHERE b.user_id = ? AND b.status = 'waitlisted'
        ORDER BY b.id
    """, (user_id,))
    result = _rows(cursor); conn.close(); return result

def get_bookings_for_passenger(passenger_name):
    """Match by exact name OR partial name (case-insensitive) for flexibility."""
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, bu.bus_number, bu.route, b.booking_date, b.status,
               COALESCE(CAST(s.seat_number AS VARCHAR),'N/A') AS seat_number,
               ISNULL(pm.promo_code,'')     AS promo_code,
               ISNULL(pm.amount_paid,1500)  AS amount_paid,
               p.name AS passenger_name,
               p.cnic AS cnic
        FROM bookings b
        JOIN passengers p  ON b.passenger_id=p.id
        LEFT JOIN seats s  ON b.seat_id=s.id
        LEFT JOIN buses bu ON s.bus_id=bu.id
        LEFT JOIN payments pm ON pm.booking_id=b.id
        WHERE (p.name=? OR p.cnic=?)
          AND b.status != 'waitlisted'
        ORDER BY b.id DESC
    """, (passenger_name, passenger_name))
    result = _rows(cursor); conn.close(); return result

def get_bookings_for_passenger_by_cnic(cnic):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, bu.bus_number, bu.route, b.booking_date, b.status,
               COALESCE(CAST(s.seat_number AS VARCHAR),'N/A') AS seat_number,
               ISNULL(pm.promo_code,'')     AS promo_code,
               ISNULL(pm.amount_paid,1500)  AS amount_paid,
               p.name AS passenger_name,
               p.cnic AS cnic
        FROM bookings b
        JOIN passengers p  ON b.passenger_id=p.id
        LEFT JOIN seats s  ON b.seat_id=s.id
        LEFT JOIN buses bu ON s.bus_id=bu.id
        LEFT JOIN payments pm ON pm.booking_id=b.id
        WHERE p.cnic=?
          AND b.status != 'waitlisted'
        ORDER BY b.id DESC
    """, (cnic,))
    result = _rows(cursor); conn.close(); return result

# ΓöÇΓöÇ WAITLIST ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
def add_waitlist_booking(passenger_id, bus_id, user_id=None):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bookings (passenger_id,seat_id,bus_id_override,status,user_id) "
        "OUTPUT INSERTED.id VALUES (?,NULL,?,'waitlisted',?)",
        (passenger_id, bus_id, user_id))
    bid = cursor.fetchone()[0]; conn.commit(); conn.close(); return bid

def serve_waitlist_booking(booking_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id,b.passenger_id,b.bus_id_override,p.name,p.cnic,p.phone
        FROM bookings b JOIN passengers p ON b.passenger_id=p.id WHERE b.id=?
    """, (booking_id,))
    row = cursor.fetchone()
    if not row: conn.close(); return None
    bus_id = row[2]
    cursor.execute(
        "SELECT TOP 1 id,seat_number FROM seats WHERE bus_id=? AND is_booked=0 ORDER BY seat_number",
        (bus_id,))
    seat = cursor.fetchone()
    if not seat: conn.close(); return None
    cursor.execute("UPDATE seats SET is_booked=1 WHERE id=?", (seat[0],))
    cursor.execute("UPDATE bookings SET seat_id=?,status='confirmed' WHERE id=?", (seat[0],booking_id))
    conn.commit()
    cursor.execute("""
        SELECT b.id,p.name,p.cnic,s.seat_number,bu.bus_number,b.booking_date,b.status
        FROM bookings b JOIN passengers p ON b.passenger_id=p.id
        JOIN seats s ON b.seat_id=s.id JOIN buses bu ON s.bus_id=bu.id WHERE b.id=?
    """, (booking_id,))
    result = cursor.fetchone(); cols=[c[0] for c in cursor.description]
    conn.close(); return dict(zip(cols,result)) if result else None

def get_waitlisted_bookings():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id,b.passenger_id,b.bus_id_override AS bus_id,
               p.name,p.cnic,p.phone,COALESCE(bu.bus_number,'N/A') AS bus_number
        FROM bookings b JOIN passengers p ON b.passenger_id=p.id
        LEFT JOIN buses bu ON bu.id=b.bus_id_override
        WHERE b.status='waitlisted' ORDER BY b.id
    """)
    result = _rows(cursor); conn.close(); return result

def get_waitlist_for_passenger(passenger_name):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id,
               COALESCE(bu.bus_number,(SELECT bus_number FROM buses WHERE id=b.bus_id_override),'N/A') AS bus_number,
               COALESCE(bu.route,(SELECT route FROM buses WHERE id=b.bus_id_override),'N/A') AS route,
               b.booking_date,
               ROW_NUMBER() OVER (PARTITION BY b.bus_id_override ORDER BY b.id) AS position
        FROM bookings b JOIN passengers p ON b.passenger_id=p.id
        LEFT JOIN buses bu ON bu.id=b.bus_id_override
        WHERE p.name=? AND b.status='waitlisted' ORDER BY b.id
    """, (passenger_name,))
    result = _rows(cursor); conn.close(); return result

# ΓöÇΓöÇ PROMO CODES ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
def get_all_promo_codes():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM promo_codes ORDER BY id")
    result = _rows(cursor); conn.close(); return result

def validate_promo(code):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM promo_codes WHERE code=? AND active=1 AND used<max_uses",
        (code.upper(),))
    row = cursor.fetchone(); conn.close()
    if row:
        cols = [c[0] for c in cursor.description]
        return dict(zip(cols,row))
    return None

def use_promo(code):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("UPDATE promo_codes SET used=used+1 WHERE code=?", (code.upper(),))
    conn.commit(); conn.close()

def create_promo(code, discount_pct, max_uses):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO promo_codes (code,discount_pct,max_uses,used,active) VALUES (?,?,?,0,1)",
        (code.upper(), discount_pct, max_uses))
    conn.commit(); conn.close()

def toggle_promo(promo_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("UPDATE promo_codes SET active=1-active WHERE id=?", (promo_id,))
    conn.commit(); conn.close()

def delete_promo(promo_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("DELETE FROM promo_codes WHERE id=?", (promo_id,))
    conn.commit(); conn.close()

# ΓöÇΓöÇ PAYMENT METHODS ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
def get_payment_methods():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM payment_methods ORDER BY id")
    result = _rows(cursor); conn.close(); return result

def toggle_payment_method(method_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("UPDATE payment_methods SET enabled=1-enabled WHERE id=?", (method_id,))
    conn.commit(); conn.close()

# ΓöÇΓöÇ PAYMENTS ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
def record_payment(booking_id, amount_paid, original_price,
                   promo_code, discount_amt, method, method_detail=""):
    ticket_no  = _gen_ref("TKT-", 8)
    invoice_no = f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
    txn_ref    = _gen_ref("TXN-", 10)
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO payments
            (booking_id,amount_paid,original_price,promo_code,
             discount_amt,method,method_detail,ticket_no,invoice_no,txn_ref)
        OUTPUT INSERTED.id VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (booking_id, amount_paid, original_price, promo_code or None,
          discount_amt, method, method_detail, ticket_no, invoice_no, txn_ref))
    pid = cursor.fetchone()[0]; conn.commit(); conn.close()
    return {"payment_id":pid,"ticket_no":ticket_no,
            "invoice_no":invoice_no,"txn_ref":txn_ref}

def backfill_payments():
    """Create payment records for confirmed bookings that have none (seeded data)."""
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id FROM bookings b
        LEFT JOIN payments p ON p.booking_id = b.id
        WHERE b.status = 'confirmed' AND p.id IS NULL
    """)
    missing = [row[0] for row in cursor.fetchall()]
    import random, string
    from datetime import datetime
    def _ref(prefix, n=8):
        return prefix + ''.join(random.choices(string.ascii_uppercase+string.digits, k=n))
    for bid in missing:
        ticket_no  = _ref("TKT-")
        invoice_no = f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
        txn_ref    = _ref("TXN-", 10)
        cursor.execute("""
            INSERT INTO payments
                (booking_id,amount_paid,original_price,promo_code,
                 discount_amt,method,method_detail,ticket_no,invoice_no,txn_ref)
            VALUES (?,1500,1500,NULL,0,'Seeded Data','',?,?,?)
        """, (bid, ticket_no, invoice_no, txn_ref))
    conn.commit(); conn.close()
    return len(missing)

def get_payment_for_booking(booking_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments WHERE booking_id=?", (booking_id,))
    row = cursor.fetchone(); conn.close()
    if row:
        cols = [c[0] for c in cursor.description]
        return dict(zip(cols,row))
    return None

# ΓöÇΓöÇ ANALYTICS & REVENUE ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
def get_analytics_stats():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT
            (SELECT COUNT(*) FROM buses) AS total_buses,
            (SELECT COUNT(*) FROM bookings WHERE status IN ('confirmed','waitlisted')) AS total_bookings,
            (SELECT COUNT(DISTINCT route) FROM buses) AS active_routes,
            (SELECT ISNULL(CAST(100.0*SUM(CASE WHEN is_booked=1 THEN 1 ELSE 0 END)
             /NULLIF(COUNT(*),0) AS DECIMAL(5,1)),0) FROM seats) AS fill_rate
    """)
    row=cursor.fetchone(); cols=[c[0] for c in cursor.description]
    conn.close(); return dict(zip(cols,row))

def get_revenue_stats():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT ISNULL(SUM(pm.amount_paid),0) AS total_revenue, COUNT(pm.id) AS paid_bookings
        FROM payments pm JOIN bookings b ON pm.booking_id=b.id WHERE b.status='confirmed'
    """)
    row=cursor.fetchone(); cols=[c[0] for c in cursor.description]
    conn.close(); return dict(zip(cols,row))

def get_revenue_per_bus():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT bu.bus_number, COUNT(pm.id) AS bookings,
               ISNULL(SUM(pm.amount_paid),0) AS revenue
        FROM buses bu
        LEFT JOIN seats s ON s.bus_id=bu.id
        LEFT JOIN bookings bk ON bk.seat_id=s.id AND bk.status='confirmed'
        LEFT JOIN payments pm ON pm.booking_id=bk.id
        GROUP BY bu.id,bu.bus_number ORDER BY revenue DESC
    """)
    result=_rows(cursor); conn.close(); return result

def get_bookings_per_bus():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT bu.bus_number, COUNT(b.id) AS bookings
        FROM buses bu
        LEFT JOIN seats s ON s.bus_id=bu.id
        LEFT JOIN bookings b ON b.seat_id=s.id AND b.status='confirmed'
        GROUP BY bu.id,bu.bus_number ORDER BY bookings DESC
    """)
    result=_rows(cursor); conn.close(); return result

def get_bookings_per_route():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT bu.route, COUNT(b.id) AS bookings
        FROM buses bu
        LEFT JOIN seats s ON s.bus_id=bu.id
        LEFT JOIN bookings b ON b.seat_id=s.id AND b.status='confirmed'
        GROUP BY bu.route ORDER BY bookings DESC
    """)
    result=_rows(cursor); conn.close(); return result

# ΓöÇΓöÇ FEEDBACK ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
def submit_feedback(passenger_id, bus_id, rating, comment, booking_id=None):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT id FROM feedback WHERE passenger_id=? AND bus_id=?",
                   (passenger_id, bus_id))
    existing = cursor.fetchone()
    if existing:
        cursor.execute(
            "UPDATE feedback SET rating=?,comment=?,created_at=GETDATE() WHERE id=?",
            (rating, comment, existing[0]))
    else:
        cursor.execute(
            "INSERT INTO feedback (passenger_id,bus_id,booking_id,rating,comment) VALUES (?,?,?,?,?)",
            (passenger_id, bus_id, booking_id, rating, comment))
    conn.commit(); conn.close()

def get_feedback_for_passenger(passenger_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT f.id,bu.bus_number,bu.route,f.rating,f.comment,f.created_at
        FROM feedback f JOIN buses bu ON f.bus_id=bu.id
        WHERE f.passenger_id=? ORDER BY f.created_at DESC
    """, (passenger_id,))
    result=_rows(cursor); conn.close(); return result

def get_all_feedback():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT f.id,p.name AS passenger,bu.bus_number,bu.route,
               f.rating,f.comment,f.created_at
        FROM feedback f JOIN passengers p ON f.passenger_id=p.id
        JOIN buses bu ON f.bus_id=bu.id ORDER BY f.created_at DESC
    """)
    result=_rows(cursor); conn.close(); return result

def get_avg_rating_per_bus():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT bu.bus_number,bu.route,
               CAST(AVG(CAST(f.rating AS FLOAT)) AS DECIMAL(3,1)) AS avg_rating,
               COUNT(f.id) AS review_count
        FROM buses bu LEFT JOIN feedback f ON f.bus_id=bu.id
        GROUP BY bu.id,bu.bus_number,bu.route ORDER BY avg_rating DESC
    """)
    result=_rows(cursor); conn.close(); return result

def delete_feedback(feedback_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("DELETE FROM feedback WHERE id=?", (feedback_id,))
    conn.commit(); conn.close()

def get_passenger_id_by_user_id(user_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id FROM passengers p
        INNER JOIN bookings b ON b.passenger_id = p.id
        WHERE b.user_id = ?
    """, (user_id,))
    row = cursor.fetchone(); conn.close()
    return row[0] if row else None

def get_user_cnic(user_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT cnic FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone(); conn.close()
    return row[0] if row else None

def get_booking_by_id(booking_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, p.name, p.cnic,
               COALESCE(s.seat_number, 'N/A') as seat_number,
               COALESCE(bu.bus_number, 'N/A') as bus_number
        FROM bookings b
        JOIN passengers p ON p.id = b.passenger_id
        LEFT JOIN seats s ON s.id = b.seat_id
        LEFT JOIN buses bu ON bu.id = s.bus_id
        WHERE b.id = ?
    """, (booking_id,))
    row = cursor.fetchone()
    if not row:
        conn.close(); return None
    cols = [c[0] for c in cursor.description]
    conn.close(); return dict(zip(cols, row))

def is_seat_taken(seat_id, exclude_booking_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM bookings 
        WHERE seat_id=? AND status='confirmed' AND id != ?
    """, (seat_id, exclude_booking_id))
    count = cursor.fetchone()[0]; conn.close()
    return count > 0
