"""
BusRes — Reset & Seed Script
=============================
Safely wipes and re-seeds:
  - passengers, bookings, seats, buses, payments, feedback

NEVER touches:
  - users (Maheen/Kinza hardcoded, Ali passenger account stays)
  - promo_codes
  - payment_methods

Run from D:\\BusSeatReservation:
    python reset_and_seed.py
"""

import pyodbc
import random
from datetime import datetime, timedelta

def get_connection():
    return pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=bus_reservation;"
        "Trusted_Connection=yes;"
    )

# ── Config ─────────────────────────────────────────────────────────────────
TOTAL_BUSES    = 25
SEATS_PER_BUS  = 40
TARGET_BOOKINGS = 224   # approx — some randomness expected

BUSES = [
    # Original 10
    ("BUS-100", "Islamabad to Rawalpindi",   "2026-06-03 02:37", 1500),
    ("BUS-101", "Rawalpindi to Lahore",      "2026-06-10 23:27", 1500),
    ("BUS-102", "Islamabad to Murree",       "2026-06-17 06:31", 1500),
    ("BUS-103", "Peshawar to Islamabad",     "2026-06-13 19:03", 1500),
    ("BUS-104", "Lahore to Multan",          "2026-06-08 15:13", 1500),
    ("BUS-105", "Karachi to Hyderabad",      "2026-06-22 11:11", 1500),
    ("BUS-106", "Quetta to Karachi",         "2026-05-29 04:34", 1500),
    ("BUS-107", "Faisalabad to Lahore",      "2026-06-05 18:35", 1500),
    ("BUS-108", "Multan to Bahawalpur",      "2026-05-28 08:04", 1500),
    ("BUS-109", "Abbottabad to Islamabad",   "2026-06-15 23:17", 1500),
    # 15 new buses — same routes, different numbers & times
    ("BUS-110", "Islamabad to Rawalpindi",   "2026-06-04 07:15", 1500),
    ("BUS-111", "Rawalpindi to Lahore",      "2026-06-11 14:30", 1500),
    ("BUS-112", "Islamabad to Murree",       "2026-06-18 09:00", 1500),
    ("BUS-113", "Peshawar to Islamabad",     "2026-06-14 06:45", 1500),
    ("BUS-114", "Lahore to Multan",          "2026-06-09 11:20", 1500),
    ("BUS-115", "Karachi to Hyderabad",      "2026-06-23 16:00", 1500),
    ("BUS-116", "Quetta to Karachi",         "2026-05-30 21:10", 1500),
    ("BUS-117", "Faisalabad to Lahore",      "2026-06-06 08:50", 1500),
    ("BUS-118", "Multan to Bahawalpur",      "2026-05-29 13:00", 1500),
    ("BUS-119", "Abbottabad to Islamabad",   "2026-06-16 17:45", 1500),
    ("BUS-120", "Islamabad to Peshawar",     "2026-06-07 05:30", 1500),
    ("BUS-121", "Lahore to Faisalabad",      "2026-06-12 10:15", 1500),
    ("BUS-122", "Karachi to Quetta",         "2026-06-20 22:00", 1500),
    ("BUS-123", "Multan to Lahore",          "2026-06-19 03:40", 1500),
    ("BUS-124", "Rawalpindi to Islamabad",   "2026-06-21 19:55", 1500),
]

FIRST_NAMES = [
    "Gloria","Kenneth","Frank","Amber","Taylor","Jesus","David","Sheryl",
    "Gregory","Carrie","Joseph","Katie","Renee","Melissa","Robert","Andrew",
    "Jimmy","Sarah","Hassan","Fatima","Usman","Ayesha","Bilal","Sana",
    "Omar","Zara","Ahmed","Maria","Ali","Hina","Tariq","Nadia","Imran",
    "Samina","Waqar","Sadia","Faisal","Rabia","Kamran","Mehwish"
]
LAST_NAMES = [
    "Miranda","Preston","Cervantes","Parker","Banks","Sparks","Pope","Cole",
    "Cruz","Aguirre","Donaldson","Klein","Wright","Moore","Farmer","Martin",
    "Figueroa","Khan","Ahmed","Malik","Hussain","Siddiqui","Chaudhry","Akhtar",
    "Sheikh","Ansari","Qureshi","Butt","Mirza","Rizvi","Javed","Nawaz"
]

def random_cnic(used):
    while True:
        c = f"{random.randint(10000,99999)}-{random.randint(1000000,9999999)}-{random.randint(1,9)}"
        if c not in used:
            used.add(c)
            return c

def random_phone():
    prefixes = ["0300","0301","0302","0303","0311","0312","0313","0321","0333","0345"]
    return f"{random.choice(prefixes)}-{random.randint(1000000,9999999)}"

def random_email(name):
    domains = ["gmail.com","yahoo.com","hotmail.com","outlook.com"]
    return f"{name.lower().replace(' ','.')}{random.randint(1,99)}@{random.choice(domains)}"

def random_date():
    base = datetime(2026, 5, 26, 21, 56, 57)
    return base + timedelta(milliseconds=random.randint(0, 86400000))

def main():
    conn   = get_connection()
    cursor = conn.cursor()

    print("=" * 55)
    print("  BusRes Reset & Seed")
    print("=" * 55)

    # ── Step 1: Wipe in safe order ──────────────────────────────────
    print("\n[1/5] Wiping existing data...")
    cursor.execute("DELETE FROM feedback")
    cursor.execute("DELETE FROM payments")
    cursor.execute("DELETE FROM bookings")
    cursor.execute("DELETE FROM seats")
    cursor.execute("DELETE FROM passengers")
    cursor.execute("DELETE FROM buses")
    # Reset identity counters
    for tbl in ["feedback","payments","bookings","seats","passengers","buses"]:
        try:
            cursor.execute(f"DBCC CHECKIDENT ('{tbl}', RESEED, 0)")
        except: pass
    conn.commit()
    print("   ✅ All records wiped. Users/Promos/PaymentMethods untouched.")

    # ── Step 2: Insert buses ────────────────────────────────────────
    print("\n[2/5] Inserting buses...")
    bus_ids = []
    for bus_num, route, dep, price in BUSES:
        cursor.execute(
            "INSERT INTO buses (bus_number,route,departure_time,total_seats,price) "
            "OUTPUT INSERTED.id VALUES (?,?,?,?,?)",
            (bus_num, route, dep, SEATS_PER_BUS, price))
        bus_ids.append(cursor.fetchone()[0])
    conn.commit()
    print(f"   ✅ {len(bus_ids)} buses inserted.")

    # ── Step 3: Insert seats ────────────────────────────────────────
    print("\n[3/5] Inserting seats...")
    seat_ids = {}   # bus_id -> [seat_id, ...]
    for bid in bus_ids:
        seat_ids[bid] = []
        for sn in range(1, SEATS_PER_BUS + 1):
            cursor.execute(
                "INSERT INTO seats (bus_id,seat_number,is_booked) "
                "OUTPUT INSERTED.id VALUES (?,?,0)",
                (bid, sn))
            seat_ids[bid].append(cursor.fetchone()[0])
    conn.commit()
    total_seats = sum(len(v) for v in seat_ids.values())
    print(f"   ✅ {total_seats} seats inserted ({SEATS_PER_BUS} per bus).")

    # ── Step 4: Insert passengers & bookings ────────────────────────
    print("\n[4/5] Inserting passengers & bookings...")

    # Distribute bookings — first 3 buses FULLY booked (40/40) for demo
    # remaining buses get 18-26 bookings each
    bookings_per_bus = {}
    # BUS-100,101,102 (idx 0,1,2) + BUS-110,117,118 (idx 10,17,18) = FULL
    full_indices = [0, 1, 2, 10, 17, 18]
    full_bus_ids = [bus_ids[i] for i in full_indices]
    for bid in full_bus_ids:
        bookings_per_bus[bid] = SEATS_PER_BUS   # 40/40 = FULL
    remaining = TARGET_BOOKINGS - (len(full_indices) * SEATS_PER_BUS)
    if remaining < 0: remaining = 0
    non_full = [bid for bid in bus_ids if bid not in full_bus_ids]
    for i, bid in enumerate(non_full):
        n = random.randint(5, 12)
        bookings_per_bus[bid] = min(n, SEATS_PER_BUS)

    used_cnics  = set()
    used_seats  = {bid: set() for bid in bus_ids}
    total_booked = 0

    for bid in bus_ids:
        count = bookings_per_bus[bid]
        available_seats = list(range(len(seat_ids[bid])))
        random.shuffle(available_seats)
        chosen_seat_indices = available_seats[:count]

        for idx in chosen_seat_indices:
            # Passenger
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            name  = f"{fname} {lname}"
            cnic  = random_cnic(used_cnics)
            phone = random_phone()
            email = random_email(name)

            cursor.execute(
                "INSERT INTO passengers (name,cnic,email,phone) "
                "OUTPUT INSERTED.id VALUES (?,?,?,?)",
                (name, cnic, email, phone))
            pid = cursor.fetchone()[0]

            # Booking
            actual_seat_id = seat_ids[bid][idx]
            bdate = random_date()
            cursor.execute(
                "INSERT INTO bookings (passenger_id,seat_id,status,booking_date) "
                "OUTPUT INSERTED.id VALUES (?,?,'confirmed',?)",
                (pid, actual_seat_id, bdate))
            booking_id = cursor.fetchone()[0]

            # Mark seat as booked
            cursor.execute("UPDATE seats SET is_booked=1 WHERE id=?", (actual_seat_id,))
            total_booked += 1

    conn.commit()
    print(f"   ✅ {total_booked} passengers & bookings inserted.")

    # ── Step 5: Backfill payments ───────────────────────────────────
    print("\n[5/5] Backfilling payment records...")
    cursor.execute("""
        SELECT b.id FROM bookings b
        LEFT JOIN payments p ON p.booking_id=b.id
        WHERE b.status='confirmed' AND p.id IS NULL
    """)
    missing = [r[0] for r in cursor.fetchall()]

    import string
    def _ref(prefix, n=8):
        return prefix + ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=n))

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
    conn.commit()
    print(f"   ✅ {len(missing)} payment records backfilled.")

    # ── Summary ─────────────────────────────────────────────────────
    cursor.execute("SELECT COUNT(*) FROM buses")       ; nb = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM passengers")  ; np = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM bookings")    ; nk = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM seats WHERE is_booked=1") ; ns = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM payments")    ; npy= cursor.fetchone()[0]
    conn.close()

    print("\n" + "=" * 55)
    print("  SEED COMPLETE")
    print("=" * 55)
    print(f"  Buses        : {nb}")
    print(f"  Passengers   : {np}")
    print(f"  Bookings     : {nk}")
    print(f"  Booked seats : {ns}")
    print(f"  Payments     : {npy}")
    print(f"\n  Users / Promos / Payment Methods : UNTOUCHED ✅")
    print("=" * 55)

if __name__ == "__main__":
    main()