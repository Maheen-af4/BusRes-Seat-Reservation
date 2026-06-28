import csv
from database import get_all_bookings

def export_bookings_to_csv(filepath="D:\\BusSeatReservation\\bookings_export.csv"):
    bookings = get_all_bookings()
    if not bookings:
        return False
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=bookings[0].keys())
        writer.writeheader()
        writer.writerows(bookings)
    return True

def import_bookings_from_csv(filepath="D:\\BusSeatReservation\\bookings_export.csv"):
    records = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    except FileNotFoundError:
        return []
    return records
