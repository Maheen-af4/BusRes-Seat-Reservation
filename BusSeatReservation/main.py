import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from database import (get_all_buses, get_seats_for_bus, book_seat,
                      add_passenger, cancel_booking, get_all_bookings)
from dsa.seat_matrix import SeatMatrix
from dsa.sorting import compare_sorts
from dsa.searching import BookingHashTable
from dsa.graph import RouteGraph
from dsa.bst import PassengerBST
from dsa.queue_waitlist import WaitlistQueue
from file_handler import export_bookings_to_csv, import_bookings_from_csv

WAITLIST_LOG = "D:\\BusSeatReservation\\waitlist_log.csv"

BG     = "#1a1a2e"
PANEL  = "#16213e"
ACCENT = "#0f3460"
GREEN  = "#00b894"
RED    = "#d63031"
WHITE  = "#e0e0e0"
YELLOW = "#fdcb6e"

# ── Password ─────────────────────────────────────────────────────────
ADMIN_PASSWORD = "admin123"   # change this to your preferred password

def _ask_password(parent, title="Password Required"):
    """
    Show a modal password dialog.
    Returns True if the correct password was entered, False otherwise.
    """
    result = {"ok": False}

    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.configure(bg=PANEL)
    dlg.resizable(False, False)
    dlg.grab_set()

    # Centre on parent
    parent.update_idletasks()
    px = parent.winfo_x() + parent.winfo_width() // 2
    py = parent.winfo_y() + parent.winfo_height() // 2
    dlg.geometry(f"360x200+{px - 180}+{py - 100}")

    tk.Label(dlg, text="🔒  Access Restricted",
             bg=PANEL, fg=WHITE,
             font=("Segoe UI", 14, "bold")).pack(pady=(22, 4))
    tk.Label(dlg, text="Enter admin password to continue:",
             bg=PANEL, fg=YELLOW,
             font=("Segoe UI", 10)).pack()

    pw_var = tk.StringVar()
    pw_e = tk.Entry(dlg, textvariable=pw_var,
                    show="*", font=("Segoe UI", 12),
                    bg=ACCENT, fg=WHITE,
                    insertbackground=WHITE, width=28)
    pw_e.pack(pady=10, ipady=5)
    pw_e.focus_set()

    err_lbl = tk.Label(dlg, text="", bg=PANEL, fg=RED,
                       font=("Segoe UI", 9))
    err_lbl.pack()

    def _confirm(event=None):
        if pw_var.get() == ADMIN_PASSWORD:
            result["ok"] = True
            dlg.destroy()
        else:
            err_lbl.config(text="❌  Incorrect password. Try again.")
            pw_var.set("")

    def _cancel():
        dlg.destroy()

    btn_row = tk.Frame(dlg, bg=PANEL)
    btn_row.pack(pady=6)
    tk.Button(btn_row, text="Confirm", bg=GREEN, fg="white",
              font=("Segoe UI", 10, "bold"), width=10,
              cursor="hand2", command=_confirm).pack(side="left", padx=6)
    tk.Button(btn_row, text="Cancel", bg=RED, fg="white",
              font=("Segoe UI", 10, "bold"), width=10,
              cursor="hand2", command=_cancel).pack(side="left", padx=6)

    pw_e.bind("<Return>", _confirm)
    dlg.wait_window()
    return result["ok"]


class BusReservationApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Bus Seat Reservation System — Bahria University DSA Project")
        self.geometry("1150x720")
        self.configure(bg=BG)
        self.resizable(True, True)

        self.hash_table    = BookingHashTable()
        self.passenger_bst = PassengerBST()
        self.waitlist      = WaitlistQueue()
        self.route_graph   = RouteGraph()

        self._load_hash_table()
        self._load_bst()
        self._setup_routes()
        self._build_sidebar()
        self._build_main_area()
        self.show_dashboard()

    # ── Data loaders ────────────────────────────────────────────
    def _load_hash_table(self):
        for b in get_all_bookings():
            self.hash_table.insert(b["id"], b)

    def _load_bst(self):
        for b in get_all_bookings():
            self.passenger_bst.insert(b["name"], b)

    def _setup_routes(self):
        stops = [
            ("Islamabad",  "Rawalpindi", 15),
            ("Rawalpindi", "Taxila",     35),
            ("Taxila",     "Attock",     45),
            ("Islamabad",  "Murree",     60),
            ("Murree",     "Abbottabad", 55),
            ("Rawalpindi", "Murree",     50),
            ("Islamabad",  "Peshawar",  170),
            ("Lahore",     "Multan",    330),
            ("Karachi",    "Hyderabad", 160),
            ("Rawalpindi", "Lahore",    375),
        ]
        for f, t, d in stops:
            self.route_graph.add_route(f, t, d)

    # ── Layout ──────────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=ACCENT, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="🚌  BusRes",
                 bg=ACCENT, fg=WHITE,
                 font=("Segoe UI", 17, "bold")).pack(pady=28)
        tk.Label(self.sidebar, text="Bahria University",
                 bg=ACCENT, fg=YELLOW,
                 font=("Segoe UI", 8)).pack()
        tk.Frame(self.sidebar, bg=WHITE, height=1).pack(fill="x", pady=12)

        nav = [
            ("🏠   Dashboard",    self.show_dashboard),
            ("🎫   Book Seat",     self.show_booking),
            ("🔍   Search",        self.show_search),
            ("🗺   Route Finder",  self.show_routes),
            ("📊   Sort & Stats",  self.show_sort_stats),
            ("⏳   Waitlist",      self._open_waitlist_guarded),
            ("📁   Export CSV",    self._export_csv),
            ("⚙   Admin Panel",   self._open_admin_guarded),
        ]
        for label, cmd in nav:
            tk.Button(self.sidebar, text=label,
                      bg=ACCENT, fg=WHITE,
                      font=("Segoe UI", 11), bd=0, pady=11,
                      activebackground=BG, activeforeground=YELLOW,
                      anchor="w", padx=18, cursor="hand2",
                      command=cmd).pack(fill="x")

    def _build_main_area(self):
        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="right", fill="both", expand=True)

    def _clear(self):
        for w in self.main.winfo_children():
            w.destroy()

    def _heading(self, text):
        tk.Label(self.main, text=text, bg=BG, fg=WHITE,
                 font=("Segoe UI", 20, "bold")).pack(pady=18, padx=20, anchor="w")

    def _export_csv(self):
        ok = export_bookings_to_csv()
        messagebox.showinfo("Export CSV",
            "✅ Exported to D:\\BusSeatReservation\\bookings_export.csv" if ok
            else "⚠ No bookings found to export.")

    # ── Password-guarded entry points ───────────────────────────
    def _open_admin_guarded(self):
        if _ask_password(self, "Admin Panel — Password Required"):
            self.show_admin()

    def _open_waitlist_guarded(self):
        if _ask_password(self, "Waitlist — Password Required"):
            self.show_waitlist()

    # ── DASHBOARD ───────────────────────────────────────────────
    def show_dashboard(self):
        self._clear()
        self._heading("Dashboard")

        buses = get_all_buses()
        if not buses:
            tk.Label(self.main,
                     text="No buses found. Run seed_data.py first.",
                     bg=BG, fg=YELLOW,
                     font=("Segoe UI", 13)).pack(pady=40)
            return

        canvas    = tk.Canvas(self.main, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main, orient="vertical",
                                  command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG)
        scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")

        for bus in buses:
            seats  = get_seats_for_bus(bus["id"])
            booked = sum(1 for s in seats if s["is_booked"])
            free   = len(seats) - booked

            card = tk.Frame(scroll_frame, bg=PANEL, padx=18, pady=14)
            card.pack(fill="x", pady=6, padx=4)

            tk.Label(card,
                     text=f"🚌  {bus['bus_number']}   |   {bus['route']}",
                     bg=PANEL, fg=WHITE,
                     font=("Segoe UI", 13, "bold")).pack(anchor="w")
            tk.Label(card,
                     text=f"Departure: {bus['departure_time']}",
                     bg=PANEL, fg=YELLOW,
                     font=("Segoe UI", 10)).pack(anchor="w", pady=2)

            info = tk.Frame(card, bg=PANEL)
            info.pack(anchor="w")
            tk.Label(info, text=f"✅ Free: {free}",
                     bg=PANEL, fg=GREEN,
                     font=("Segoe UI", 10)).pack(side="left", padx=(0, 12))
            tk.Label(info, text=f"❌ Booked: {booked}",
                     bg=PANEL, fg=RED,
                     font=("Segoe UI", 10)).pack(side="left")

            tk.Button(card, text="View Seat Map",
                      bg=GREEN, fg="white",
                      font=("Segoe UI", 9, "bold"),
                      cursor="hand2",
                      command=lambda b=bus: self.show_seat_map(b)
                      ).pack(anchor="e", pady=4)

    # ── SEAT MAP ────────────────────────────────────────────────
    def show_seat_map(self, bus):
        self._clear()
        self._heading(f"Seat Map — {bus['bus_number']}")

        seats = get_seats_for_bus(bus["id"])
        mat   = SeatMatrix()
        for s in seats:
            if s["is_booked"]:
                mat.book_seat(s["seat_number"])

        # Legend — use coloured squares instead of emoji circles
        legend_frame = tk.Frame(self.main, bg=BG)
        legend_frame.pack()
        tk.Label(legend_frame, text="  ", bg=GREEN,
                 width=2).pack(side="left", padx=(0, 4))
        tk.Label(legend_frame, text="Available",
                 bg=BG, fg=WHITE,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 16))
        tk.Label(legend_frame, text="  ", bg=RED,
                 width=2).pack(side="left", padx=(0, 4))
        tk.Label(legend_frame, text="Booked",
                 bg=BG, fg=WHITE,
                 font=("Segoe UI", 10)).pack(side="left")

        grid_frame = tk.Frame(self.main, bg=BG)
        grid_frame.pack(pady=14)

        for idx, seat in enumerate(seats):
            r, c  = divmod(idx, 5)
            color = RED if seat["is_booked"] else GREEN
            lbl   = f"{'❌' if seat['is_booked'] else '✅'}\n{seat['seat_number']}"
            tk.Label(grid_frame, text=lbl,
                     bg=color, fg="white",
                     width=7, height=3,
                     font=("Segoe UI", 9, "bold"),
                     relief="raised").grid(row=r, column=c, padx=4, pady=4)

        tk.Button(self.main, text="← Back to Dashboard",
                  bg=ACCENT, fg=WHITE,
                  font=("Segoe UI", 10),
                  command=self.show_dashboard).pack(pady=12)

    # ── BOOKING FORM ────────────────────────────────────────────
    def show_booking(self):
        self._clear()
        self._heading("Book a Seat")

        form = tk.Frame(self.main, bg=PANEL, padx=30, pady=25)
        form.pack(padx=40, pady=6, fill="x")

        fields = [
            ("Full Name",               "name"),
            ("CNIC (e.g. 12345-1234567-1)", "cnic"),
            ("Email",                   "email"),
            ("Phone",                   "phone"),
        ]
        entries = {}
        for label, key in fields:
            tk.Label(form, text=label, bg=PANEL, fg=WHITE,
                     font=("Segoe UI", 11)).pack(anchor="w", pady=(8, 0))
            e = tk.Entry(form, font=("Segoe UI", 11),
                         bg=ACCENT, fg=WHITE,
                         insertbackground=WHITE, width=42)
            e.pack(anchor="w", ipady=5)
            entries[key] = e

        tk.Label(form, text="Select Bus", bg=PANEL, fg=WHITE,
                 font=("Segoe UI", 11)).pack(anchor="w", pady=(10, 0))
        buses   = get_all_buses()
        bus_map = {f"{b['bus_number']} — {b['route']}": b for b in buses}
        bus_var = tk.StringVar()
        bus_cb  = ttk.Combobox(form, textvariable=bus_var,
                               values=list(bus_map.keys()), width=40,
                               state="readonly")
        bus_cb.bind("<Button-1>", lambda e: bus_cb.event_generate('<Down>'))
        bus_cb.pack(anchor="w")

        tk.Label(form, text="Select Seat", bg=PANEL, fg=WHITE,
                 font=("Segoe UI", 11)).pack(anchor="w", pady=(10, 0))
        seat_var = tk.StringVar()
        seat_cb  = ttk.Combobox(form, textvariable=seat_var, width=40,
                                state="readonly")
        seat_cb.bind("<Button-1>", lambda e: seat_cb.event_generate('<Down>'))
        seat_cb.pack(anchor="w")

        def load_seats(*_):
            chosen = bus_map.get(bus_var.get())
            if chosen:
                seats = get_seats_for_bus(chosen["id"])
                free  = [str(s["seat_number"]) for s in seats
                         if not s["is_booked"]]
                seat_cb["values"] = free

        bus_var.trace("w", load_seats)

        status_lbl = tk.Label(self.main, text="", bg=BG, fg=GREEN,
                              font=("Segoe UI", 11))
        status_lbl.pack(pady=6)

        def submit():
            bus = bus_map.get(bus_var.get().strip())
            if not bus:
                for key in bus_map:
                    if bus_var.get().strip() in key:
                        bus = bus_map[key]; break

            name = entries["name"].get().strip()
            cnic = entries["cnic"].get().strip()

            if not bus or not seat_var.get() or not name or not cnic:
                messagebox.showerror("Missing Info",
                                     "Please fill all fields and select a seat.")
                return

            seats = get_seats_for_bus(bus["id"])
            sid   = next((s["id"] for s in seats
                          if str(s["seat_number"]) == seat_var.get()), None)
            if not sid:
                messagebox.showerror("Error", "Seat not found."); return

            try:
                pid = add_passenger(name, cnic,
                                    entries["email"].get(),
                                    entries["phone"].get())
                book_seat(pid, sid)
                self.hash_table.insert(pid, {"name": name, "seat": seat_var.get()})
                self.passenger_bst.insert(name, {"name": name, "cnic": cnic})
                status_lbl.config(
                    text=f"✅ Seat {seat_var.get()} booked for {name}!")
                for e in entries.values():
                    e.delete(0, tk.END)
                seat_cb["values"] = []
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

        tk.Button(form, text="✅  Confirm Booking",
                  bg=GREEN, fg="white",
                  font=("Segoe UI", 12, "bold"),
                  pady=8, cursor="hand2",
                  command=submit).pack(pady=18)

    # ── SEARCH ──────────────────────────────────────────────────
    def show_search(self):
        self._clear()
        self._heading("Search Bookings")

        frame = tk.Frame(self.main, bg=PANEL, padx=24, pady=22)
        frame.pack(padx=30, fill="x")

        result_lbl = tk.Label(self.main, text="",
                              bg=BG, fg=YELLOW,
                              font=("Segoe UI", 11),
                              wraplength=750)
        result_lbl.pack(pady=12)

        # ── Hash Search ───────────────────────────────────────────────
        tk.Label(frame,
                 text="🔑  Hash Search — Select a Booking:",
                 bg=PANEL, fg=WHITE,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(frame,
                 text="Booking ID is the unique number auto-assigned to each reservation in the database.",
                 bg=PANEL, fg=YELLOW,
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))

        all_bookings    = get_all_bookings()
        booking_options = [
            f"{b['id']}  —  {b['name']}  |  Seat {b['seat_number']}  |  {b['bus_number']}"
            for b in all_bookings
        ]
        booking_id_map = {opt: b["id"] for opt, b in zip(booking_options, all_bookings)}

        hash_var = tk.StringVar()
        hash_cb  = ttk.Combobox(frame, textvariable=hash_var,
                                values=booking_options, width=60)
        hash_cb.pack(anchor="w", ipady=4, pady=4)

        def _filter_hash(event=None):
            typed = hash_var.get().lower()
            hash_cb["values"] = (booking_options if typed == ""
                                 else [o for o in booking_options if typed in o.lower()])
            try:
                hash_cb.event_generate("<Down>")
            except Exception:
                pass

        hash_cb.bind("<KeyRelease>", _filter_hash)

        def do_hash():
            chosen = hash_var.get().strip()
            if not chosen:
                result_lbl.config(text="⚠ Please select or type a booking.")
                return
            bid = booking_id_map.get(chosen)
            if bid is None:
                for opt, oid in booking_id_map.items():
                    if chosen.lower() in opt.lower():
                        bid = oid; break
            if bid is None:
                result_lbl.config(text="❌  No matching booking found.")
                return
            r = self.hash_table.search(bid)
            if r:
                result_lbl.config(
                    text=f"✅  Found — Passenger: {r.get('name')}  |  "
                         f"Seat: {r.get('seat_number')}  |  "
                         f"Bus: {r.get('bus_number')}  |  "
                         f"Status: {r.get('status')}")
            else:
                result_lbl.config(text="❌  Booking not found in hash table.")

        tk.Button(frame, text="Hash Search",
                  bg=ACCENT, fg=WHITE,
                  font=("Segoe UI", 10),
                  cursor="hand2",
                  command=do_hash).pack(anchor="w", pady=6)

        tk.Frame(frame, bg=WHITE, height=1).pack(fill="x", pady=12)

        # ── Binary Search ─────────────────────────────────────────────
        tk.Label(frame,
                 text="🔢  Binary Search — Enter Seat Number:",
                 bg=PANEL, fg=WHITE,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        bin_entry = tk.Entry(frame, font=("Segoe UI", 11),
                             bg=ACCENT, fg=WHITE,
                             insertbackground=WHITE, width=30)
        bin_entry.pack(anchor="w", ipady=5, pady=4)

        def do_binary():
            val = bin_entry.get().strip()
            if not val.isdigit():
                result_lbl.config(text="⚠ Enter a numeric seat number.")
                return
            target   = int(val)
            bookings = sorted(get_all_bookings(),
                              key=lambda x: int(x["seat_number"]))
            low, high = 0, len(bookings) - 1
            found = None
            while low <= high:
                mid     = (low + high) // 2
                mid_val = int(bookings[mid]["seat_number"])
                if mid_val == target:
                    found = bookings[mid]; break
                elif mid_val < target:
                    low = mid + 1
                else:
                    high = mid - 1
            if found:
                result_lbl.config(
                    text=f"✅  Seat {val} — {found['name']} "
                         f"on bus {found['bus_number']}  |  "
                         f"Status: {found['status']}")
            else:
                result_lbl.config(text=f"❌  Seat {val} has no confirmed booking.")

        tk.Button(frame, text="Binary Search",
                  bg=ACCENT, fg=WHITE,
                  font=("Segoe UI", 10),
                  cursor="hand2",
                  command=do_binary).pack(anchor="w")

        tk.Frame(frame, bg=WHITE, height=1).pack(fill="x", pady=12)

        # ── BST Search ────────────────────────────────────────────────
        tk.Label(frame,
                 text="🌳  BST Search — Enter Passenger Name:",
                 bg=PANEL, fg=WHITE,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        bst_entry = tk.Entry(frame, font=("Segoe UI", 11),
                             bg=ACCENT, fg=WHITE,
                             insertbackground=WHITE, width=30)
        bst_entry.pack(anchor="w", ipady=5, pady=4)

        def do_bst():
            name = bst_entry.get().strip()
            r    = self.passenger_bst.search(name)
            if r:
                result_lbl.config(
                    text=f"✅  BST Found — {r.get('name')}  |  "
                         f"Seat: {r.get('seat_number')}  |  "
                         f"Bus: {r.get('bus_number')}")
            else:
                result_lbl.config(text="❌  Passenger not found in BST.")

        tk.Button(frame, text="BST Search",
                  bg=ACCENT, fg=WHITE,
                  font=("Segoe UI", 10),
                  cursor="hand2",
                  command=do_bst).pack(anchor="w")

    # ── ROUTES ──────────────────────────────────────────────────
    def show_routes(self):
        self._clear()
        self._heading("Route Finder — Dijkstra's Algorithm")

        frame = tk.Frame(self.main, bg=PANEL, padx=24, pady=22)
        frame.pack(padx=30, fill="x")

        stops  = self.route_graph.get_all_stops()
        from_v = tk.StringVar()
        to_v   = tk.StringVar()

        tk.Label(frame, text="From:", bg=PANEL, fg=WHITE,
                 font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=6)
        ttk.Combobox(frame, textvariable=from_v,
                     values=stops, width=28).grid(row=0, column=1, padx=12, pady=6)

        tk.Label(frame, text="To:", bg=PANEL, fg=WHITE,
                 font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w")
        ttk.Combobox(frame, textvariable=to_v,
                     values=stops, width=28).grid(row=1, column=1, padx=12)

        result_lbl = tk.Label(self.main, text="",
                              bg=BG, fg=GREEN,
                              font=("Segoe UI", 12),
                              wraplength=700)
        result_lbl.pack(pady=16)

        bfs_lbl = tk.Label(self.main, text="",
                           bg=BG, fg=YELLOW,
                           font=("Segoe UI", 11),
                           wraplength=700)
        bfs_lbl.pack()

        def find():
            f, t = from_v.get(), to_v.get()
            if not f or not t:
                result_lbl.config(text="⚠ Select both stops."); return

            path, dist = self.route_graph.dijkstra(f, t)
            if dist == float('inf'):
                result_lbl.config(text="❌ No path found."); return

            # Build segment breakdown: A → B → C = d1+d2 = total
            if len(path) >= 2:
                segments = []
                for i in range(len(path) - 1):
                    seg_dist = self._get_edge_weight(path[i], path[i + 1])
                    segments.append(str(seg_dist))
                breakdown = "+".join(segments)
                route_str = " → ".join(path)
                result_lbl.config(
                    text=f"🗺  Shortest Path: {route_str} = {dist}km: {breakdown}")
            else:
                result_lbl.config(
                    text=f"🗺  Path: {' → '.join(path)}\n📏  Total: {dist} km")

            bfs = self.route_graph.bfs(f)
            bfs_lbl.config(text=f"BFS traversal from {f}: {' → '.join(bfs)}")

        tk.Button(frame, text="Find Shortest Route",
                  bg=GREEN, fg="white",
                  font=("Segoe UI", 11, "bold"),
                  cursor="hand2",
                  command=find).grid(row=2, column=1,
                                     sticky="w", padx=12, pady=14)

    def _get_edge_weight(self, u, v):
        """Return the direct edge weight between u and v (0 if not found)."""
        for neighbor, weight in self.route_graph.graph.get(u, []):
            if neighbor == v:
                return weight
        return 0

    # ── SORT STATS ──────────────────────────────────────────────
    def show_sort_stats(self):
        self._clear()
        self._heading("Sorting Algorithm Comparison")

        bookings = get_all_bookings()
        if not bookings:
            tk.Label(self.main,
                     text="No bookings yet. Run seed_data.py first.",
                     bg=BG, fg=YELLOW,
                     font=("Segoe UI", 12)).pack(pady=30)
            return

        result = compare_sorts(bookings, "id")
        frame  = tk.Frame(self.main, bg=PANEL, padx=30, pady=28)
        frame.pack(padx=40, pady=10)

        rows = [
            ("Records sorted:",   str(len(bookings))),
            ("Merge Sort time:",  f"{result['merge_sort_ms']} ms"),
            ("Bubble Sort time:", f"{result['bubble_sort_ms']} ms"),
            ("Faster algorithm:", result["faster"]),
        ]
        for label, val in rows:
            r = tk.Frame(frame, bg=PANEL)
            r.pack(fill="x", pady=5)
            tk.Label(r, text=label, bg=PANEL, fg=WHITE,
                     font=("Segoe UI", 12), width=22,
                     anchor="w").pack(side="left")
            tk.Label(r, text=val, bg=PANEL, fg=YELLOW,
                     font=("Segoe UI", 12, "bold")).pack(side="left")

        tk.Label(self.main,
                 text="Merge Sort: O(n log n)  |  Bubble Sort: O(n²)\n"
                      "Merge Sort wins on large datasets — "
                      "this is the industry standard choice.",
                 bg=BG, fg=WHITE,
                 font=("Segoe UI", 10),
                 wraplength=600,
                 justify="left").pack(pady=18, padx=40, anchor="w")

    # ── WAITLIST (password-protected via sidebar) ────────────────
    def show_waitlist(self):
        self._clear()
        self._heading("Waitlist Queue")

        frame = tk.Frame(self.main, bg=PANEL, padx=24, pady=20)
        frame.pack(padx=30, fill="x")

        tk.Label(frame, text="Add Passenger to Waitlist:",
                 bg=PANEL, fg=WHITE,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")

        tk.Label(frame, text="Name:", bg=PANEL, fg=WHITE,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(8, 0))
        name_e = tk.Entry(frame, font=("Segoe UI", 11),
                          bg=ACCENT, fg=WHITE,
                          insertbackground=WHITE, width=35)
        name_e.pack(anchor="w", ipady=4)

        tk.Label(frame, text="Phone:", bg=PANEL, fg=WHITE,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 0))
        phone_e = tk.Entry(frame, font=("Segoe UI", 11),
                           bg=ACCENT, fg=WHITE,
                           insertbackground=WHITE, width=35)
        phone_e.pack(anchor="w", ipady=4)

        list_frame = tk.Frame(self.main, bg=BG)
        list_frame.pack(padx=30, pady=14, fill="x")

        queue_lbl = tk.Label(list_frame, text="",
                             bg=BG, fg=YELLOW,
                             font=("Segoe UI", 11),
                             justify="left")
        queue_lbl.pack(anchor="w")

        def _log_waitlist_action(action, name, phone):
            log_path    = WAITLIST_LOG
            file_exists = os.path.isfile(log_path)
            try:
                with open(log_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(
                        f, fieldnames=["datetime", "action", "name", "phone"])
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow({
                        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "action":   action,
                        "name":     name,
                        "phone":    phone,
                    })
            except Exception as e:
                print(f"[Waitlist log error] {e}")

        def refresh_list():
            items = self.waitlist.get_all()
            if items:
                text = "\n".join(
                    f"{i+1}. {p['name']} — {p['phone']}"
                    for i, p in enumerate(items))
                queue_lbl.config(
                    text=f"Queue ({self.waitlist.size()} waiting):\n{text}")
            else:
                queue_lbl.config(text="Queue is empty.")

        def add_to_waitlist():
            n = name_e.get().strip()
            p = phone_e.get().strip()
            if not n:
                messagebox.showerror("Error", "Enter a name.")
                return
            self.waitlist.enqueue({"name": n, "phone": p})
            _log_waitlist_action("ADDED", n, p)
            name_e.delete(0, tk.END)
            phone_e.delete(0, tk.END)
            refresh_list()

        def serve_next():
            passenger = self.waitlist.dequeue()
            if passenger:
                _log_waitlist_action("SERVED", passenger["name"], passenger["phone"])
                messagebox.showinfo("Served",
                    f"Next passenger served: {passenger['name']}")
                refresh_list()
            else:
                messagebox.showinfo("Empty", "Waitlist is empty.")

        btn_row = tk.Frame(frame, bg=PANEL)
        btn_row.pack(anchor="w", pady=12)

        tk.Button(btn_row, text="Add to Waitlist",
                  bg=ACCENT, fg=WHITE,
                  font=("Segoe UI", 10),
                  cursor="hand2",
                  command=add_to_waitlist).pack(side="left", padx=(0, 10))
        tk.Button(btn_row, text="Serve Next ▶",
                  bg=GREEN, fg="white",
                  font=("Segoe UI", 10),
                  cursor="hand2",
                  command=serve_next).pack(side="left")

        def open_log():
            if os.path.isfile(WAITLIST_LOG):
                os.startfile(WAITLIST_LOG)
            else:
                messagebox.showinfo("Log", "No waitlist activity logged yet.")

        tk.Button(btn_row, text="📄 Open Log CSV",
                  bg=YELLOW, fg="#1a1a2e",
                  font=("Segoe UI", 10, "bold"),
                  cursor="hand2",
                  command=open_log).pack(side="left", padx=(10, 0))

        refresh_list()

    # ── ADMIN ───────────────────────────────────────────────────
    def show_admin(self):
        self._clear()
        self._heading("Admin Panel — All Bookings")

        # ── Search / filter bar ──────────────────────────────────────
        filter_frame = tk.Frame(self.main, bg=BG)
        filter_frame.pack(fill="x", padx=20, pady=(0, 6))

        tk.Label(filter_frame, text="🔍 Search:",
                 bg=BG, fg=WHITE,
                 font=("Segoe UI", 10)).pack(side="left")

        search_var = tk.StringVar()
        search_e   = tk.Entry(filter_frame, textvariable=search_var,
                              font=("Segoe UI", 10),
                              bg=ACCENT, fg=WHITE,
                              insertbackground=WHITE, width=30)
        search_e.pack(side="left", ipady=4, padx=(6, 16))

        # Column-filter dropdown
        col_filter_var = tk.StringVar(value="All Columns")
        col_options    = ["All Columns", "ID", "Passenger", "CNIC",
                          "Seat", "Bus", "Date", "Status"]
        col_cb         = ttk.Combobox(filter_frame, textvariable=col_filter_var,
                                      values=col_options, width=14, state="readonly")
        col_cb.pack(side="left")

        # ── Treeview ─────────────────────────────────────────────────
        cols = ("ID", "Passenger", "CNIC", "Seat", "Bus", "Date", "Status")

        frame = tk.Frame(self.main, bg=BG)
        frame.pack(fill="both", expand=True, padx=20)

        tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)
        vsb  = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        widths = [50, 160, 130, 60, 110, 150, 90]

        all_bookings = get_all_bookings()

        def _populate(rows):
            tree.delete(*tree.get_children())
            for b in rows:
                tag = "cancelled" if str(b.get("status", "")).lower() == "cancelled" else ""
                tree.insert("", "end", values=(
                    b["id"], b["name"], b["cnic"],
                    b["seat_number"], b["bus_number"],
                    b["booking_date"], b["status"]
                ), tags=(tag,))

        tree.tag_configure("cancelled", foreground="#ff7675")

        # Column headings with sort dropdown trigger
        for c, w in zip(cols, widths):
            tree.heading(c, text=c,
                         command=lambda _c=c: _sort_by(_c))
            tree.column(c, width=w, anchor="w")

        _sort_state = {"col": None, "rev": False}

        def _sort_by(col):
            col_idx = cols.index(col)
            _sort_state["rev"] = (not _sort_state["rev"]
                                  if _sort_state["col"] == col else False)
            _sort_state["col"] = col
            data = [(tree.set(k, col), k) for k in tree.get_children("")]
            try:
                data.sort(key=lambda t: int(t[0]), reverse=_sort_state["rev"])
            except ValueError:
                data.sort(key=lambda t: t[0].lower(), reverse=_sort_state["rev"])
            for idx, (_, k) in enumerate(data):
                tree.move(k, "", idx)
            # Update heading arrows
            for c2 in cols:
                arrow = (" ▲" if not _sort_state["rev"] else " ▼") if c2 == col else ""
                tree.heading(c2, text=c2 + arrow)

        def _apply_filter(*_):
            query  = search_var.get().strip().lower()
            col_f  = col_filter_var.get()
            if not query:
                _populate(all_bookings)
                return
            col_idx_map = {
                "ID": "id", "Passenger": "name", "CNIC": "cnic",
                "Seat": "seat_number", "Bus": "bus_number",
                "Date": "booking_date", "Status": "status"
            }
            filtered = []
            for b in all_bookings:
                if col_f == "All Columns":
                    haystack = " ".join(str(v).lower() for v in b.values())
                else:
                    key      = col_idx_map.get(col_f, "name")
                    haystack = str(b.get(key, "")).lower()
                if query in haystack:
                    filtered.append(b)
            _populate(filtered)

        search_var.trace("w", _apply_filter)
        col_filter_var.trace("w", _apply_filter)

        _populate(all_bookings)

        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # ── Bottom action buttons ─────────────────────────────────────
        btn_frame = tk.Frame(self.main, bg=BG)
        btn_frame.pack(pady=8)

        def cancel_sel():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a booking first.")
                return
            bid    = tree.item(sel[0])["values"][0]
            status = str(tree.item(sel[0])["values"][6]).lower()
            if status == "cancelled":
                messagebox.showinfo("Info", "This booking is already cancelled.")
                return
            if messagebox.askyesno("Confirm", f"Cancel booking {bid}?"):
                cancel_booking(bid)
                self.hash_table.delete(bid)
                messagebox.showinfo("Done", f"Booking {bid} cancelled.")
                # Refresh in-place: update the row status rather than full reload
                tree.set(sel[0], "Status", "cancelled")
                tree.item(sel[0], tags=("cancelled",))

        def confirm_sel():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a booking first.")
                return
            bid    = tree.item(sel[0])["values"][0]
            status = str(tree.item(sel[0])["values"][6]).lower()
            if status == "confirmed":
                messagebox.showinfo("Info", "This booking is already confirmed.")
                return
            if messagebox.askyesno("Confirm", f"Set booking {bid} back to confirmed?"):
                # Update DB status
                try:
                    from database import update_booking_status
                    update_booking_status(bid, "confirmed")
                except Exception:
                    pass
                tree.set(sel[0], "Status", "confirmed")
                tree.item(sel[0], tags=("",))
                messagebox.showinfo("Done", f"Booking {bid} set to confirmed.")

        tk.Button(btn_frame, text="❌  Cancel Selected",
                  bg=RED, fg="white",
                  font=("Segoe UI", 11, "bold"),
                  cursor="hand2",
                  command=cancel_sel).pack(side="left", padx=8)

        tk.Button(btn_frame, text="✅  Confirm Selected",
                  bg=GREEN, fg="white",
                  font=("Segoe UI", 11, "bold"),
                  cursor="hand2",
                  command=confirm_sel).pack(side="left", padx=8)


if __name__ == "__main__":
    app = BusReservationApp()
    app.mainloop()