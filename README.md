# 🚌 BusRes — Bus Seat Reservation System

A fully-featured desktop bus seat reservation system built in Python with tkinter, SQL Server, and 6 DSA implementations. Developed as a Data Structures & Algorithms project at Bahria University.

---

## 🖥️ Overview

BusRes is a 3-role desktop application that manages bus bookings, waitlists, payments, analytics, and route finding — all backed by real DSA implementations running in memory alongside a persistent SQL Server database.

| Role | Access |
|------|--------|
| 👑 Admin | Analytics, Revenue, Promo Codes, User Management, All Buses, Waitlist, Admin Panel |
| 🔧 Manager | Manage Buses, Add Bus, Feedback Monitor, Search, Route Finder |
| 🎫 Passenger | All Buses, Book a Seat, My Bookings, My Waitlist, Feedback, Route Finder |

---

## ✨ Features

- **Role-Based Access Control** — 3 completely different dashboards from one login screen
- **Book a Seat** — two-column layout with live bus list, CNIC validation, promo codes, payment flow
- **Waitlist System** — auto-joins waitlist when bus is full; admin serves next from queue
- **PDF Generation** — professional ticket and invoice PDFs generated on booking confirmation
- **Route Finder** — Dijkstra's shortest path + BFS traversal on a 19-city Pakistan road graph
- **Sort & Stats** — live Merge Sort vs Bubble Sort benchmarking on real booking data
- **Search Panel** — Hash Search O(1), Binary Search O(log n), BST Search O(log n)
- **Analytics Dashboard** — animated stat cards + bookings per bus/route bar charts
- **Revenue Tracking** — per-bus revenue sorted by bus number with bar chart
- **Input Validation** — regex + logical checks on every form in the system
- **Self-Healing Startup** — auto-fixes data inconsistencies on every launch

---

## 🧠 DSA Implementations

| Structure | File | Role |
|-----------|------|------|
| Hash Table | `dsa/searching.py` | O(1) booking lookup by ID |
| Binary Search Tree | `dsa/bst.py` | O(log n) passenger name search |
| FIFO Queue | `dsa/queue_waitlist.py` | Waitlist management in arrival order |
| Weighted Directed Graph | `dsa/graph.py` | Dijkstra + BFS on city graph |
| 2D Matrix | `dsa/seat_matrix.py` | Seat layout representation per bus |
| Merge Sort + Bubble Sort | `dsa/sorting.py` | Algorithm comparison with timing |

---

## 🗂️ Project Structure

```
BusSeatReservation/
│
├── main.py                  # UI classes + all panel methods + business logic
├── database.py              # All database functions (Data Access Layer)
├── file_handler.py          # CSV export
├── reset_and_seed.py        # Reset DB and seed with sample data
├── schema_update.sql        # SQL schema (run once in SSMS)
│
└── dsa/
    ├── __init__.py
    ├── searching.py         # BookingHashTable
    ├── bst.py               # PassengerBST
    ├── queue_waitlist.py    # WaitlistQueue
    ├── graph.py             # RouteGraph (Dijkstra + BFS)
    ├── seat_matrix.py       # SeatMatrix
    └── sorting.py           # Merge Sort + Bubble Sort comparison
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.x
- SQL Server Express
- SSMS (SQL Server Management Studio)

### Step 1 — Install dependencies
```bash
pip install pyodbc reportlab
```

### Step 2 — Set up the database
1. Open SSMS and connect to `localhost\SQLEXPRESS`
2. Create a new database called `bus_reservation`
3. Run `schema_update.sql` in SSMS to create all tables

### Step 3 — Seed sample data
```bash
python reset_and_seed.py
```
This creates 25 buses with bookings, payments, and 6 fully booked buses for testing.

### Step 4 — Run the app
```bash
python main.py
```

---

## 🔐 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | Maheen | maple |
| Manager | Kinza | maple |
| Passenger | Create via app | Your choice |

---

## 🏗️ Architecture

The system is organized across 6 layers:

```
Presentation Layer     →  main.py (tkinter UI)
Business Logic Layer   →  main.py (rules + validation)
Data Access Layer      →  database.py (all SQL)
Data Layer             →  SQL Server Express (9 tables)
DSA Layer              →  dsa/ package (6 structures)
File & Export Layer    →  file_handler.py + PDF functions
```

---

## 📦 Requirements

```
pyodbc
reportlab
tkinter (built into Python)
```

Create a `requirements.txt`:
```bash
pip freeze > requirements.txt
```

---

## 🗄️ Database Tables

`buses` · `seats` · `passengers` · `bookings` · `users` · `payments` · `feedback` · `promo_codes` · `payment_methods`

---

## 👩‍💻 Built With

- **Python 3** — core language
- **tkinter** — GUI framework
- **SQL Server Express** — database
- **pyodbc** — database connector
- **ReportLab** — PDF generation

---

## 🎓 Academic Context

**Course:** Data Structures and Algorithms  
**University:** Bahria University  
**Year:** 2025

DSA concepts demonstrated:
- ✅ Linear Data Structure — FIFO Queue
- ✅ Non-Linear Data Structures — BST + Weighted Graph
- ✅ Sorting with comparison — Merge Sort vs Bubble Sort
- ✅ Searching — Hash, Binary, BST
- ✅ Graph Algorithm — Dijkstra + BFS
- ✅ GUI — tkinter desktop application
- ✅ File Handling — CSV + PDF + SQL Server
- ✅ Database Connectivity — SQL Server via pyodbc

---

*Made with ☕ and way too many debugging sessions*