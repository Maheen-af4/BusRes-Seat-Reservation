import csv, os, re, random, string, time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# Force default theme IMMEDIATELY — must happen before any Tk/ttk widget is created
# On Windows, vista theme ignores tag background colors in Treeview
import tkinter
_root_check = tkinter.Tk()
_style_fix  = ttk.Style(_root_check)
_style_fix.theme_use("default")
_root_check.destroy()
from database import (
    get_all_buses, get_seats_for_bus, book_seat, add_passenger,
    cancel_booking, get_all_bookings, update_booking_status,
    add_waitlist_booking, serve_waitlist_booking, get_waitlisted_bookings,
    get_waitlist_for_passenger, get_bookings_for_passenger,
    get_passenger_by_cnic, get_passenger_id_by_name,
    get_all_users, delete_user, create_user, login_user, change_password,
    get_all_promo_codes, validate_promo, use_promo,
    create_promo, toggle_promo, delete_promo,
    get_payment_methods, toggle_payment_method,
    record_payment, get_payment_for_booking, backfill_payments,
    get_bookings_for_passenger_by_cnic,
    get_analytics_stats, get_revenue_stats, get_revenue_per_bus,
    get_bookings_per_bus, get_bookings_per_route,
    get_buses_with_stats, add_bus, update_bus, delete_bus,
    submit_feedback, get_feedback_for_passenger,
    get_all_feedback, get_avg_rating_per_bus, delete_feedback,
    ensure_schema,
    sync_seats_from_bookings,
    add_user_id_to_bookings,
    get_bookings_for_user,
    get_waitlist_for_user,
    get_passenger_id_by_user_id,
    get_user_cnic, get_booking_by_id, 
    is_seat_taken
)
from dsa.seat_matrix import SeatMatrix
from dsa.sorting import compare_sorts
from dsa.searching import BookingHashTable
from dsa.graph import RouteGraph
from dsa.bst import PassengerBST
from dsa.queue_waitlist import WaitlistQueue
from file_handler import export_bookings_to_csv

WAITLIST_LOG = r"D:\BusSeatReservation\waitlist_log.csv"

# Coffee & Caramel Theme
BG      = "#1C0F0A"
PANEL   = "#2C1810"
SIDEBAR = "#241209"
ACCENT  = "#6B3A2A"
GREEN   = "#7D9B6A"
RED     = "#C0392B"
WHITE   = "#F5E6D3"
YELLOW  = "#C8853A"
GOLD    = "#E8A44A"
PURPLE  = "#8B6F7A"
CARD1   = "#3D1F0D"
CARD2   = "#2A1F0A"
BLUE    = "#4A7C9E"

ADMIN_USERNAME = "Maheen"
ADMIN_PASSWORD = "maple"
MANAGER_USERNAME = "Kinza"
MANAGER_PASSWORD = "maple"

FONT_TITLE = ("Georgia", 20, "bold")
FONT_HEAD  = ("Georgia", 13, "bold")
FONT_BODY  = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)
FONT_CARD  = ("Georgia", 28, "bold")
FONT_BTN   = ("Segoe UI", 10, "bold")

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BusRes — Sign In")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._build()
        self.update_idletasks()
        self._center()

    def _center(self):
        self.update_idletasks()
        w = 460
        h = self.winfo_reqheight() + 10
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        tk.Label(self, text="🚌", font=("Segoe UI", 28), bg=BG, fg=YELLOW).pack(pady=(18,2))
        tk.Label(self, text="BusRes", font=("Georgia",22,"bold"), bg=BG, fg=WHITE).pack()
        tk.Label(self, text="Sign in to your account", font=FONT_SMALL, bg=BG, fg=YELLOW).pack(pady=(1,10))

        card = tk.Frame(self, bg=PANEL, padx=28, pady=18)
        card.pack(padx=28, fill="x")

        # Role selector
        tk.Label(card, text="Select Role", bg=PANEL, fg=WHITE, font=("Segoe UI",10,"bold")).pack(anchor="w")
        role_row = tk.Frame(card, bg=PANEL)
        role_row.pack(anchor="w", pady=(3,10))
        self.role_var = tk.StringVar(value="admin")
        for r, color in [("admin",GOLD),("manager",GREEN),("passenger",BLUE)]:
            tk.Radiobutton(role_row, text=r.upper(), variable=self.role_var, value=r,
                           bg=PANEL, fg=color, selectcolor=PANEL, activebackground=PANEL,
                           font=("Segoe UI",10,"bold"), cursor="hand2").pack(side="left", padx=6)

        # Username
        tk.Label(card, text="Username", bg=PANEL, fg=WHITE, font=FONT_BODY).pack(anchor="w", pady=(0,2))
        self.user_e = tk.Entry(card, font=FONT_BODY, bg=ACCENT, fg=WHITE, insertbackground=WHITE, width=34)
        self.user_e.pack(fill="x", ipady=5)

        # Password
        tk.Label(card, text="Password", bg=PANEL, fg=WHITE, font=FONT_BODY).pack(anchor="w", pady=(8,2))
        pw_row = tk.Frame(card, bg=PANEL)
        pw_row.pack(fill="x")
        self.pw_e = tk.Entry(pw_row, font=FONT_BODY, bg=ACCENT, fg=WHITE, insertbackground=WHITE, show="● ", width=28)
        self.pw_e.pack(side="left", ipady=5, fill="x", expand=True)
        self._show_pw = False
        tk.Button(pw_row, text="👁", bg=ACCENT, fg=WHITE, bd=0, cursor="hand2", command=self._toggle_pw).pack(side="left", padx=(4,0))

        self.err_lbl = tk.Label(card, text="", bg=PANEL, fg=RED, font=FONT_SMALL)
        self.err_lbl.pack(pady=(6,0))

        tk.Button(card, text="Sign In", bg=YELLOW, fg=BG, font=("Georgia",12,"bold"),
                  cursor="hand2", pady=8, bd=0, command=self._sign_in).pack(fill="x", pady=(10,0))
        self.pw_e.bind("<Return>", lambda e: self._sign_in())

        #Tip

        # ── Create Account — always visible ──────────────────────────
        ca_frame = tk.Frame(self, bg="#2C1810", padx=20, pady=12)
        ca_frame.pack(fill="x", padx=28, pady=(0,12))
        tk.Label(ca_frame, text="New Passenger? Create an account below:",
                 font=FONT_SMALL, bg="#2C1810", fg=WHITE).pack(anchor="w")
        tk.Button(ca_frame, text="➕  Create Account",
                  bg=YELLOW, fg=BG,
                  font=("Segoe UI",10,"bold"),
                  pady=6, cursor="hand2", bd=0,
                  command=self._open_create).pack(fill="x", pady=(6,0))

    def _toggle_pw(self):
        self._show_pw = not self._show_pw
        self.pw_e.config(show="" if self._show_pw else "● ")

    def _sign_in(self):
        username = self.user_e.get().strip()
        password = self.pw_e.get().strip()
        role     = self.role_var.get()
        if not username or not password:
            self.err_lbl.config(text="⚠ Enter username and password."); return
        user = login_user(username, password, role)
        if not user:
            self.err_lbl.config(text="❌  Invalid credentials or wrong role."); return
        self.destroy()
        BusResApp(user).mainloop()

    def _open_create(self):
        CreateAccountWindow(self)


class CreateAccountWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create Account")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self._build_content()
        self.update_idletasks()
        w = 420; h = self.winfo_reqheight()+20
        x=(self.winfo_screenwidth()-w)//2; y=(self.winfo_screenheight()-h)//2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_content(self):
        tk.Label(self, text="🚌", font=("Segoe UI",26), bg=BG, fg=YELLOW).pack(pady=(16,2))
        tk.Label(self, text="Create Account", font=("Georgia",18,"bold"), bg=BG, fg=WHITE).pack()
        tk.Label(self, text="Passenger registration only", font=FONT_SMALL, bg=BG, fg=YELLOW).pack(pady=(1,10))
        card = tk.Frame(self, bg=PANEL, padx=24, pady=16)
        card.pack(padx=20, fill="x")
        self.entries = {}
        for label, key in [("Username","user"),("Email (optional)","email")]:
            tk.Label(card, text=label, bg=PANEL, fg=WHITE, font=FONT_BODY).pack(anchor="w", pady=(4,1))
            e = tk.Entry(card, font=FONT_BODY, bg=ACCENT, fg=WHITE, insertbackground=WHITE, width=34)
            e.pack(fill="x", ipady=4); self.entries[key] = e
        for label, key in [("Password (4-20 chars)","pw"),("Confirm Password","pw2")]:
            tk.Label(card, text=label, bg=PANEL, fg=WHITE, font=FONT_BODY).pack(anchor="w", pady=(4,1))
            e = tk.Entry(card, font=FONT_BODY, bg=ACCENT, fg=WHITE, insertbackground=WHITE, show="● ", width=34)
            e.pack(fill="x", ipady=4); self.entries[key] = e
        # Passengers only — managers sign in with hardcoded credentials
        self.role_var = tk.StringVar(value="passenger")
        self.err_lbl = tk.Label(card, text="", bg=PANEL, fg=RED, font=FONT_SMALL)
        self.err_lbl.pack(pady=(4,0))
        tk.Button(card, text="✅  Create Account", bg=GREEN, fg=BG,
                  font=("Georgia",11,"bold"), pady=9, cursor="hand2", bd=0,
                  command=self._create).pack(fill="x", pady=(8,0))
        tk.Button(self, text="← Back to Login", bg=BG, fg=YELLOW,
                  font=FONT_SMALL, bd=0, cursor="hand2",
                  command=self.destroy).pack(pady=(8,12))

    def _create(self):
        u=self.entries["user"].get().strip(); em=self.entries["email"].get().strip()
        pw=self.entries["pw"].get(); p2=self.entries["pw2"].get(); r=self.role_var.get()
        if not u: self.err_lbl.config(text="⚠ Username required."); return
        if not 4<=len(pw)<=20: self.err_lbl.config(text="⚠ Password must be 4-20 chars."); return
        if pw!=p2: self.err_lbl.config(text="⚠ Passwords do not match."); return
        ok, result = create_user(u, pw, r, em)
        if not ok: self.err_lbl.config(text=f"❌  {result}"); return
        messagebox.showinfo("Success", f"Account created! Sign in as {r.upper()}.")
        self.destroy()


class ChangePasswordWindow(tk.Toplevel):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.title("Change Password")
        self.configure(bg=BG)
        self.geometry("380x400")
        self.resizable(False, False)
        self.grab_set()
        x=(self.winfo_screenwidth()-380)//2; y=(self.winfo_screenheight()-400)//2
        self.geometry(f"380x400+{x}+{y}")
        tk.Label(self, text="🔑  Change Password", font=FONT_HEAD, bg=BG, fg=WHITE).pack(pady=(24,2))
        tk.Label(self, text="Password must be 4-20 characters", font=FONT_SMALL, bg=BG, fg=YELLOW).pack(pady=(0,16))
        card = tk.Frame(self, bg=PANEL, padx=28, pady=22)
        card.pack(padx=24, fill="x")
        self.entries = {}
        for label, key in [("Current Password","cur"),("New Password","new"),("Confirm Password","con")]:
            tk.Label(card, text=label, bg=PANEL, fg=WHITE, font=FONT_BODY).pack(anchor="w", pady=(6,1))
            row = tk.Frame(card, bg=PANEL); row.pack(fill="x")
            e = tk.Entry(row, font=FONT_BODY, bg=ACCENT, fg=WHITE, insertbackground=WHITE, show="● ", width=28)
            e.pack(side="left", fill="x", expand=True, ipady=5)
            _show=[False]
            def _tog(entry=e, state=_show):
                state[0]=not state[0]; entry.config(show="" if state[0] else "● ")
            tk.Button(row, text="👁", bg=ACCENT, fg=WHITE, bd=0, cursor="hand2", command=_tog).pack(side="left", padx=2)
            self.entries[key] = e
        self.err_lbl = tk.Label(card, text="", bg=PANEL, fg=RED, font=FONT_SMALL)
        self.err_lbl.pack(pady=(8,0))
        tk.Button(card, text="✅  Update Password", bg=GREEN, fg=BG,
                  font=FONT_BTN, pady=8, cursor="hand2", bd=0,
                  command=self._update).pack(fill="x", pady=(12,0))

    def _update(self):
        cur=self.entries["cur"].get(); new=self.entries["new"].get(); con=self.entries["con"].get()
        if not 4<=len(new)<=20: self.err_lbl.config(text="⚠ 4-20 characters required."); return
        if new!=con: self.err_lbl.config(text="⚠ Passwords do not match."); return
        ok, msg = change_password(self.user["id"], self.user["role"], cur, new)
        if not ok: self.err_lbl.config(text=f"❌  {msg}"); return
        messagebox.showinfo("Done","Password updated!")
        self.destroy()

def _apply_row_colors(tree):
    """Force row tag colors on Windows — must call after tree is packed & visible."""
    # Configure tags directly — works with "default" theme
    tree.tag_configure("full",
                       background="#5C0000",
                       foreground="#FF8080")
    tree.tag_configure("available",
                       background="#2C1810",
                       foreground="#F5E6D3")
    tree.tag_configure("cancelled",
                       background="#2C1810",
                       foreground="#C0392B")
    tree.tag_configure("waitlisted",
                       background="#2C1810",
                       foreground="#8B6F7A")
    tree.tag_configure("highlight",
                       background="#3D1F0D",
                       foreground="#E8A44A")
    # Force Tk to redraw — update() is stronger than update_idletasks()
    tree.update()

def _ask_password(parent, correct_password, on_success):
    win=tk.Toplevel(parent); win.title("Authentication Required")
    win.configure(bg=PANEL); win.resizable(False,False); win.grab_set()
    parent.update_idletasks()
    px,py=parent.winfo_rootx(),parent.winfo_rooty()
    pw,ph=parent.winfo_width(),parent.winfo_height()
    win.geometry(f"340x200+{px+pw//2-170}+{py+ph//2-100}")
    tk.Label(win,text="🔑  Admin Access Required",bg=PANEL,fg=WHITE,font=("Georgia",13,"bold")).pack(pady=(22,4))
    tk.Label(win,text="Enter password to continue:",bg=PANEL,fg=YELLOW,font=FONT_SMALL).pack()
    pw_var=tk.StringVar()
    pw_e=tk.Entry(win,textvariable=pw_var,show="● ",font=FONT_BODY,bg=ACCENT,fg=WHITE,insertbackground=WHITE,width=22)
    pw_e.pack(pady=12,ipady=4); pw_e.focus_set()
    err=tk.Label(win,text="",bg=PANEL,fg=RED,font=FONT_SMALL); err.pack()
    def _check(event=None):
        if pw_var.get()==correct_password: win.destroy(); on_success()
        else: err.config(text="❌  Incorrect password."); pw_e.delete(0,tk.END)
    pw_e.bind("<Return>",_check)
    tk.Button(win,text="Unlock",bg=GREEN,fg="white",font=FONT_BTN,cursor="hand2",command=_check).pack(pady=6)


class BusResApp(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.user=user; self.current_role=user["role"]
        self.title(f"BusRes — {user['username']} ({user['role'].upper()})")
        self.state("zoomed"); self.configure(bg=BG); self.resizable(True,True)
        # Dark theme for all treeviews
        style = ttk.Style(self)
        style.theme_use("default")
        # NO fieldbackground — it blocks tag background colors on Windows
        style.configure("Treeview",
            background=PANEL, foreground=WHITE,
            fieldbackground=PANEL, rowheight=28,
            font=("Segoe UI",10))
        style.configure("Treeview.Heading",
            background=ACCENT, foreground=WHITE,
            font=("Segoe UI",10,"bold"), relief="flat")
        # ONLY map selected state — mapping any other state kills tag colors
        style.map("Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", GOLD)])
        ensure_schema()
        add_user_id_to_bookings()    # add user_id column if missing
        sync_seats_from_bookings()   # sync is_booked from confirmed bookings
        backfill_payments()          # ensure all confirmed bookings have payment records
        self.hash_table=BookingHashTable(); self.passenger_bst=PassengerBST()
        self.waitlist=WaitlistQueue(); self.route_graph=RouteGraph()
        self._load_hash_table(); self._load_bst()
        self._load_waitlist(); self._setup_routes()
        self._build_ui()

    def _load_hash_table(self):
        for b in get_all_bookings(): self.hash_table.insert(b["id"],b)

    def _load_bst(self):
        for b in get_all_bookings(): self.passenger_bst.insert(b["name"],b)

    def _load_waitlist(self):
        for row in get_waitlisted_bookings():
            self.waitlist.enqueue({"name":row["name"],"cnic":row["cnic"],"phone":row["phone"],
                "bus_number":row["bus_number"],"booking_id":row["id"],
                "passenger_id":row["passenger_id"],"bus_id":row["bus_id"]})

    def _setup_routes(self):
        stops=[("Islamabad","Rawalpindi",15),("Islamabad","Murree",60),
               ("Islamabad","Peshawar",170),("Islamabad","Abbottabad",120),
               ("Rawalpindi","Taxila",35),("Rawalpindi","Murree",50),
               ("Rawalpindi","Lahore",375),("Rawalpindi","Attock",90),
               ("Taxila","Attock",45),("Murree","Abbottabad",55),
               ("Peshawar","Attock",95),("Lahore","Multan",330),
               ("Lahore","Faisalabad",130),("Multan","Bahawalpur",100),
               ("Multan","Sukkur",380),("Sukkur","Karachi",470),
               ("Karachi","Hyderabad",160),("Sukkur","Quetta",380),("Quetta","Multan",580)]
        for f,t,d in stops: self.route_graph.add_route(f,t,d)

    def _build_ui(self):
        self._build_sidebar()
        self.main=tk.Frame(self,bg=BG); self.main.pack(side="right",fill="both",expand=True)
        self._show_home()

    def _build_sidebar(self):
        self.sidebar=tk.Frame(self,bg=SIDEBAR,width=220)
        self.sidebar.pack(side="left",fill="y")
        self.sidebar.pack_propagate(False)

        # ── Logo ──────────────────────────────────────────────────────
        tk.Label(self.sidebar,text="🚌  BusRes",bg=SIDEBAR,fg=WHITE,
                 font=("Georgia",16,"bold")).pack(pady=(22,2))
        tk.Label(self.sidebar,text="Bus Reservation System",bg=SIDEBAR,fg=YELLOW,
                 font=("Segoe UI",7)).pack()
        tk.Frame(self.sidebar,bg=ACCENT,height=1).pack(fill="x",pady=10)

        # ── User badge ────────────────────────────────────────────────
        badge=tk.Frame(self.sidebar,bg=ACCENT,padx=10,pady=8)
        badge.pack(fill="x",padx=12,pady=(0,10))
        role_colors={"admin":GOLD,"manager":GREEN,"passenger":BLUE}
        tk.Label(badge,text=self.user["username"],bg=ACCENT,fg=WHITE,
                 font=("Georgia",12,"bold")).pack()
        tk.Label(badge,text=self.user["role"].upper(),bg=ACCENT,
                 fg=role_colors.get(self.current_role,WHITE),
                 font=("Segoe UI",9,"bold")).pack()

        # ── Nav items ─────────────────────────────────────────────────
        if self.current_role=="admin":
            nav=[("📊  Analytics",       self._show_analytics),
                 ("💰  Revenue",          self._show_revenue),
                 ("🎟   Promo Codes",     self._show_promo_codes),
                 ("👥  User Management",  self._show_user_mgmt),
                 ("🚌  All Buses",        self._show_all_buses_admin),
                 ("💳  Payment Methods",  self._show_payment_methods),
                 ("🗺   Route Finder",    self._show_routes),
                 ("📊  Sort & Stats",     self._show_sort_stats),
                 ("⚙    Admin Panel",     self._gate_admin)]
        elif self.current_role=="manager":
            nav=[("🚌  Manage Buses",    self._show_manage_buses),
                 ("➕  Add Bus",         self._show_add_bus),
                 ("💬  Feedback Monitor",self._show_feedback_monitor),
                 ("🔍  Search",          self._show_search),
                 ("🗺   Route Finder",   self._show_routes),
                 ("📊  Sort & Stats",    self._show_sort_stats)]
        else:
            nav=[("🚌  All Buses",       self._show_all_buses_passenger),
                 ("🎫  Book a Seat",      self._show_book_seat),
                 ("🔍  Search",           self._show_search),
                 ("📋  My Bookings",      self._show_my_bookings),
                 ("⏳  My Waitlist",      self._show_my_waitlist),
                 ("⭐  Feedback",         self._show_feedback),
                 ("🗺   Route Finder",   self._show_routes)]

        # ── BOTTOM buttons MUST be packed before nav so they anchor ──
        tk.Frame(self.sidebar,bg=ACCENT,height=1).pack(side="bottom",fill="x")
        tk.Button(self.sidebar,text="→   Logout",
                  bg="#3D0A0A",fg="#FF6B6B",
                  font=("Segoe UI",10,"bold"),bd=0,pady=11,
                  anchor="w",padx=16,cursor="hand2",
                  command=self._logout).pack(side="bottom",fill="x")
        tk.Frame(self.sidebar,bg=ACCENT,height=1).pack(side="bottom",fill="x")
        tk.Button(self.sidebar,text="🔑  Change Password",
                  bg=SIDEBAR,fg=YELLOW,
                  font=("Segoe UI",9,"bold"),bd=0,pady=9,
                  anchor="w",padx=16,cursor="hand2",
                  command=self._change_pw).pack(side="bottom",fill="x")

        # ── Divider then nav items ────────────────────────────────────
        tk.Frame(self.sidebar,bg=ACCENT,height=1).pack(fill="x",padx=10,pady=(4,0))
        for label,cmd in nav:
            tk.Button(self.sidebar,text=label,
                      bg=SIDEBAR,fg=WHITE,font=("Segoe UI",10),
                      bd=0,pady=10,activebackground=ACCENT,activeforeground=GOLD,
                      anchor="w",padx=16,cursor="hand2",
                      command=cmd).pack(fill="x")
    def _change_pw(self): ChangePasswordWindow(self,self.user)
    def _logout(self):
        if messagebox.askyesno("Logout","Are you sure you want to logout?"):
            self.destroy(); LoginWindow().mainloop()
    def _clear(self):
        for w in self.main.winfo_children(): w.destroy()
    def _heading(self,title,subtitle=""):
        tk.Label(self.main,text=title,bg=BG,fg=WHITE,font=FONT_TITLE).pack(pady=(18,0),padx=24,anchor="w")
        if subtitle: tk.Label(self.main,text=subtitle,bg=BG,fg=YELLOW,font=FONT_SMALL).pack(padx=24,anchor="w",pady=(0,8))
    def _scrollable(self):
        canvas=tk.Canvas(self.main,bg=BG,highlightthickness=0)
        vsb=ttk.Scrollbar(self.main,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set); vsb.pack(side="right",fill="y")
        canvas.pack(side="left",fill="both",expand=True)
        wrap=tk.Frame(canvas,bg=BG); wid=canvas.create_window((0,0),window=wrap,anchor="nw")
        wrap.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",lambda e:canvas.itemconfig(wid,width=e.width))
        return wrap
    def _show_home(self):
        if self.current_role=="admin": self._show_analytics()
        elif self.current_role=="manager": self._show_manage_buses()
        else: self._show_all_buses_passenger()
    def _gate_waitlist(self): _ask_password(self,ADMIN_PASSWORD,self._show_waitlist_admin)
    def _gate_admin(self): _ask_password(self,ADMIN_PASSWORD,self._show_admin_panel)
    def _export_csv(self):
        ok=export_bookings_to_csv()
        if ok:
            path=r"D:\BusSeatReservation\bookings_export.csv"
            try: os.startfile(path)
            except: messagebox.showinfo("Export",f"Exported to {path}")
        else: messagebox.showwarning("Export","No bookings to export.")

    # ADMIN PAGES
    def _show_analytics(self):
        self._clear(); self._heading("Analytics Dashboard","Live overview of buses and bookings")
        wrap=self._scrollable(); stats=get_analytics_stats()
        cards_data=[("🚌","Total Buses",stats["total_buses"],GOLD,"%d"),
                    ("🎫","Total Bookings",stats["total_bookings"],GREEN,"%d"),
                    ("📈","Avg Fill Rate",float(stats["fill_rate"]),YELLOW,"%.1f%%"),
                    ("🗺","Active Routes",stats["active_routes"],BLUE,"%d")]
        cards_row=tk.Frame(wrap,bg=BG); cards_row.pack(fill="x",padx=24,pady=(8,16))
        card_widgets=[]
        for icon,label,target,color,fmt in cards_data:
            card=tk.Frame(cards_row,bg=CARD1,padx=20,pady=18)
            card.pack(side="left",expand=True,fill="both",padx=6)
            tk.Label(card,text=icon,font=("Segoe UI",22),bg=CARD1,fg=color).pack()
            num_lbl=tk.Label(card,text="0",font=FONT_CARD,bg=CARD1,fg=color); num_lbl.pack()
            tk.Label(card,text=label,font=("Segoe UI",10),bg=CARD1,fg=WHITE).pack()
            card_widgets.append((num_lbl,target,fmt))
        def _animate(step=0):
            steps=30
            if step<=steps:
                for lbl,target,fmt in card_widgets:
                    val=target*step/steps
                    try: lbl.config(text=fmt%val)
                    except: lbl.config(text=str(int(val)))
                wrap.after(30,lambda:_animate(step+1))
        wrap.after(100,_animate)
        charts_row=tk.Frame(wrap,bg=BG); charts_row.pack(fill="x",padx=24,pady=8)
        def _bar(parent,title,data,key_col,val_col,color):
            frame=tk.Frame(parent,bg=PANEL,padx=16,pady=14)
            frame.pack(side="left",fill="both",expand=True,padx=6)
            tk.Label(frame,text=title,font=("Georgia",11,"bold"),bg=PANEL,fg=WHITE).pack(anchor="w",pady=(0,8))
            if not data: tk.Label(frame,text="No data yet",bg=PANEL,fg=YELLOW,font=FONT_SMALL).pack(); return
            max_val=max((d[val_col] for d in data),default=1) or 1
            for d in data[:25]:
                row=tk.Frame(frame,bg=PANEL); row.pack(fill="x",pady=2)
                tk.Label(row,text=str(d[key_col])[:12],bg=PANEL,fg=WHITE,font=FONT_SMALL,width=14,anchor="w").pack(side="left")
                bar_w=max(int(180*d[val_col]/max_val),4)
                tk.Frame(row,bg=color,width=bar_w,height=16).pack(side="left",padx=(2,4))
                tk.Label(row,text=str(d[val_col]),bg=PANEL,fg=color,font=FONT_SMALL).pack(side="left")
        _bar(charts_row,"📊  Bookings per Bus",get_bookings_per_bus(),"bus_number","bookings",GOLD)
        raw_routes = get_bookings_per_route()
        seen = {}
        for r in raw_routes:
            if r["route"] in seen: seen[r["route"]]["bookings"] += r["bookings"]
            else: seen[r["route"]] = dict(r)
        deduped = sorted(seen.values(), key=lambda x: x["bookings"], reverse=True)
        _bar(charts_row,"📊  Bookings per Route",deduped,"route","bookings",GREEN)

    def _show_revenue(self):
        self._clear(); self._heading("Revenue Tracking","Income from all confirmed bookings")
        wrap=self._scrollable()
        backfill_payments()
        stats=get_revenue_stats(); bus_rev=get_revenue_per_bus()
        top=tk.Frame(wrap,bg=BG); top.pack(fill="x",padx=24,pady=(8,16))
        for icon,label,value,color in [("💰","Total Revenue",f"PKR {stats['total_revenue']:,.2f}",GOLD),
                                        ("🎫","Paid Bookings",str(stats['paid_bookings']),GREEN)]:
            c=tk.Frame(top,bg=CARD1,padx=28,pady=18); c.pack(side="left",padx=8)
            tk.Label(c,text=icon,font=("Segoe UI",20),bg=CARD1,fg=color).pack()
            tk.Label(c,text=value,font=("Georgia",22,"bold"),bg=CARD1,fg=color).pack()
            tk.Label(c,text=label,font=FONT_SMALL,bg=CARD1,fg=WHITE).pack()
        tk.Label(wrap,text="Revenue per Bus",font=FONT_HEAD,bg=BG,fg=WHITE).pack(anchor="w",padx=24,pady=(8,4))
        cols=("Bus","Bookings","Revenue (PKR)")
        t_frame=tk.Frame(wrap,bg=BG); t_frame.pack(fill="x",padx=24)
        tree=ttk.Treeview(t_frame,columns=cols,show="headings",height=10)
        for col,w in zip(cols,[40,90,180,130,60,70,80,100]): tree.heading(col,text=col); tree.column(col,width=w,anchor="w")
        tree.tag_configure("highlight",background=CARD1,foreground=GOLD)
        bus_rev = sorted(bus_rev, key=lambda x: x["bus_number"])
        for r in bus_rev:
            tree.insert("","end",values=(r["bus_number"],r["bookings"],f"{r['revenue']:,.2f}"),
                        tags=("highlight",) if r["revenue"]>0 else ())
        vsb=ttk.Scrollbar(t_frame,orient="vertical",command=tree.yview)
        tree.configure(yscrollcommand=vsb.set); tree.pack(side="left",fill="both",expand=True); vsb.pack(side="right",fill="y")
        tk.Label(wrap,text="Revenue per Bus (chart)",font=FONT_HEAD,bg=BG,fg=WHITE).pack(anchor="w",padx=24,pady=(16,4))
        chart=tk.Frame(wrap,bg=PANEL,padx=16,pady=14); chart.pack(fill="x",padx=24,pady=(0,16))
        if bus_rev:
            max_rev=max((r["revenue"] for r in bus_rev),default=1) or 1
            bus_rev = sorted(bus_rev, key=lambda x: x["bus_number"])
            for r in bus_rev[:25]:
                row=tk.Frame(chart,bg=PANEL); row.pack(fill="x",pady=2)
                tk.Label(row,text=r["bus_number"],bg=PANEL,fg=WHITE,font=FONT_SMALL,width=10,anchor="w").pack(side="left")
                bar_w=max(int(300*r["revenue"]/max_rev),4)
                tk.Frame(row,bg=GOLD,width=bar_w,height=18).pack(side="left",padx=2)
                tk.Label(row,text=f"PKR {r['revenue']:,.0f}",bg=PANEL,fg=GOLD,font=FONT_SMALL).pack(side="left",padx=4)

    def _show_promo_codes(self):
        self._clear(); self._heading("Promo Codes","Create and manage discount codes")
        tb=tk.Frame(self.main,bg=BG); tb.pack(fill="x",padx=24,pady=(4,8))
        tree_holder=[None]
        for label,color,cmd in [("🔄  Refresh",ACCENT,lambda:self._show_promo_codes()),
                                  ("➕  New Code",GREEN,self._new_promo_popup),
                                  ("⚡  Toggle",YELLOW,lambda:self._toggle_promo(tree_holder[0])),
                                  ("🗑   Delete",RED,lambda:self._delete_promo(tree_holder[0]))]:
            tk.Button(tb,text=label,bg=color,fg=WHITE if color!=YELLOW else BG,
                      font=FONT_BTN,padx=10,pady=5,cursor="hand2",bd=0,command=cmd).pack(side="left",padx=4)
        cols=("ID","Code","Discount %","Max Uses","Used","Active")
        t_f=tk.Frame(self.main,bg=BG); t_f.pack(fill="both",expand=True,padx=24)
        tree=ttk.Treeview(t_f,columns=cols,show="headings",height=20)
        tree_holder[0]=tree
        vsb=ttk.Scrollbar(t_f,orient="vertical",command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        for c,w in zip(cols,[50,120,100,100,80,80]): tree.heading(c,text=c); tree.column(c,width=w,anchor="w")
        tree.tag_configure("inactive",foreground="#888")
        for p in get_all_promo_codes():
            tree.insert("","end",tags=() if p["active"] else ("inactive",),
                        values=(p["id"],p["code"],f"{p['discount_pct']}%",p["max_uses"],p["used"],"✅ Yes" if p["active"] else "❌  No"))
        tree.pack(side="left",fill="both",expand=True); vsb.pack(side="right",fill="y")

    def _new_promo_popup(self):
        win=tk.Toplevel(self); win.title("New Promo Code"); win.configure(bg=BG)
        win.resizable(False,False); win.grab_set()
        tk.Label(win,text="🎟  New Promo Code",font=FONT_HEAD,bg=BG,fg=WHITE).pack(pady=(20,4))
        card=tk.Frame(win,bg=PANEL,padx=24,pady=18); card.pack(padx=20,fill="x")
        entries={}
        for label,key,ph in [("Code","code","e.g. SAVE20"),("Discount %","disc","e.g. 20"),("Max Uses","uses","e.g. 100")]:
            tk.Label(card,text=label,bg=PANEL,fg=WHITE,font=FONT_BODY).pack(anchor="w",pady=(6,1))
            e=tk.Entry(card,font=FONT_BODY,bg=ACCENT,fg=WHITE,insertbackground=WHITE,width=28)
            e.pack(fill="x",ipady=5); entries[key]=e
        err=tk.Label(card,text="",bg=PANEL,fg=RED,font=FONT_SMALL); err.pack()
        def _create():
            code=entries["code"].get().strip(); disc=entries["disc"].get().strip(); uses=entries["uses"].get().strip()
            if not code: err.config(text="⚠ Enter a code."); return
            if not disc.isdigit() or not 1<=int(disc)<=100: err.config(text="⚠ Discount 1-100."); return
            if not uses.isdigit() or int(uses)<1: err.config(text="⚠ Max uses ≥ 1."); return
            try: create_promo(code,int(disc),int(uses)); win.destroy(); self._show_promo_codes()
            except Exception as ex: err.config(text=f"❌  {ex}")
        tk.Button(card,text="✅  Create Code",bg=GREEN,fg=BG,font=FONT_BTN,pady=7,cursor="hand2",bd=0,command=_create).pack(fill="x",pady=(10,0))
        win.update_idletasks()
        w=400; h=win.winfo_reqheight()+24
        x=(win.winfo_screenwidth()-w)//2; y=(win.winfo_screenheight()-h)//2
        win.geometry(f"{w}x{h}+{x}+{y}")

    def _toggle_promo(self,tree):
        sel=tree.selection() if tree else []
        if not sel: messagebox.showwarning("Select","Select a promo code first."); return
        toggle_promo(tree.item(sel[0])["values"][0]); self._show_promo_codes()

    def _delete_promo(self,tree):
        sel=tree.selection() if tree else []
        if not sel: messagebox.showwarning("Select","Select a promo code first."); return
        if messagebox.askyesno("Delete","Delete this promo code?"):
            delete_promo(tree.item(sel[0])["values"][0]); self._show_promo_codes()

    def _show_user_mgmt(self):
        self._clear(); self._heading("User Management","View, add, and remove user accounts")
        tb=tk.Frame(self.main,bg=BG); tb.pack(fill="x",padx=24,pady=(4,8))
        tree_ref=[None]
        tk.Button(tb,text="🔄  Refresh",bg=ACCENT,fg=WHITE,font=FONT_BTN,padx=10,pady=5,
                  cursor="hand2",bd=0,command=self._show_user_mgmt).pack(side="left",padx=4)
        tk.Button(tb,text="🗑   Delete Selected",bg=RED,fg=WHITE,font=FONT_BTN,padx=10,pady=5,
                  cursor="hand2",bd=0,command=lambda:self._delete_user(tree_ref[0])).pack(side="left",padx=4)
        cols=("ID","Username","Role","Email","Created")
        t_f=tk.Frame(self.main,bg=BG); t_f.pack(fill="both",expand=True,padx=24)
        tree=ttk.Treeview(t_f,columns=cols,show="headings",height=22); tree_ref[0]=tree
        vsb=ttk.Scrollbar(t_f,orient="vertical",command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        for c,w in zip(cols,[50,140,100,200,160]): tree.heading(c,text=c); tree.column(c,width=w,anchor="w")
        for tag,color in [("admin",GOLD),("manager",GREEN),("passenger",BLUE)]: tree.tag_configure(tag,foreground=color)
        # Show hardcoded display names for admin/manager rows
        for u in get_all_users():
            display = u["username"]
            if u["role"] == "admin":   display = "Maheen"
            elif u["role"] == "manager": display = "Kinza"
            tree.insert("","end",tags=(u["role"],),values=(u["id"],display,u["role"].upper(),u.get("email",""),str(u.get("created_at",""))[:16]))
        # Also add hardcoded admin+manager rows if not in DB
        ids_in_db = [u["role"] for u in get_all_users()]
        if "admin" not in ids_in_db:
            tree.insert("","end",tags=("admin",),values=(0,"Maheen","ADMIN","admin@busres.com","hardcoded"))
        if "manager" not in ids_in_db:
            tree.insert("","end",tags=("manager",),values=(-1,"Kinza","MANAGER","manager@busres.com","hardcoded"))
        tree.pack(side="left",fill="both",expand=True); vsb.pack(side="right",fill="y")

    def _delete_user(self,tree):
        if not tree: return
        sel=tree.selection()
        if not sel: messagebox.showwarning("Select","Select a user first."); return
        uid=tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete",f"Delete user {uid}?"): delete_user(uid); self._show_user_mgmt()

    def _show_all_buses_admin(self):
        self._clear(); self._heading("All Buses","Read-only overview of all buses")

        # Search bar
        sb = tk.Frame(self.main, bg=BG)
        sb.pack(fill="x", padx=24, pady=(4,6))
        tk.Label(sb, text="🔍", bg=BG, fg=WHITE, font=FONT_BODY).pack(side="left")
        q_var = tk.StringVar()
        tk.Entry(sb, textvariable=q_var, font=FONT_BODY, bg=ACCENT, fg=WHITE,
                 insertbackground=WHITE, width=30).pack(side="left", padx=6, ipady=4)
        col_var = tk.StringVar(value="All Columns")
        ttk.Combobox(sb, textvariable=col_var,
                     values=["All Columns","Bus No","Route","Status"],
                     width=13, state="readonly").pack(side="left")
        tk.Button(sb, text="🔄 Refresh", bg=ACCENT, fg=WHITE, font=FONT_BTN,
                  bd=0, cursor="hand2", padx=8, pady=4,
                  command=self._show_all_buses_admin).pack(side="right", padx=4)

        cols = ("ID","Bus No","Route","Departure","Seats","Booked","Available","Price","Status")
        t_f  = tk.Frame(self.main, bg=BG)
        t_f.pack(fill="both", expand=True, padx=24, pady=(0,8))
        tree = ttk.Treeview(t_f, columns=cols, show="headings", height=24)
        vsb  = ttk.Scrollbar(t_f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        for c,w in zip(cols,[40,80,170,130,55,65,75,95,80]):
            tree.heading(c,text=c); tree.column(c,width=w,anchor="w")
        tree.tag_configure("full", background="#5C0000", foreground="#FF8080")

        all_buses = get_buses_with_stats()

        def _populate(data):
            tree.delete(*tree.get_children())
            for b in data:
                status = "FULL" if b["available"]==0 else "Available"
                tag    = ("full",) if b["available"]==0 else ()
                tree.insert("","end", tags=tag, values=(
                    b["id"], b["bus_number"], b["route"],
                    str(b["departure_time"])[:16],
                    b["total_seats"], b["booked"], b["available"],
                    f"PKR {b['price']:,}", status))
            tree.after(100, lambda: _apply_row_colors(tree))

        _populate(all_buses)

        def _filter(*_):
            q  = q_var.get().strip().lower()
            cf = col_var.get()
            if not q: _populate(all_buses); return
            col_map = {"Bus No":"bus_number","Route":"route",
                       "Status": lambda b: "full" if b["available"]==0 else "available"}
            filtered = []
            for b in all_buses:
                if cf == "All Columns":
                    hay = f"{b['bus_number']} {b['route']}".lower()
                elif cf == "Status":
                    hay = "full" if b["available"]==0 else "available"
                else:
                    hay = str(b.get(col_map.get(cf,"route"),"")).lower()
                if q in hay: filtered.append(b)
            _populate(filtered)

        q_var.trace_add("write", _filter)
        col_var.trace_add("write", _filter)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def _show_payment_methods(self):
        self._clear(); self._heading("Payment Methods","Enable / disable accepted payment methods")
        wrap=tk.Frame(self.main,bg=BG); wrap.pack(padx=40,pady=16,fill="x")
        def _refresh():
            for w in wrap.winfo_children(): w.destroy()
            for pm in get_payment_methods():
                row=tk.Frame(wrap,bg=PANEL,padx=20,pady=14); row.pack(fill="x",pady=4)
                icon="💳" if "Card" in pm["name"] else "🏦" if "Banking" in pm["name"] else "📱" if "Wallet" in pm["name"] else "🏧"
                tk.Label(row,text=f"{icon}  {pm['name']}",bg=PANEL,fg=WHITE,font=("Segoe UI",12)).pack(side="left")
                tk.Label(row,text="Enabled ✅" if pm["enabled"] else "Disabled ❌ ",
                         bg=PANEL,fg=GREEN if pm["enabled"] else RED,font=("Segoe UI",11)).pack(side="right",padx=12)
                tk.Button(row,text="Toggle",bg=ACCENT,fg=WHITE,font=FONT_BTN,cursor="hand2",bd=0,
                          command=lambda mid=pm["id"]:[toggle_payment_method(mid),_refresh()]).pack(side="right")
            tk.Label(wrap,text="ⓘ  Changes take effect immediately for new bookings.",bg=BG,fg=YELLOW,font=FONT_SMALL).pack(anchor="w",pady=(12,0))
        _refresh()

    def _show_admin_panel(self):
        self._clear(); self._heading("Admin Panel — All Bookings",
                                     "Manage bookings •  Search •  Export CSV")
        # ── Top toolbar: search + export ─────────────────────────────
        toolbar=tk.Frame(self.main,bg=BG); toolbar.pack(fill="x",padx=20,pady=(0,4))
        tk.Label(toolbar,text="🔍",bg=BG,fg=WHITE,font=FONT_SMALL).pack(side="left")
        search_var=tk.StringVar()
        tk.Entry(toolbar,textvariable=search_var,font=FONT_BODY,bg=ACCENT,fg=WHITE,
                 insertbackground=WHITE,width=28).pack(side="left",ipady=4,padx=(4,8))
        col_filter_var=tk.StringVar(value="All Columns")
        ttk.Combobox(toolbar,textvariable=col_filter_var,
                     values=["All Columns","ID","Passenger","CNIC","Seat","Bus","Date","Status"],
                     width=13,state="readonly").pack(side="left")

        # Waitlist button — opens popup
        tk.Frame(toolbar,bg=ACCENT,width=1).pack(side="left",fill="y",padx=8)
        tk.Button(toolbar,text="⏳  Waitlist",bg=YELLOW,fg=BG,font=FONT_BTN,
                  cursor="hand2",bd=0,padx=10,pady=4,
                  command=lambda:self._waitlist_popup()).pack(side="left",padx=2)
        # Export CSV on the right
        tk.Button(toolbar,text="📁  Export CSV",bg=GREEN,fg=BG,font=FONT_BTN,
                  cursor="hand2",bd=0,padx=10,pady=4,
                  command=self._export_csv).pack(side="right",padx=4)
        filter_frame = toolbar  # alias for trace callbacks
        btn_frame=tk.Frame(self.main,bg=BG); btn_frame.pack(side="bottom",pady=4)
        tree_ref=[None]
        cols=("ID","Passenger","CNIC","Seat","Bus","Date","Status")
        t_frame=tk.Frame(self.main,bg=BG); t_frame.pack(fill="both",expand=True,padx=20,pady=(0,2))
        tree=ttk.Treeview(t_frame,columns=cols,show="headings",height=20)
        tree_ref[0]=tree
        vsb=ttk.Scrollbar(t_frame,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right",fill="y"); tree.pack(side="left",fill="both",expand=True)
        for c,w in zip(cols,[50,160,130,60,110,150,90]): tree.heading(c,text=c); tree.column(c,width=w,anchor="w")
        tree.tag_configure("cancelled",foreground=RED); tree.tag_configure("waitlisted",foreground=PURPLE)
        live_bookings=get_all_bookings()
        def _populate(rows):
            tree.delete(*tree.get_children())
            for b in rows:
                st=str(b.get("status","")).lower(); tag=st if st in ("cancelled","waitlisted") else ""
                tree.insert("","end",tags=((tag,) if tag else ()),values=(b["id"],b["name"],b["cnic"],b.get("seat_number","N/A"),b.get("bus_number","N/A"),b["booking_date"],b["status"]))
            tree.update_idletasks()
            _apply_row_colors(tree)
        col_idx_map={"ID":"id","Passenger":"name","CNIC":"cnic","Seat":"seat_number","Bus":"bus_number","Date":"booking_date","Status":"status"}
        def _apply(*_):
            q=search_var.get().strip().lower(); cf=col_filter_var.get()
            if not q: _populate(live_bookings); return
            _populate([b for b in live_bookings if q in (" ".join(str(v).lower() for v in b.values()) if cf=="All Columns" else str(b.get(col_idx_map.get(cf,"name"),"")).lower())])
        search_var.trace_add("write",_apply); col_filter_var.trace_add("write",_apply); _populate(live_bookings)
        def _update_live(bid,st):
            for b in live_bookings:
                if str(b["id"])==str(bid): b["status"]=st; break
        def cancel_sel():
            sel=tree.selection()
            if not sel: messagebox.showwarning("Select","Select a booking."); return
            bid=tree.item(sel[0])["values"][0]
            if str(tree.item(sel[0])["values"][6]).lower()=="cancelled": messagebox.showinfo("Info","Already cancelled."); return
            if messagebox.askyesno("Confirm",f"Cancel booking {bid}?"):
                cancel_booking(bid); _update_live(bid,"cancelled"); tree.set(sel[0],"Status","cancelled"); tree.item(sel[0],tags=("cancelled",))
                updated = get_booking_by_id(bid)
                self.hash_table.insert(bid, updated)
                self.passenger_bst.insert(updated["name"], updated)
        def confirm_sel():
            sel=tree.selection()
            if not sel: messagebox.showwarning("Select","Select a booking."); return
            bid=tree.item(sel[0])["values"][0]
            if str(tree.item(sel[0])["values"][6]).lower()=="confirmed": messagebox.showinfo("Info","Already confirmed."); return
            if messagebox.askyesno("Confirm",f"Confirm booking {bid}?"):
                from database import get_booking_by_id, is_seat_taken
                booking = get_booking_by_id(bid)
                if booking and is_seat_taken(booking["seat_id"], bid):
                    messagebox.showwarning("Conflict","❌  This seat is already taken by another confirmed booking!"); return
                update_booking_status(bid,"confirmed"); _update_live(bid,"confirmed"); tree.set(sel[0],"Status","confirmed"); tree.item(sel[0],tags=())
                self.hash_table.insert(bid, get_booking_by_id(bid))

        tk.Button(btn_frame,text="❌   Cancel Selected",bg=RED,fg="white",font=FONT_BTN,cursor="hand2",command=cancel_sel).pack(side="left",padx=8)
        tk.Button(btn_frame,text="✅  Confirm Selected",bg=GREEN,fg="white",font=FONT_BTN,cursor="hand2",command=confirm_sel).pack(side="left",padx=8)

    def _show_waitlist_admin(self):
        self._clear(); self._heading("Waitlist Queue")
        import re as _re
        buses=get_all_buses(); bus_map={f"{b['bus_number']} — {b['route']}":b for b in buses}
        frame=tk.Frame(self.main,bg=PANEL,padx=24,pady=20); frame.pack(padx=30,fill="x")
        tk.Label(frame,text="Add Passenger to Waitlist:",bg=PANEL,fg=WHITE,font=FONT_HEAD).pack(anchor="w")
        def _field(label):
            tk.Label(frame,text=label,bg=PANEL,fg=WHITE,font=FONT_BODY).pack(anchor="w",pady=(8,0))
            e=tk.Entry(frame,font=FONT_BODY,bg=ACCENT,fg=WHITE,insertbackground=WHITE,width=35); e.pack(anchor="w",ipady=4)
            err=tk.Label(frame,text="",bg=PANEL,fg=RED,font=FONT_SMALL); err.pack(anchor="w")
            return e,err
        name_e,name_err=_field("Name:"); cnic_e,cnic_err=_field("CNIC (e.g. 12345-1234567-1):")
        phone_e,phone_err=_field("Phone (e.g. 0301-1234567):")
        tk.Label(frame,text="Preferred Bus:",bg=PANEL,fg=WHITE,font=FONT_BODY).pack(anchor="w",pady=(8,0))
        bus_var=tk.StringVar()
        bus_cb=ttk.Combobox(frame,textvariable=bus_var,values=list(bus_map.keys()),width=38,state="readonly"); bus_cb.pack(anchor="w")
        bus_err=tk.Label(frame,text="",bg=PANEL,fg=RED,font=FONT_SMALL); bus_err.pack(anchor="w")
        list_frame=tk.Frame(self.main,bg=BG); list_frame.pack(padx=30,pady=10,fill="x")
        queue_lbl=tk.Label(list_frame,text="",bg=BG,fg=YELLOW,font=FONT_BODY,justify="left"); queue_lbl.pack(anchor="w")
        def _log(action,name,phone):
            try:
                exists=os.path.isfile(WAITLIST_LOG)
                with open(WAITLIST_LOG,"a",newline="",encoding="utf-8") as f:
                    w=csv.DictWriter(f,fieldnames=["datetime","action","name","phone"])
                    if not exists: w.writeheader()
                    w.writerow({"datetime":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"action":action,"name":name,"phone":phone})
            except: pass
        def refresh_list():
            items=self.waitlist.get_all()
            if items: queue_lbl.config(text=f"Queue ({len(items)} waiting):\n"+"\n".join(f"  {i+1}. {p['name']}  |  {p.get('bus_number','?')}  |  ID:{p.get('booking_id','?')}" for i,p in enumerate(items)))
            else: queue_lbl.config(text="Queue is empty.")
        def add_to_waitlist():
            for lbl in (name_err,cnic_err,phone_err,bus_err): lbl.config(text="")
            n=name_e.get().strip(); c=cnic_e.get().strip(); p=phone_e.get().strip(); b=bus_var.get()
            ok=True
            if not n or len(n)<2: name_err.config(text="⚠ Name required."); ok=False
            if not _re.fullmatch(r'\d{5}-\d{7}-\d',c): cnic_err.config(text="⚠ CNIC format: 12345-1234567-1"); ok=False
            if not _re.fullmatch(r'0\d{3}-\d{7}',p): phone_err.config(text="⚠ Phone format: 0301-1234567"); ok=False
            if not b: bus_err.config(text="⚠ Select a bus."); ok=False
            if not ok: return
            if get_passenger_by_cnic(c): cnic_err.config(text="⚠ CNIC already registered."); return
            bus_obj=bus_map[b]; pid=add_passenger(n,c,"",p); bid=add_waitlist_booking(pid,bus_obj["id"])
            entry={"name":n,"cnic":c,"phone":p,"bus_number":bus_obj["bus_number"],"booking_id":bid,"passenger_id":pid,"bus_id":bus_obj["id"]}
            self.waitlist.enqueue(entry)
            wl_rec={"id":bid,"name":n,"cnic":c,"seat_number":"N/A","bus_number":bus_obj["bus_number"],"booking_date":str(datetime.now()),"status":"waitlisted"}
            self.hash_table.insert(bid,wl_rec); self.passenger_bst.insert(n,wl_rec)
            _log("WAITLISTED",n,p)
            for e in (name_e,cnic_e,phone_e): e.delete(0,tk.END)
            bus_var.set(""); refresh_list()
        def serve_next():
            passenger=self.waitlist.peek()
            if not passenger: messagebox.showinfo("Empty","Waitlist is empty."); return
            bid=passenger.get("booking_id"); result=serve_waitlist_booking(bid) if bid else None
            if result is None: messagebox.showwarning("No Seat",f"No free seat on {passenger.get('bus_number')} yet."); return
            self.waitlist.dequeue(); self.hash_table.insert(bid,result)
            def _bst_upd(node,key,data):
                if node is None: return
                if node.key==key: node.data=data; return
                if key<node.key: _bst_upd(node.left,key,data)
                else: _bst_upd(node.right,key,data)
            if self.passenger_bst._search(self.passenger_bst.root,passenger["name"]):
                _bst_upd(self.passenger_bst.root,passenger["name"],result)
            else: self.passenger_bst.insert(passenger["name"],result)
            _log("SERVED",passenger["name"],passenger.get("phone",""))
            messagebox.showinfo("Served",f"✅ {result['name']} →  Seat {result['seat_number']} on {result['bus_number']}"); refresh_list()
        btn_row=tk.Frame(frame,bg=PANEL); btn_row.pack(anchor="w",pady=12)
        tk.Button(btn_row,text="Add to Waitlist",bg=ACCENT,fg=WHITE,font=FONT_BTN,cursor="hand2",command=add_to_waitlist).pack(side="left",padx=(0,10))
        tk.Button(btn_row,text="Serve Next ▶",bg=GREEN,fg=WHITE,font=FONT_BTN,cursor="hand2",command=serve_next).pack(side="left")
        tk.Button(btn_row,text="📄Open Log",bg=YELLOW,fg=BG,font=FONT_BTN,cursor="hand2",
                  command=lambda:os.startfile(WAITLIST_LOG) if os.path.isfile(WAITLIST_LOG) else messagebox.showinfo("Log","No log yet.")).pack(side="left",padx=(10,0))
        refresh_list()

    def _waitlist_popup(self):
        """Full waitlist management in a popup — password gated."""
        _ask_password(self, ADMIN_PASSWORD, self._open_waitlist_popup)

    def _open_waitlist_popup(self):
        import re as _re
        win = tk.Toplevel(self)
        win.title("Waitlist Management")
        win.configure(bg=BG)
        win.geometry("720x680")
        win.grab_set()
        x = (self.winfo_screenwidth()  - 720) // 2
        y = (self.winfo_screenheight() - 680) // 2
        win.geometry(f"720x680+{x}+{y}")

        # ── Header ────────────────────────────────────────────────────
        hdr = tk.Frame(win, bg=ACCENT, padx=20, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⏳  Waitlist Management",
                 bg=ACCENT, fg=WHITE, font=("Georgia",14,"bold")).pack(side="left")
        tk.Button(hdr, text="✖  Close", bg=RED, fg=WHITE,
                  font=FONT_BTN, bd=0, cursor="hand2",
                  command=win.destroy).pack(side="right")

        # ── Queue display ─────────────────────────────────────────────
        queue_frame = tk.Frame(win, bg=PANEL, padx=16, pady=10)
        queue_frame.pack(fill="x", padx=16, pady=(10,4))
        tk.Label(queue_frame, text="Current Queue",
                 bg=PANEL, fg=YELLOW, font=FONT_HEAD).pack(anchor="w")
        queue_lbl = tk.Label(queue_frame, text="Loading...",
                             bg=PANEL, fg=WHITE, font=FONT_BODY,
                             justify="left", wraplength=660)
        queue_lbl.pack(anchor="w", pady=(4,0))

        def refresh_queue():
            items = self.waitlist.get_all()
            if items:
                parts = []
                for i, p in enumerate(items):
                    parts.append(
                        f"  {i+1}.  {p['name']}  |  Phone: {p.get('phone','—')}  |  "
                        f"Bus: {p.get('bus_number','?')}  |  ID: {p.get('booking_id','?')}")
                queue_lbl.config(
                    text="Queue — {} passenger(s) waiting:\n{}".format(
                        len(items), "\n".join(parts)),
                    fg=WHITE)
            else:
                queue_lbl.config(text="Queue is empty.", fg=YELLOW)

        # ── Add to Waitlist form ───────────────────────────────────────
        sep = tk.Frame(win, bg=ACCENT, height=1)
        sep.pack(fill="x", padx=16, pady=(6,0))

        form_outer = tk.Frame(win, bg=BG)
        form_outer.pack(fill="both", expand=True, padx=16, pady=6)

        # Scrollable form
        canvas2 = tk.Canvas(form_outer, bg=BG, highlightthickness=0)
        vsb2    = ttk.Scrollbar(form_outer, orient="vertical", command=canvas2.yview)
        canvas2.configure(yscrollcommand=vsb2.set)
        vsb2.pack(side="right", fill="y")
        canvas2.pack(side="left", fill="both", expand=True)
        form = tk.Frame(canvas2, bg=BG)
        w2id = canvas2.create_window((0,0), window=form, anchor="nw")
        form.bind("<Configure>",
            lambda e: canvas2.configure(scrollregion=canvas2.bbox("all")))
        canvas2.bind("<Configure>",
            lambda e: canvas2.itemconfig(w2id, width=e.width))

        tk.Label(form, text="Add Passenger to Waitlist",
                 bg=BG, fg=WHITE, font=FONT_HEAD).pack(anchor="w", pady=(8,6))

        buses   = get_all_buses()
        bus_map = {f"{b['bus_number']} — {b['route']}": b for b in buses}

        entries   = {}
        err_labels = {}

        fields = [
            ("Full Name",                    "name",  r'.{2,}',         "Name must be at least 2 characters."),
            ("CNIC  (e.g. 12345-1234567-1)", "cnic",  r'\d{5}-\d{7}-\d',"CNIC format: 12345-1234567-1"),
            ("Phone  (e.g. 0301-1234567)",   "phone", r'0\d{3}-\d{7}',  "Phone format: 0301-1234567"),
        ]
        for label, key, pattern, msg in fields:
            tk.Label(form, text=label, bg=BG, fg=WHITE,
                     font=FONT_BODY).pack(anchor="w", pady=(6,0))
            e = tk.Entry(form, font=FONT_BODY, bg=ACCENT, fg=WHITE,
                         insertbackground=WHITE, width=46)
            e.pack(anchor="w", ipady=5, fill="x")
            err = tk.Label(form, text="", bg=BG, fg=RED, font=FONT_SMALL)
            err.pack(anchor="w")
            entries[key]    = e
            err_labels[key] = (err, pattern, msg)

        tk.Label(form, text="Preferred Bus:", bg=BG, fg=WHITE,
                 font=FONT_BODY).pack(anchor="w", pady=(6,0))
        bus_var = tk.StringVar()
        bus_cb  = ttk.Combobox(form, textvariable=bus_var,
                               values=list(bus_map.keys()),
                               width=46, state="readonly")
        bus_cb.pack(anchor="w")
        bus_err = tk.Label(form, text="", bg=BG, fg=RED, font=FONT_SMALL)
        bus_err.pack(anchor="w")

        form_err = tk.Label(form, text="", bg=BG, fg=RED, font=FONT_BODY)
        form_err.pack(anchor="w", pady=(4,0))

        def _log(action, name, phone):
            try:
                exists = os.path.isfile(WAITLIST_LOG)
                with open(WAITLIST_LOG, "a", newline="", encoding="utf-8") as f:
                    import csv
                    w = csv.DictWriter(f, fieldnames=["datetime","action","name","phone"])
                    if not exists: w.writeheader()
                    w.writerow({"datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "action": action, "name": name, "phone": phone})
            except: pass

        def add_to_waitlist():
            # Clear errors
            for err, _, _ in err_labels.values(): err.config(text="")
            bus_err.config(text=""); form_err.config(text="")

            vals = {k: entries[k].get().strip() for k in entries}
            b    = bus_var.get()
            ok   = True

            for key, (err_lbl, pattern, msg) in err_labels.items():
                if not vals[key]:
                    err_lbl.config(text="⚠ This field is required."); ok = False
                elif not _re.fullmatch(pattern, vals[key]):
                    err_lbl.config(text=f"⚠ {msg}"); ok = False
            if not b:
                bus_err.config(text="⚠ Please select a bus."); ok = False
            if not ok: return

            if get_passenger_by_cnic(vals["cnic"]):
                err_labels["cnic"][0].config(text="⚠ This CNIC is already registered."); return

            bus_obj = bus_map[b]
            pid     = add_passenger(vals["name"], vals["cnic"], "", vals["phone"])
            bid     = add_waitlist_booking(pid, bus_obj["id"])
            entry   = {"name": vals["name"], "cnic": vals["cnic"],
                       "phone": vals["phone"], "bus_number": bus_obj["bus_number"],
                       "booking_id": bid, "passenger_id": pid, "bus_id": bus_obj["id"]}
            self.waitlist.enqueue(entry)
            wl_rec  = {"id": bid, "name": vals["name"], "cnic": vals["cnic"],
                       "seat_number": "N/A", "bus_number": bus_obj["bus_number"],
                       "booking_date": str(datetime.now()), "status": "waitlisted"}
            self.hash_table.insert(bid, wl_rec)
            self.passenger_bst.insert(vals["name"], wl_rec)
            _log("WAITLISTED", vals["name"], vals["phone"])

            for e in entries.values(): e.delete(0, tk.END)
            bus_var.set("")
            form_err.config(text=f"✅ {vals['name']} added to waitlist!", fg=GREEN)
            refresh_queue()
            self._show_admin_panel()
            win.destroy()

        def serve_next():
            passenger = self.waitlist.peek()
            if not passenger:
                messagebox.showinfo("Empty", "Waitlist is empty."); return
            bid    = passenger.get("booking_id")
            result = serve_waitlist_booking(bid) if bid else None
            if result is None:
                messagebox.showwarning("No Seat",
                    f"No free seat on {passenger.get('bus_number')} yet."); return
            self.waitlist.dequeue()
            self.hash_table.insert(bid, result)
            def _bst_upd(node, key, data):
                if node is None: return
                if node.key == key: node.data = data; return
                if key < node.key: _bst_upd(node.left, key, data)
                else:              _bst_upd(node.right, key, data)
            if self.passenger_bst._search(self.passenger_bst.root, passenger["name"]):
                _bst_upd(self.passenger_bst.root, passenger["name"], result)
            else:
                self.passenger_bst.insert(passenger["name"], result)
            _log("SERVED", passenger["name"], passenger.get("phone",""))
            messagebox.showinfo("Served ✅",
                f"{result['name']} →  Seat {result['seat_number']} on {result['bus_number']}")
            refresh_queue()
            self._show_admin_panel()
            win.destroy()

        # ── Action buttons ────────────────────────────────────────────
        btn_row = tk.Frame(form, bg=BG)
        btn_row.pack(anchor="w", pady=12)
        tk.Button(btn_row, text="➕  Add to Waitlist",
                  bg=ACCENT, fg=WHITE, font=FONT_BTN,
                  cursor="hand2", bd=0, padx=12, pady=7,
                  command=add_to_waitlist).pack(side="left", padx=(0,8))
        tk.Button(btn_row, text="▶  Serve Next",
                  bg=GREEN, fg=BG, font=FONT_BTN,
                  cursor="hand2", bd=0, padx=12, pady=7,
                  command=serve_next).pack(side="left", padx=(0,8))
        tk.Button(btn_row, text="📄 Open Log",
                  bg=YELLOW, fg=BG, font=FONT_BTN,
                  cursor="hand2", bd=0, padx=12, pady=7,
                  command=lambda: os.startfile(WAITLIST_LOG)
                      if os.path.isfile(WAITLIST_LOG)
                      else messagebox.showinfo("Log","No log file yet.")
                  ).pack(side="left")

        refresh_queue()

    def _inline_hash(self, search_var, col_var, tree):
        bid_str = search_var.get().strip()
        if not bid_str.isdigit():
            messagebox.showinfo("Hash Search","Type a numeric Booking ID in the search box first."); return
        r = self.hash_table.search(int(bid_str))
        if r:
            col_var.set("ID"); search_var.set(bid_str)
        else:
            messagebox.showinfo("Hash Search", f"Booking ID {bid_str} not found.")

    def _inline_binary(self, search_var, tree):
        val = search_var.get().strip()
        if not val.isdigit():
            messagebox.showinfo("Binary Search","Type a seat number in the search box first."); return
        target = int(val)
        all_b = [b for b in get_all_bookings() if str(b["seat_number"]).isdigit()]
        bookings = sorted(all_b, key=lambda x: int(x["seat_number"]))
        lo, hi, hit = 0, len(bookings)-1, -1
        while lo <= hi:
            mid = (lo+hi)//2; mv = int(bookings[mid]["seat_number"])
            if mv == target: hit = mid; break
            elif mv < target: lo = mid+1
            else: hi = mid-1
        if hit == -1:
            messagebox.showinfo("Binary Search", f"No booking found for seat {val}."); return
        messagebox.showinfo("Binary Search",
            f"✅ Seat {val} — {bookings[hit]['name']} | Bus: {bookings[hit]['bus_number']} | Status: {bookings[hit]['status']}")

    def _inline_bst(self, search_var, tree):
        name = search_var.get().strip()
        if not name:
            messagebox.showinfo("BST Search","Type a passenger name in the search box first."); return
        r = self.passenger_bst.search(name)
        if r:
            seat = r.get("seat_number","N/A")
            seat_d = "Waitlisted" if seat=="N/A" else seat
            messagebox.showinfo("BST Search",
                f"✅ {r.get('name')} | Seat: {seat_d} | Bus: {r.get('bus_number')} | Status: {r.get('status','N/A')}")
        else:
            messagebox.showinfo("BST Search", f"'{name}' not found in BST.")

    # MANAGER PAGES
    def _show_manage_buses(self):
        self._clear(); self._heading("Manage Buses","Edit or delete buses")
        tb=tk.Frame(self.main,bg=BG); tb.pack(fill="x",padx=24,pady=(4,8))
        tree_ref=[None]; buses=get_buses_with_stats()
        tk.Label(tb,text=f"{len(buses)} bus(es)",bg=BG,fg=YELLOW,font=FONT_SMALL).pack(side="right",padx=8)
        for label,color,cmd in [("🔄  Refresh",ACCENT,self._show_manage_buses),
                                  ("✏️   Edit",BLUE,lambda:self._edit_bus(tree_ref[0])),
                                  ("🗑   Delete",RED,lambda:self._delete_bus_action(tree_ref[0]))]:
            tk.Button(tb,text=label,bg=color,fg=WHITE,font=FONT_BTN,padx=10,pady=5,cursor="hand2",bd=0,command=cmd).pack(side="left",padx=4)
        cols=("ID","Bus No","Route","Departure","Seats","Booked","Available","Price")
        t_f=tk.Frame(self.main,bg=BG); t_f.pack(fill="both",expand=True,padx=24)
        tree=ttk.Treeview(t_f,columns=cols,show="headings",height=22); tree_ref[0]=tree
        vsb=ttk.Scrollbar(t_f,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=vsb.set)
        for c,w in zip(cols,[40,90,180,130,60,70,80,100]): tree.heading(c,text=c); tree.column(c,width=w,anchor="w")
        tree.tag_configure("full", background="#5C0000", foreground="#FF8080")
        for b in buses:
            tag = ("full",) if b["available"] == 0 else ()
            tree.insert("","end", tags=tag, values=(b["id"],b["bus_number"],b["route"],str(b["departure_time"])[:16],b["total_seats"],b["booked"],b["available"],f"PKR {b['price']:,}"))
        tree.pack(side="left",fill="both",expand=True); vsb.pack(side="right",fill="y")
        tree.after(100, lambda: _apply_row_colors(tree))
    def _edit_bus(self,tree):
        if not tree: return
        sel=tree.selection()
        if not sel: messagebox.showwarning("Select","Select a bus first."); return
        vals=tree.item(sel[0])["values"]; self._show_edit_bus_form(vals[0],vals)

    def _show_edit_bus_form(self,bus_id,vals):
        self._clear(); self._heading("Edit Bus",f"Editing: {vals[1]}")
        form=tk.Frame(self.main,bg=PANEL,padx=40,pady=30); form.pack(padx=40,pady=10,fill="x")
        price_clean=str(vals[7]).replace("PKR ","").replace(",","") if len(vals)>7 else "1500"
        fields=[("Bus Number  (e.g. BUS-125)",vals[1]),("Route  (e.g. Lahore to Karachi)",vals[2]),("Departure Time  (e.g. 2026-07-01 08:30)",vals[3]),("Total Seats  (e.g. 40)",vals[4]),("Price (PKR)",price_clean)]
        entries={}
        for label,default in fields:
            tk.Label(form,text=label,bg=PANEL,fg=WHITE,font=FONT_BODY).pack(anchor="w",pady=(8,1))
            e=tk.Entry(form,font=FONT_BODY,bg=ACCENT,fg=WHITE,insertbackground=WHITE,width=44); e.insert(0,default); e.pack(fill="x",ipady=6); entries[label]=e
        err=tk.Label(form,text="",bg=PANEL,fg=RED,font=FONT_SMALL); err.pack()
        def _save():
            bn=entries["Bus Number  (e.g. BUS-125)"].get().strip()
            rt=entries["Route  (e.g. Lahore to Karachi)"].get().strip()
            dt=entries["Departure Time  (e.g. 2026-07-01 08:30)"].get().strip()
            ts=entries["Total Seats  (e.g. 40)"].get().strip()
            pr=entries["Price (PKR)"].get().strip()
            if not all([bn,rt,dt,ts,pr]): err.config(text="⚠ All fields required."); return
            if not ts.isdigit() or int(ts)<1: err.config(text="⚠ Seats must be ≥ 1."); return
            pr_clean = pr.replace("PKR ","").replace(",","").strip()
            if not pr_clean.isdigit() or int(pr_clean)<1: err.config(text="⚠ Price must be ≥ 1."); return
            pr = pr_clean
            try:
                update_bus(bus_id,bn,rt,dt,int(ts),int(pr))
                sync_seats_from_bookings()
                messagebox.showinfo("Saved","Bus updated!"); self._show_manage_buses()
            except Exception as ex:
                err.config(text=f"❌  {ex}")
        btn_row=tk.Frame(form,bg=PANEL); btn_row.pack(anchor="w",pady=12)
        tk.Button(btn_row,text="💾  Save",bg=GREEN,fg=BG,font=FONT_BTN,pady=7,cursor="hand2",bd=0,command=_save).pack(side="left",padx=(0,10))
        tk.Button(btn_row,text="✖  Cancel",bg=ACCENT,fg=WHITE,font=FONT_BTN,pady=7,cursor="hand2",bd=0,command=self._show_manage_buses).pack(side="left")

    def _delete_bus_action(self,tree):
        if not tree: return
        sel=tree.selection()
        if not sel: messagebox.showwarning("Select","Select a bus first."); return
        bid=tree.item(sel[0])["values"][0]; name=tree.item(sel[0])["values"][1]
        if messagebox.askyesno("Delete",f"Delete {name} and all its bookings?"): delete_bus(bid); self._show_manage_buses()

    def _show_add_bus(self):
        self._clear(); self._heading("Add New Bus","Fill in the details below")
        form=tk.Frame(self.main,bg=PANEL,padx=40,pady=30); form.pack(padx=40,pady=10,fill="x")
        fields=[("Bus Number  (e.g. BUS-125)",""),("Route  (e.g. Lahore to Karachi)",""),("Departure Time  (e.g. 2026-07-01 08:30)",""),("Total Seats  (e.g. 40)",""),("Price (PKR)","1500")]
        entries={}
        for label,default in fields:
            tk.Label(form,text=label,bg=PANEL,fg=WHITE,font=FONT_BODY).pack(anchor="w",pady=(8,1))
            e=tk.Entry(form,font=FONT_BODY,bg=ACCENT,fg=WHITE,insertbackground=WHITE,width=44)
            if default: e.insert(0,default)
            e.pack(fill="x",ipady=6); entries[label]=e
        err=tk.Label(form,text="",bg=PANEL,fg=RED,font=FONT_SMALL); err.pack()
        def _add():
            bn=entries["Bus Number  (e.g. BUS-125)"].get().strip(); rt=entries["Route  (e.g. Lahore to Karachi)"].get().strip()
            dt=entries["Departure Time  (e.g. 2026-07-01 08:30)"].get().strip(); ts=entries["Total Seats  (e.g. 40)"].get().strip(); pr=entries["Price (PKR)"].get().strip()
            if not all([bn,rt,dt,ts,pr]): err.config(text="⚠ All fields required."); return
            if not ts.isdigit() or int(ts)<1: err.config(text="⚠ Capacity must be greater than 0."); return
            if not pr.isdigit() or int(pr)<1: err.config(text="⚠ Price must be ≥ 1."); return
            add_bus(bn,rt,dt,int(ts),int(pr)); messagebox.showinfo("Added","Bus added successfully!"); self._show_add_bus()
        def _clear_form():
            for e in entries.values(): e.delete(0,tk.END)
            entries["Price (PKR)"].insert(0,"1500"); err.config(text="")
        btn_row=tk.Frame(form,bg=PANEL); btn_row.pack(anchor="w",pady=12)
        tk.Button(btn_row,text="➕  Add Bus",bg=GREEN,fg=BG,font=FONT_BTN,pady=7,cursor="hand2",bd=0,command=_add).pack(side="left",padx=(0,10))
        tk.Button(btn_row,text="🗑  Clear",bg=ACCENT,fg=WHITE,font=FONT_BTN,pady=7,cursor="hand2",bd=0,command=_clear_form).pack(side="left")

    def _show_feedback_monitor(self):
        self._clear(); self._heading("Feedback Monitoring","View all passenger feedback")
        wrap=self._scrollable()
        tk.Label(wrap,text="⭐  Average Ratings per Bus",font=FONT_HEAD,bg=BG,fg=YELLOW).pack(anchor="w",padx=24,pady=(8,4))
        for r in get_avg_rating_per_bus():
            rating=r["avg_rating"] or 0; stars="★"*int(rating)+"☆"*(5-int(rating))
            row=tk.Frame(wrap,bg=PANEL,padx=16,pady=6); row.pack(fill="x",padx=24,pady=2)
            tk.Label(row,text=f"{r['bus_number']} — {r['route']}",bg=PANEL,fg=WHITE,font=FONT_BODY,width=30,anchor="w").pack(side="left")
            tk.Label(row,text=stars,bg=PANEL,fg=GOLD,font=("Segoe UI",12)).pack(side="left",padx=8)
            tk.Label(row,text=f"{rating}/5  ({r['review_count']} reviews)",bg=PANEL,fg=YELLOW,font=FONT_SMALL).pack(side="left")
        tk.Label(wrap,text="💬  All Feedback",font=FONT_HEAD,bg=BG,fg=YELLOW).pack(anchor="w",padx=24,pady=(16,4))
        cols=("ID","Passenger","Bus","Route","Rating","Comment","Date")
        t_f=tk.Frame(wrap,bg=BG); t_f.pack(fill="x",padx=24,pady=(0,16))
        tree=ttk.Treeview(t_f,columns=cols,show="headings",height=14)
        vsb=ttk.Scrollbar(t_f,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=vsb.set)
        for c,w in zip(cols,[40,120,80,160,60,200,120]): tree.heading(c,text=c); tree.column(c,width=w,anchor="w")
        for f in get_all_feedback():
            tree.insert("","end",values=(f["id"],f["passenger"],f["bus_number"],f["route"],"★"*f["rating"]+"☆"*(5-f["rating"]),f.get("comment",""),str(f["created_at"])[:16]))
        tree.pack(side="left",fill="x",expand=True); vsb.pack(side="right",fill="y")

    # SHARED DSA PANELS
    def _show_search(self):
        self._clear(); self._heading("Search Bookings")
        outer_canvas=tk.Canvas(self.main,bg=BG,highlightthickness=0)
        outer_vsb=ttk.Scrollbar(self.main,orient="vertical",command=outer_canvas.yview)
        outer_canvas.configure(yscrollcommand=outer_vsb.set)
        outer_vsb.pack(side="right",fill="y"); outer_canvas.pack(side="left",fill="both",expand=True)
        scroll_wrap=tk.Frame(outer_canvas,bg=BG)
        _sw_id=outer_canvas.create_window((0,0),window=scroll_wrap,anchor="nw")
        scroll_wrap.bind("<Configure>",lambda e:outer_canvas.configure(scrollregion=outer_canvas.bbox("all")))
        outer_canvas.bind("<Configure>",lambda e:outer_canvas.itemconfig(_sw_id,width=e.width))
        frame=tk.Frame(scroll_wrap,bg=PANEL,padx=24,pady=22); frame.pack(padx=30,fill="x")
        result_lbl=tk.Label(scroll_wrap,text="",bg=BG,fg=YELLOW,font=FONT_BODY,justify="left",wraplength=820)
        result_lbl.pack(pady=12,padx=30,anchor="w")
        # ── Hash Search ───────────────────────────────────────────────
        tk.Label(frame,text="🔑  Hash Search — Type a Booking ID:",bg=PANEL,fg=WHITE,font=("Georgia",11,"bold")).pack(anchor="w")
        tk.Label(frame,text="Type the ID — matching bookings appear below in O(1).",bg=PANEL,fg=YELLOW,font=FONT_SMALL).pack(anchor="w",pady=(0,4))
        all_bookings=get_all_bookings(); id_to_booking={str(b["id"]):b for b in all_bookings}
        for _b in self.hash_table.get_all():
            if _b and "id" in _b: id_to_booking[str(_b["id"])]=_b
        hash_id_var=tk.StringVar()
        hash_sub=tk.Frame(frame,bg=PANEL); hash_sub.pack(anchor="w")
        hash_entry=tk.Entry(hash_sub,textvariable=hash_id_var,font=FONT_BODY,bg=ACCENT,fg=WHITE,insertbackground=WHITE,width=20)
        hash_entry.pack(anchor="w",ipady=4,pady=(0,2))
        suggest_lb=tk.Listbox(hash_sub,font=FONT_SMALL,bg=ACCENT,fg=WHITE,selectbackground=GREEN,height=5,width=45,activestyle="none")
        selected_booking=[None]
        def _update_suggestions(*_):
            q=hash_id_var.get().strip(); suggest_lb.delete(0,tk.END)
            if not q: suggest_lb.pack_forget(); selected_booking[0]=None; return
            matches=[b for bid,b in id_to_booking.items() if bid.startswith(q)]
            if matches:
                for b in matches[:8]: suggest_lb.insert(tk.END,f"{b['id']}  —  {b['name']}")
                suggest_lb.pack(anchor="w",pady=(0,4),in_=hash_sub)
            else: suggest_lb.pack_forget()
        def _on_select(event):
            idx=suggest_lb.curselection()
            if not idx: return
            label=suggest_lb.get(idx[0]); bid=label.split("  —  ")[0].strip()
            selected_booking[0]=id_to_booking.get(bid); hash_id_var.set(bid); suggest_lb.pack_forget()
        hash_id_var.trace_add("write",_update_suggestions); suggest_lb.bind("<<ListboxSelect>>",_on_select)
        def do_hash():
            bid_str=hash_id_var.get().strip()
            if not bid_str.isdigit(): result_lbl.config(text="⚠  Enter a numeric Booking ID."); return
            booking=selected_booking[0] or id_to_booking.get(bid_str)
            if not booking: result_lbl.config(text="❌   Booking ID not found."); return
            r=self.hash_table.search(int(bid_str)); b=r if r else booking
            seat_d="No seat yet (waitlisted)" if b.get("seat_number")=="N/A" else b.get("seat_number")
            result_lbl.config(text=f"✅  Hash Found — {b.get('name')}  |  Seat: {seat_d}  |  Bus: {b.get('bus_number')}  |  Status: {b.get('status')}")
        tk.Button(frame,text="Hash Search",bg=ACCENT,fg=WHITE,font=FONT_BTN,cursor="hand2",command=do_hash).pack(anchor="w",pady=6)
        tk.Frame(frame,bg=YELLOW,height=1).pack(fill="x",pady=12)
        # ── Binary Search ─────────────────────────────────────────────
        tk.Label(frame,text="🔢  Binary Search — Enter Seat Number:",bg=PANEL,fg=WHITE,font=("Georgia",11,"bold")).pack(anchor="w")
        bin_entry=tk.Entry(frame,font=FONT_BODY,bg=ACCENT,fg=WHITE,insertbackground=WHITE,width=30)
        bin_entry.pack(anchor="w",ipady=5,pady=4)
        bin_result_txt=tk.Text(scroll_wrap,bg=BG,fg=YELLOW,font=FONT_SMALL,relief="flat",bd=0,state="disabled",wrap="word",height=1,width=80)
        bin_result_txt.tag_configure("header",foreground=GREEN,font=("Georgia",11))
        bin_result_txt.tag_configure("recent",foreground=GREEN,font=("Segoe UI",10,"bold"))
        bin_result_txt.tag_configure("normal",foreground=YELLOW,font=FONT_SMALL)
        bin_result_txt.tag_configure("error",foreground=RED,font=FONT_SMALL)
        def _bin_write(lines_tags):
            bin_result_txt.config(state="normal"); bin_result_txt.delete("1.0",tk.END)
            for text,tag in lines_tags: bin_result_txt.insert(tk.END,text,tag)
            n=int(bin_result_txt.index("end-1c").split(".")[0])
            bin_result_txt.config(height=min(n,18),state="disabled")
            bin_result_txt.pack(pady=6,padx=30,anchor="w"); scroll_wrap.update_idletasks()
        bin_result_txt.pack_forget()
        def do_binary():
            val=bin_entry.get().strip()
            if not val.isdigit(): _bin_write([("⚠  Enter a numeric seat number.","error")]); result_lbl.config(text=""); return
            target=int(val)
            all_b=[b for b in get_all_bookings() if str(b["seat_number"]).isdigit()]
            bookings=sorted(all_b,key=lambda x:int(x["seat_number"]))
            low,high,hit_idx=0,len(bookings)-1,-1
            while low<=high:
                mid=(low+high)//2; mid_val=int(bookings[mid]["seat_number"])
                if mid_val==target: hit_idx=mid; break
                elif mid_val<target: low=mid+1
                else: high=mid-1
            if hit_idx==-1: _bin_write([(f"❌   Seat {val} has no booking.","error")]); result_lbl.config(text=""); return
            left=hit_idx
            while left>0 and int(bookings[left-1]["seat_number"])==target: left-=1
            right=hit_idx
            while right<len(bookings)-1 and int(bookings[right+1]["seat_number"])==target: right+=1
            hits=bookings[left:right+1]
            most_recent_id=max(hits,key=lambda b:str(b["booking_date"]))["id"]
            for _b in self.hash_table.get_all():
                if (_b and str(_b.get("seat_number",""))==val and _b.get("id") not in [h["id"] for h in hits]):
                    hits.append(_b); most_recent_id=_b["id"]
            lines_tags=[(f"✅  Seat {val} found on {len(hits)} bus(es):\n","header")]
            for b in hits:
                tag="recent" if b["id"]==most_recent_id else "normal"
                star="  ★ " if b["id"]==most_recent_id else "  •  "
                suffix="  ← most recent" if b["id"]==most_recent_id else ""
                lines_tags.append((f"{star}{b['name']}  |  Bus: {b['bus_number']}  |  Status: {b['status']}{suffix}\n",tag))
            _bin_write(lines_tags); result_lbl.config(text="")
        tk.Button(frame,text="Binary Search",bg=ACCENT,fg=WHITE,font=FONT_BTN,cursor="hand2",command=do_binary).pack(anchor="w")
        tk.Frame(frame,bg=YELLOW,height=1).pack(fill="x",pady=12)
        # ── BST Search ────────────────────────────────────────────────
        tk.Label(frame,text="🌳  BST Search — Enter Passenger Name:",bg=PANEL,fg=WHITE,font=("Georgia",11,"bold")).pack(anchor="w")
        bst_entry=tk.Entry(frame,font=FONT_BODY,bg=ACCENT,fg=WHITE,insertbackground=WHITE,width=30)
        bst_entry.pack(anchor="w",ipady=5,pady=4)
        def do_bst():
            name=bst_entry.get().strip()
            if not name: result_lbl.config(text="⚠ Enter a passenger name."); return
            r=self.passenger_bst.search(name)
            if r:
                seat=r.get("seat_number") or "N/A"
                seat_display="No seat yet (waitlisted)" if seat=="N/A" else seat
                result_lbl.config(text=f"✅  BST Found — {r.get('name')}  |  Seat: {seat_display}  |  Bus: {r.get('bus_number')}  |  Status: {r.get('status','N/A')}")
            else:
                hits=[b for b in get_all_bookings() if name.lower() in b["name"].lower()]
                if hits:
                    lines=[]
                    for b in hits:
                        seat=b["seat_number"] if b["seat_number"]!="N/A" else "No seat yet"
                        lines.append(f"  •  {b['name']}  |  Seat: {seat}  |  Bus: {b['bus_number']}  |  Status: {b['status']}")
                        result_lbl.config(text="✅  Found:\n"+"\n".join(lines))
                else: result_lbl.config(text="❌   Passenger not found in BST or DB.")
        tk.Button(frame,text="BST Search",bg=ACCENT,fg=WHITE,font=FONT_BTN,cursor="hand2",command=do_bst).pack(anchor="w")

    def _show_search_filter(self):
        self._clear(); self._heading("Search & Filter","Search by route or bus number")
        wrap=self._scrollable()
        search_frame=tk.Frame(wrap,bg=PANEL,padx=20,pady=14); search_frame.pack(padx=24,fill="x",pady=(8,4))
        tk.Label(search_frame,text="Search:",bg=PANEL,fg=WHITE,font=FONT_BODY).pack(side="left")
        q_var=tk.StringVar()
        tk.Entry(search_frame,textvariable=q_var,font=FONT_BODY,bg=ACCENT,fg=WHITE,insertbackground=WHITE,width=36).pack(side="left",padx=8,ipady=5)
        cols=("ID","Bus No","Route","Departure","Seats","Available","Price")
        t_f=tk.Frame(wrap,bg=BG); t_f.pack(padx=24,fill="x",pady=4)
        tree=ttk.Treeview(t_f,columns=cols,show="headings",height=18)
        vsb=ttk.Scrollbar(t_f,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=vsb.set)
        for c,w in zip(cols,[40,90,200,130,70,80,100]): tree.heading(c,text=c); tree.column(c,width=w,anchor="w")
        all_buses=get_buses_with_stats()
        def _populate(data):
            tree.delete(*tree.get_children())
            for b in data:
                tree.insert("","end",values=(b["id"],b["bus_number"],b["route"],str(b["departure_time"])[:16],b["total_seats"],b["available"],f"PKR {b['price']:,}"))
        _populate(all_buses)
        def _filter(*_):
            q=q_var.get().strip().lower()
            _populate(all_buses if not q else [b for b in all_buses if q in (b["bus_number"]+b["route"]).lower()])
        q_var.trace_add("write",_filter)
        tk.Button(search_frame,text="🔍 Search",bg=YELLOW,fg=BG,font=FONT_BTN,cursor="hand2",bd=0,command=_filter).pack(side="left")
        tree.pack(side="left",fill="x",expand=True); vsb.pack(side="right",fill="y")

    def _get_edge_weight(self,u,v):
        for neighbor,weight in self.route_graph.graph.get(u,[]):
            if neighbor==v: return weight
        return 0

    def _show_routes(self):
        self._clear(); self._heading("Route Finder — Dijkstra's Algorithm")
        canvas=tk.Canvas(self.main,bg=BG,highlightthickness=0)
        vsb=ttk.Scrollbar(self.main,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set); vsb.pack(side="right",fill="y"); canvas.pack(side="left",fill="both",expand=True)
        wrap=tk.Frame(canvas,bg=BG); wid=canvas.create_window((0,0),window=wrap,anchor="nw")
        wrap.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",lambda e:canvas.itemconfig(wid,width=e.width))
        form=tk.Frame(wrap,bg=PANEL,padx=24,pady=22); form.pack(padx=30,fill="x")
        stops=sorted(self.route_graph.get_all_stops()); from_v=tk.StringVar(); to_v=tk.StringVar()
        tk.Label(form,text="From:",bg=PANEL,fg=WHITE,font=FONT_BODY).grid(row=0,column=0,sticky="w",pady=6)
        ttk.Combobox(form,textvariable=from_v,values=stops,width=28,state="readonly").grid(row=0,column=1,padx=12,pady=6)
        tk.Label(form,text="To:",bg=PANEL,fg=WHITE,font=FONT_BODY).grid(row=1,column=0,sticky="w")
        ttk.Combobox(form,textvariable=to_v,values=stops,width=28,state="readonly").grid(row=1,column=1,padx=12)
        result_frame=tk.Frame(wrap,bg=BG); result_frame.pack(fill="x",padx=30,pady=10)
        def _clear_r():
            for w in result_frame.winfo_children(): w.destroy()
        def _lbl(parent,text,fg=WHITE,fs=11,bold=False,pady=2):
            tk.Label(parent,text=text,bg=BG,fg=fg,font=("Segoe UI",fs,"bold" if bold else ""),justify="left",wraplength=800,anchor="w").pack(anchor="w",pady=pady)
        def find():
            _clear_r(); f,t=from_v.get(),to_v.get()
            if not f or not t: _lbl(result_frame,"⚠ Select both cities.",RED); return
            if f==t: _lbl(result_frame,"⚠ From and To must differ.",RED); return
            path,dist=self.route_graph.dijkstra(f,t)
            if dist==float("inf"): _lbl(result_frame,f"❌  No route between {f} and {t}.",RED,bold=True); return
            _lbl(result_frame,"✅  Shortest Route Found",GREEN,13,True)
            _lbl(result_frame,"📍  Route Segments:",YELLOW,11,True,(10,2))
            for i in range(len(path)-1):
                seg=self._get_edge_weight(path[i],path[i+1])
                row=tk.Frame(result_frame,bg=PANEL,padx=16,pady=5); row.pack(fill="x",pady=1)
                tk.Label(row,text=f"  Hop {i+1}:  {path[i]}  →   {path[i+1]}",bg=PANEL,fg=WHITE,font=FONT_BODY,width=40,anchor="w").pack(side="left")
                tk.Label(row,text=f"{seg} km",bg=PANEL,fg=GREEN,font=("Segoe UI",11,"bold")).pack(side="left")
            tot_row=tk.Frame(result_frame,bg=ACCENT,padx=16,pady=7); tot_row.pack(fill="x",pady=(1,8))
            seg_str=" + ".join(str(self._get_edge_weight(path[i],path[i+1])) for i in range(len(path)-1))
            tk.Label(tot_row,text=f"  Total: {seg_str} = {dist} km",bg=ACCENT,fg=GOLD,font=("Georgia",12,"bold")).pack(anchor="w")
            _lbl(result_frame,"🔢  Dijkstra distance table:",YELLOW,11,True,(10,2))
            import heapq
            graph=self.route_graph.graph; all_nodes=list(graph.keys())
            dist_map={n:float("inf") for n in all_nodes}; dist_map[f]=0
            prev={n:None for n in all_nodes}; pq=[(0,f)]; visited=[]
            while pq:
                d,u=heapq.heappop(pq)
                if u in visited: continue
                visited.append(u)
                for v,w in graph.get(u,[]):
                    nd=d+w
                    if nd<dist_map.get(v,float("inf")): dist_map[v]=nd; prev[v]=u; heapq.heappush(pq,(nd,v))
            hdr=tk.Frame(result_frame,bg=ACCENT,padx=16,pady=4); hdr.pack(fill="x",pady=(0,1))
            for col,w in [("City",22),(f"Dist from {f}",28),("Via",20)]:
                tk.Label(hdr,text=col,bg=ACCENT,fg=WHITE,font=("Segoe UI",10,"bold"),width=w,anchor="w").pack(side="left")
            for node,d in sorted(dist_map.items(),key=lambda x:x[1] if x[1]!=float("inf") else 9999):
                is_path=node in path; bg_c="#2A1F0A" if is_path else PANEL; fg_c=GREEN if is_path else WHITE
                via=prev.get(node) or "—"; d_str=f"{d} km" if d!=float("inf") else "unreachable"
                r=tk.Frame(result_frame,bg=bg_c,padx=16,pady=3); r.pack(fill="x",pady=1)
                tk.Label(r,text=("★ " if is_path else "  ")+node,bg=bg_c,fg=fg_c,font=("Segoe UI",10,"bold" if is_path else ""),width=22,anchor="w").pack(side="left")
                tk.Label(r,text=d_str,bg=bg_c,fg=fg_c,font=FONT_SMALL,width=28,anchor="w").pack(side="left")
                tk.Label(r,text=str(via),bg=bg_c,fg=fg_c,font=FONT_SMALL,width=20,anchor="w").pack(side="left")
            bfs=self.route_graph.bfs(f)

            # BFS section — full card so nothing clips
            tk.Label(result_frame,text="",bg=BG).pack()
            bfs_card=tk.Frame(result_frame,bg=PANEL,padx=16,pady=14)
            bfs_card.pack(fill="x",pady=(4,2))
            tk.Label(bfs_card,
                     text=f"🔄  BFS Traversal from {f}",
                     bg=PANEL,fg=YELLOW,
                     font=("Georgia",11,"bold")).pack(anchor="w")
            tk.Label(bfs_card,
                     text="  →   ".join(bfs),
                     bg=PANEL,fg=WHITE,
                     font=("Segoe UI",10),
                     wraplength=820,justify="left").pack(anchor="w",pady=(4,8))
            tk.Frame(bfs_card,bg=ACCENT,height=1).pack(fill="x",pady=(0,8))
            tk.Label(bfs_card,
                     text="What is BFS?",
                     bg=PANEL,fg=GOLD,
                     font=("Segoe UI",10,"bold")).pack(anchor="w")
            tk.Label(bfs_card,
                     text=(
                         "BFS (Breadth-First Search) explores all directly connected cities first, "
                         "then moves to the next level — like ripples spreading outward from a stone "
                         "in water. It visits every reachable city but does NOT guarantee the shortest "
                         "distance. That is Dijkstra's job. BFS only cares about HOW MANY hops, "
                         "not how many kilometres."
                     ),
                     bg=PANEL,fg=WHITE,
                     font=("Segoe UI",9),
                     wraplength=820,justify="left").pack(anchor="w",pady=(4,0))
            wrap.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        tk.Button(form,text="Find Shortest Route",bg=GREEN,fg=BG,font=("Georgia",11,"bold"),cursor="hand2",command=find).grid(row=2,column=1,sticky="w",padx=12,pady=14)

    def _show_sort_stats(self):
        import time as _time
        self._clear(); self._heading("Sorting Algorithm Comparison")
        bookings=get_all_bookings()
        if not bookings:
            tk.Label(self.main,text="No bookings yet.",bg=BG,fg=YELLOW,font=FONT_BODY).pack(pady=30); return
        n=len(bookings); key="id"
        merge_comparisons=[0]; merge_merges=[0]
        def _merge_inst(left,right):
            result=[]; i=j=0
            while i<len(left) and j<len(right):
                merge_comparisons[0]+=1
                if str(left[i][key])<=str(right[j][key]): result.append(left[i]); i+=1
                else: result.append(right[j]); j+=1
            result.extend(left[i:]); result.extend(right[j:]); return result
        def _merge_sort_inst(data):
            if len(data)<=1: return data
            mid=len(data)//2; merge_merges[0]+=1
            return _merge_inst(_merge_sort_inst(data[:mid]),_merge_sort_inst(data[mid:]))
        data_before=[b[key] for b in bookings[:5]]
        _times=[]
        for _ in range(5):
            t0=_time.perf_counter(); _merge_sort_inst(bookings.copy()); _times.append((_time.perf_counter()-t0)*1000)
        merge_ms=round(sum(_times)/len(_times),4); merge_sorted=_merge_sort_inst(bookings.copy())
        merge_after=[b[key] for b in merge_sorted[:5]]
        bubble_comparisons=[0]; bubble_swaps=[0]
        def _bubble_sort_inst(data):
            data=data.copy()
            for i in range(len(data)):
                for j in range(0,len(data)-i-1):
                    bubble_comparisons[0]+=1
                    if str(data[j][key])>str(data[j+1][key]): data[j],data[j+1]=data[j+1],data[j]; bubble_swaps[0]+=1
            return data
        _times=[]
        for _ in range(5):
            t0=_time.perf_counter(); _bubble_sort_inst(bookings); _times.append((_time.perf_counter()-t0)*1000)
        bubble_ms=round(sum(_times)/len(_times),4); bubble_sorted=_bubble_sort_inst(bookings)
        bubble_after=[b[key] for b in bubble_sorted[:5]]
        faster="Merge Sort" if merge_ms<bubble_ms else "Bubble Sort"
        canvas=tk.Canvas(self.main,bg=BG,highlightthickness=0)
        vsb=ttk.Scrollbar(self.main,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set); vsb.pack(side="right",fill="y"); canvas.pack(side="left",fill="both",expand=True)
        wrap=tk.Frame(canvas,bg=BG); wid=canvas.create_window((0,0),window=wrap,anchor="nw")
        wrap.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",lambda e:canvas.itemconfig(wid,width=e.width))
        def _section(title,color=YELLOW):
            tk.Label(wrap,text=title,bg=BG,fg=color,font=("Georgia",12,"bold")).pack(anchor="w",padx=30,pady=(14,2))
        def _row(label,value,val_color=YELLOW):
            f=tk.Frame(wrap,bg=PANEL,padx=20,pady=6); f.pack(fill="x",padx=30,pady=1)
            tk.Label(f,text=label,bg=PANEL,fg=WHITE,font=FONT_BODY,width=30,anchor="w").pack(side="left")
            tk.Label(f,text=value,bg=PANEL,fg=val_color,font=("Segoe UI",11,"bold")).pack(side="left")
        def _note(text):
            tk.Label(wrap,text=text,bg=BG,fg=WHITE,font=FONT_SMALL,wraplength=720,justify="left").pack(anchor="w",padx=34,pady=1)
        _section("📊  Summary",GREEN)
        _row("Total records sorted:",str(n))
        _row("Sorted by field:","Booking ID  (ascending)")
        _row("Faster algorithm:",faster,GREEN if faster=="Merge Sort" else RED)
        _section("≡ƒöÇ  Merge Sort  —  O(n log n)")
        _row("Time taken (avg 5 runs):",f"{merge_ms} ms",GREEN)
        _row("Total comparisons:",f"{merge_comparisons[0]:,}")
        _row("Divide steps:",f"{merge_merges[0]:,}")
        _note(f"→  How it works: splits the list into halves recursively until each piece has 1 element, then merges pairs back in sorted order. With {n} records it split {merge_merges[0]} times and compared {merge_comparisons[0]:,} pairs during merging.")
        _row("IDs before (first 5):","  ".join(str(x) for x in data_before),WHITE)
        _row("IDs after  (first 5):","  ".join(str(x) for x in merge_after),GREEN)
        _section("🫧  Bubble Sort  —  O(n²)")
        _row("Time taken (avg 5 runs):",f"{bubble_ms} ms",RED)
        _row("Total comparisons:",f"{bubble_comparisons[0]:,}")
        _row("Total swaps:",f"{bubble_swaps[0]:,}")
        _note(f"→  How it works: repeatedly walks the list comparing adjacent pairs and swapping them if out of order. With {n} records it made {bubble_comparisons[0]:,} comparisons and {bubble_swaps[0]:,} swaps — every out-of-order pair costs a swap, which is why it's slow on large data.")
        _row("IDs before (first 5):","  ".join(str(x) for x in data_before),WHITE)
        _row("IDs after  (first 5):","  ".join(str(x) for x in bubble_after),RED)
        _section("⚖️  Verdict",GREEN)
        speedup=round(bubble_ms/merge_ms,1) if merge_ms>0 else " ∞"
        _row("Speed difference:",f"Merge Sort was {speedup}× faster")
        _note("Merge Sort is the industry standard. Bubble Sort is O(n²) — doubling data quadruples the work.")

    # PASSENGER PAGES
    def _show_all_buses_passenger(self):
        self._clear(); self._heading("All Buses","Browse all available routes")
        wrap=self._scrollable()
        filter_row=tk.Frame(wrap,bg=BG); filter_row.pack(fill="x",padx=24,pady=(8,4))
        tk.Label(filter_row,text="Filter by Route:",bg=BG,fg=WHITE,font=FONT_BODY).pack(side="left")
        routes=["All"]+sorted(set(b["route"] for b in get_all_buses()))
        route_var=tk.StringVar(value="All")
        ttk.Combobox(filter_row,textvariable=route_var,values=routes,width=28,state="readonly").pack(side="left",padx=8)
        cols=("ID","Bus No","Route","Departure","Capacity","Booked","Price","Status")
        t_f=tk.Frame(wrap,bg=BG); t_f.pack(fill="x",padx=24)
        tree=ttk.Treeview(t_f,columns=cols,show="headings",height=20)
        vsb=ttk.Scrollbar(t_f,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=vsb.set)
        for c,w in zip(cols,[40,90,180,130,70,70,100,90]): tree.heading(c,text=c); tree.column(c,width=w,anchor="w")
        tree.tag_configure("full",background="#5C0000",foreground="#FF6B6B")
        all_buses=get_buses_with_stats()
        def _populate(data):
            tree.delete(*tree.get_children())
            for b in data:
                status="FULL" if b["available"]==0 else "Available"
                tree.insert("","end",tags=("full",) if b["available"]==0 else (),
                            values=(b["id"],b["bus_number"],b["route"],str(b["departure_time"])[:16],b["total_seats"],b["booked"],f"PKR {b['price']:,}",status))
            tree.after(100, lambda: _apply_row_colors(tree))
        _populate(all_buses)
        def _filter(*_):
            r=route_var.get()
            _populate(all_buses if r=="All" else [b for b in all_buses if b["route"]==r])
        route_var.trace_add("write",_filter)
        tree.pack(side="left",fill="x",expand=True); vsb.pack(side="right",fill="y")

    def _show_book_seat(self):
        self._clear()
        self._heading("Book a Seat", "Select a bus below — FULL buses shown in red join the waitlist")
        import re as _re

        # ── Two-column layout using PanedWindow so both sides resize ──
        body = tk.PanedWindow(self.main, orient="horizontal",
                      bg=BG, sashwidth=4, sashrelief="flat",
                      sashpad=0, borderwidth=0)
        body.pack(fill="both", expand=True, padx=0, pady=(4,0))
        # ── LEFT: Bus table ────────────────────────────────────────────
        left = tk.Frame(body, bg=BG)
        body.add(left, minsize=420, stretch="always")

        tk.Label(left, text="Available Buses",
                 bg=BG, fg=YELLOW, font=("Georgia",11,"bold")).pack(anchor="w", pady=(0,4))

        cols = ("ID","Bus No","Route","Departure","Seats","Avail","Price","Status")
        t_f  = tk.Frame(left, bg=BG)
        t_f.pack(fill="both", expand=True)
        tree = ttk.Treeview(t_f, columns=cols, show="headings", height=22)
        vsb  = ttk.Scrollbar(t_f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        for c,w in zip(cols,[35,85,185,120,55,55,100,85]):
            tree.heading(c, text=c, anchor="w")
            tree.column(c, width=w, anchor="w", stretch=True)

        # Tag config — "default" theme respects these
        tree.tag_configure("full",      background="#5C0000", foreground="#FF6B6B")
        tree.tag_configure("available", background=PANEL,     foreground=WHITE)
        tree.tag_configure("selected_bus", background=ACCENT, foreground=GOLD)

        all_buses = get_buses_with_stats()
        for b in all_buses:
            avail  = b["available"]
            status = "FULL" if avail == 0 else f"{avail} left"
            tag    = ("full",) if avail == 0 else ("available",)
            tree.insert("","end", tags=tag, values=(
                b["id"], b["bus_number"], b["route"],
                str(b["departure_time"])[:16],
                b["total_seats"], avail,
                f"PKR {b['price']:,}", status))
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        tree.update_idletasks()
        _apply_row_colors(tree)

        # Legend
        leg = tk.Frame(left, bg=BG)
        leg.pack(anchor="w", pady=(4,0))
        tk.Frame(leg, bg="#5C0000", width=14, height=14).pack(side="left")
        tk.Label(leg, text=" FULL — joins waitlist",
                 bg=BG, fg="#FF6B6B", font=FONT_SMALL).pack(side="left", padx=(2,16))
        tk.Frame(leg, bg=PANEL, width=14, height=14,
                 relief="solid", bd=1).pack(side="left")
        tk.Label(leg, text=" Available",
                 bg=BG, fg=WHITE, font=FONT_SMALL).pack(side="left", padx=2)

        # ── RIGHT: Booking form ────────────────────────────────────────
        right_outer = tk.Frame(body, bg=BG)
        body.add(right_outer, minsize=300, stretch="never")

        # Scrollable right panel
        rcanvas = tk.Canvas(right_outer, bg=BG, highlightthickness=0)
        rvsb    = ttk.Scrollbar(right_outer, orient="vertical", command=rcanvas.yview)
        rcanvas.configure(yscrollcommand=rvsb.set)
        rvsb.pack(side="right", fill="y")
        rcanvas.pack(side="left", fill="both", expand=True)
        right = tk.Frame(rcanvas, bg=BG)
        rwid  = rcanvas.create_window((0,0), window=right, anchor="nw")
        right.bind("<Configure>",
            lambda e: rcanvas.configure(scrollregion=rcanvas.bbox("all")))
        rcanvas.bind("<Configure>",
            lambda e: rcanvas.itemconfig(rwid, width=e.width))

        # Selected bus indicator
        sel_card = tk.Frame(right, bg=ACCENT, padx=12, pady=8)
        sel_card.pack(fill="x", pady=(0,10))
        sel_lbl = tk.Label(sel_card, text="← Select a bus from the list",
                           bg=ACCENT, fg=WHITE, font=("Segoe UI",10,"italic"),
                           wraplength=280, justify="left")
        sel_lbl.pack(anchor="w")

        # Update selected bus card on click
        def on_select(event):
            sel = tree.selection()
            if not sel: return
            vals = tree.item(sel[0])["values"]
            avail = vals[5]
            status_txt = "🔴 FULL — will join waitlist" if str(avail)=="0" else f"🟢 {avail} seats available"
            sel_lbl.config(
                text="Selected: {}\n{}\nDep: {}\n{}  |  {}".format(
                    vals[1], vals[2], vals[3], status_txt, vals[6]))
        tree.bind("<<TreeviewSelect>>", on_select)

        # Form section header
        tk.Label(right, text="Passenger Details",
                 bg=BG, fg=WHITE, font=("Georgia",12,"bold")).pack(anchor="w", pady=(0,6))

        FIELDS = [
            ("Full Name",                       "name",
             lambda v: len(v.strip())>=2,        "Min 2 characters"),
            ("CNIC  (12345-1234567-1)",          "cnic",
             lambda v: bool(_re.fullmatch(r'\d{5}-\d{7}-\d', v)), "Format: 12345-1234567-1"),
            ("Email",                            "email",
             lambda v: bool(_re.fullmatch(r'[^@]+@[^@]+\.[^@]+', v)), "Enter valid email"),
            ("Phone  (0301-1234567)",            "phone",
             lambda v: bool(_re.fullmatch(r'0\d{3}-\d{7}', v)), "Format: 0301-1234567"),
        ]
        entries    = {}
        err_labels = {}

        for label, key, validator, msg in FIELDS:
            tk.Label(right, text=label, bg=BG, fg=YELLOW,
                     font=("Segoe UI",9,"bold")).pack(anchor="w", pady=(6,1))
            e = tk.Entry(right, font=FONT_BODY, bg=PANEL, fg=WHITE,
                         insertbackground=WHITE, relief="flat",
                         highlightthickness=1, highlightbackground=ACCENT,
                         highlightcolor=GOLD, width=32)
            e.pack(fill="x", ipady=6)
            err = tk.Label(right, text="", bg=BG, fg=RED, font=FONT_SMALL)
            err.pack(anchor="w")
            entries[key]    = e
            err_labels[key] = (err, validator, msg)

        # Promo code
        tk.Label(right, text="🎟  Promo Code (optional)",
                 bg=BG, fg=YELLOW, font=("Segoe UI",9,"bold")).pack(anchor="w", pady=(8,1))
        promo_row = tk.Frame(right, bg=BG)
        promo_row.pack(fill="x")
        promo_var = tk.StringVar()
        promo_e   = tk.Entry(promo_row, textvariable=promo_var,
                             font=FONT_BODY, bg=PANEL, fg=WHITE,
                             insertbackground=WHITE, relief="flat",
                             highlightthickness=1, highlightbackground=ACCENT,
                             highlightcolor=GOLD, width=18)
        promo_e.pack(side="left", ipady=5)
        promo_lbl = tk.Label(promo_row, text="", bg=BG, fg=GREEN, font=FONT_SMALL)
        promo_lbl.pack(side="left", padx=6)
        promo_data = [None]

        def _check_promo(*_):
            code = promo_var.get().strip().upper()
            if not code:
                promo_lbl.config(text="", fg=GREEN); promo_data[0]=None; return
            p = validate_promo(code)
            if p:
                promo_data[0] = p
                promo_lbl.config(text=f"✅ {p['discount_pct']}% off!", fg=GREEN)
            else:
                promo_data[0] = None
                promo_lbl.config(text="❌  Invalid", fg=RED)
        promo_var.trace_add("write", _check_promo)

        # Book button
        tk.Frame(right, bg=ACCENT, height=1).pack(fill="x", pady=(14,8))

        def _book():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Bus", "Please select a bus from the list first.")
                return
            bus_vals   = tree.item(sel[0])["values"]
            bus_id_sel = bus_vals[0]
            bus_num    = bus_vals[1]
            bus_route  = bus_vals[2]
            bus_price  = next((b["price"] for b in all_buses if b["id"]==bus_id_sel), 1500)
            is_full    = str(bus_vals[5]) == "0"

            # Validate fields
            for _, (err_lbl, _, _) in err_labels.items(): err_lbl.config(text="")
            vals = {key: entries[key].get().strip() for _,key,__,___ in FIELDS}
            ok   = True
            for _, key, validator, msg in FIELDS:
                err_lbl, _, _ = err_labels[key]
                if not vals[key]:
                    err_lbl.config(text="⚠ Required"); ok = False
                elif not validator(vals[key]):
                    err_lbl.config(text=f"⚠ {msg}"); ok = False
            if not ok: return
            if vals["name"].lower() != self.user["username"].lower():
                err_labels["name"][0].config(text="⚠ Name must match your account username"); return
            registered_cnic = get_user_cnic(self.user["id"])
            if registered_cnic and vals["cnic"] != registered_cnic:
                err_labels["cnic"][0].config(text="⚠ Please use your registered CNIC"); return
            _show_payment_popup(bus_id_sel, bus_num, bus_route,
                                bus_price, vals, is_full, promo_data[0])

        tk.Button(right, text="🎫  Book / Join Waitlist",
                  bg=GREEN, fg=BG,
                  font=("Georgia",12,"bold"),
                  pady=10, cursor="hand2", bd=0,
                  command=_book).pack(fill="x")
        tk.Button(right, text="🔄  Refresh",
                  bg=ACCENT, fg=WHITE,
                  font=FONT_BTN, cursor="hand2", bd=0,
                  command=self._show_book_seat).pack(fill="x", pady=(6,0))

        def _show_payment_popup(bus_id_sel, bus_num, bus_route,
                                bus_price, vals, is_full, promo):
            orig = bus_price
            disc = round(orig * promo["discount_pct"] / 100) if promo else 0
            due  = orig - disc

            win = tk.Toplevel(self)
            win.title("Secure Payment")
            win.configure(bg=BG)
            win.geometry("460x600")
            win.grab_set()
            x=(self.winfo_screenwidth()-460)//2; y=(self.winfo_screenheight()-600)//2
            win.geometry(f"460x600+{x}+{y}")

            tk.Label(win, text="💳  Secure Payment",
                     font=FONT_HEAD, bg="#2D1B4E", fg=WHITE).pack(fill="x", ipady=14)

            card = tk.Frame(win, bg=PANEL, padx=24, pady=18)
            card.pack(fill="x", padx=16, pady=8)
            tk.Label(card, text="Order Summary",
                     font=("Georgia",11,"bold"), bg=PANEL, fg=YELLOW).pack(anchor="w", pady=(0,6))

            for label, value in [("Bus", bus_num), ("Route", bus_route),
                                  ("Original Price", f"PKR {orig:,}")]:
                r = tk.Frame(card, bg=PANEL); r.pack(fill="x", pady=1)
                tk.Label(r, text=label, bg=PANEL, fg=WHITE,
                         font=FONT_SMALL, width=18, anchor="w").pack(side="left")
                tk.Label(r, text=value, bg=PANEL, fg=WHITE, font=FONT_SMALL).pack(side="left")

            if disc > 0:
                r = tk.Frame(card, bg=PANEL); r.pack(fill="x", pady=1)
                tk.Label(r, text="Promo Discount", bg=PANEL, fg=WHITE,
                         font=FONT_SMALL, width=18, anchor="w").pack(side="left")
                tk.Label(r, text=f"-PKR {disc:,}  ({promo['code']})",
                         bg=PANEL, fg=GREEN, font=FONT_SMALL).pack(side="left")

            r = tk.Frame(card, bg=PANEL); r.pack(fill="x", pady=(4,0))
            tk.Label(r, text="Amount Due", bg=PANEL, fg=WHITE,
                     font=("Segoe UI",11,"bold"), width=18, anchor="w").pack(side="left")
            tk.Label(r, text=f"PKR {due:,}",
                     bg=PANEL, fg=GOLD, font=("Georgia",13,"bold")).pack(side="left")

            methods    = [pm for pm in get_payment_methods() if pm["enabled"]]
            method_var = tk.StringVar(value=methods[0]["name"] if methods else "")
            tk.Label(win, text="Select Payment Method",
                     font=("Segoe UI",10,"bold"), bg=BG, fg=WHITE).pack(anchor="w", padx=24, pady=(4,2))
            icons = {"Credit":"💳","Online":"🏦","Mobile":"📱","Bank":"🏧"}
            for pm in methods:
                icon = next((v for k,v in icons.items() if k in pm["name"]), "💰")
                tk.Radiobutton(win, text=f" {icon}  {pm['name']}",
                               variable=method_var, value=pm["name"],
                               bg=BG, fg=WHITE, selectcolor=ACCENT,
                               activebackground=BG, font=FONT_BODY,
                               cursor="hand2").pack(anchor="w", padx=32)

            detail_frame = tk.Frame(win, bg=BG)
            detail_frame.pack(fill="x", padx=24, pady=4)
            detail_entry = [None]

            def _update_details(*_):
                for w in detail_frame.winfo_children(): w.destroy()
                method = method_var.get()
                if "Mobile" in method:
                    tk.Label(detail_frame, text="Mobile Number (e.g. 0301-1234567):",
                             bg=BG, fg=WHITE, font=FONT_SMALL).pack(anchor="w")
                    e = tk.Entry(detail_frame, font=FONT_BODY, bg=ACCENT, fg=WHITE,
                                 insertbackground=WHITE, width=28)
                    e.pack(anchor="w", ipady=4); detail_entry[0] = e
                elif "Card" in method:
                    tk.Label(detail_frame, text="Card Number (last 4 digits):",
                             bg=BG, fg=WHITE, font=FONT_SMALL).pack(anchor="w")
                    e = tk.Entry(detail_frame, font=FONT_BODY, bg=ACCENT, fg=WHITE,
                                 insertbackground=WHITE, width=20)
                    e.pack(anchor="w", ipady=4); detail_entry[0] = e
                elif "Banking" in method:
                    tk.Label(detail_frame, text="Account / IBAN Number:",
                             bg=BG, fg=WHITE, font=FONT_SMALL).pack(anchor="w")
                    e = tk.Entry(detail_frame, font=FONT_BODY, bg=ACCENT, fg=WHITE,
                                 insertbackground=WHITE, width=32)
                    e.pack(anchor="w", ipady=4); detail_entry[0] = e
                elif "Transfer" in method:
                    tk.Label(detail_frame, text="Sender Account / Bank Name:",
                             bg=BG, fg=WHITE, font=FONT_SMALL).pack(anchor="w")
                    e = tk.Entry(detail_frame, font=FONT_BODY, bg=ACCENT, fg=WHITE,
                                 insertbackground=WHITE, width=32)
                    e.pack(anchor="w", ipady=4); detail_entry[0] = e
                else:
                    detail_entry[0] = None

            method_var.trace_add("write", _update_details)
            _update_details()

            err_pay = tk.Label(win, text="", bg=BG, fg=RED, font=FONT_SMALL)
            err_pay.pack()

            def _pay():
                method = method_var.get()
                detail = ""
                if detail_entry[0]:
                    detail = detail_entry[0].get().strip()
                    if not detail:
                        err_pay.config(text="⚠ Please fill in payment details."); return

                proc = tk.Toplevel(win)
                proc.title("Processing")
                proc.configure(bg=BG)
                proc.geometry("260x90")
                px=(self.winfo_screenwidth()-260)//2; py=(self.winfo_screenheight()-90)//2
                proc.geometry(f"260x90+{px}+{py}"); proc.grab_set()
                tk.Label(proc, text="⏳  Processing payment...",
                         bg=BG, fg=YELLOW, font=FONT_BODY).pack(expand=True)
                proc.update(); time.sleep(1.2); proc.destroy()

                pid = add_passenger(vals["name"], vals["cnic"], vals["email"], vals["phone"])
                if is_full:
                    bid = add_waitlist_booking(pid, bus_id_sel, self.user["id"])
                    wl_rec = {"id":bid,"name":vals["name"],"cnic":vals["cnic"],
                              "seat_number":"N/A","bus_number":bus_num,
                              "booking_date":str(datetime.now()),"status":"waitlisted"}
                    self.hash_table.insert(bid, wl_rec)
                    self.passenger_bst.insert(vals["name"], wl_rec)
                    self.waitlist.enqueue({**wl_rec,"booking_id":bid,
                                          "passenger_id":pid,"bus_id":bus_id_sel})
                    pay_data = record_payment(bid, due, orig,
                                             promo["code"] if promo else None,
                                             disc, method, detail)
                    if promo: use_promo(promo["code"])
                    _show_success(win, vals["name"], bus_num, "Waitlisted",
                                  pay_data, due, method, disc, promo)
                else:
                    seats     = get_seats_for_bus(bus_id_sel)
                    free_seat = next((s for s in seats if not s["is_booked"]), None)
                    if not free_seat:
                        win.destroy()
                        messagebox.showwarning("Full","Bus just filled up! Try again or pick another bus.")
                        return
                    bid = book_seat(pid, free_seat["id"], self.user["id"], vals["cnic"])
                    full_bk = {"id":bid,"name":vals["name"],"cnic":vals["cnic"],
                               "seat_number":str(free_seat["seat_number"]),
                               "bus_number":bus_num,
                               "booking_date":str(datetime.now()),"status":"confirmed"}
                    self.hash_table.insert(bid, full_bk)
                    self.passenger_bst.insert(vals["name"], full_bk)
                    pay_data = record_payment(bid, due, orig,
                                             promo["code"] if promo else None,
                                             disc, method, detail)
                    if promo: use_promo(promo["code"])
                    _show_success(win, vals["name"], bus_num,
                                  str(free_seat["seat_number"]),
                                  pay_data, due, method, disc, promo)

            tk.Button(win, text=f"✅  Pay PKR {due:,}",
                      bg=GREEN, fg=BG, font=("Georgia",12,"bold"),
                      pady=10, cursor="hand2", bd=0,
                      command=_pay).pack(fill="x", padx=24, pady=(6,2))
            tk.Button(win, text="✖  Cancel",
                      bg=ACCENT, fg=WHITE, font=FONT_BTN,
                      cursor="hand2", bd=0,
                      command=win.destroy).pack(padx=24, pady=(0,8))

        def _show_success(parent_win, name, bus_num, seat,
                          pay_data, due, method, disc, promo):
            parent_win.destroy()
            swin = tk.Toplevel(self)
            swin.title("Payment Successful")
            swin.configure(bg=BG)
            swin.geometry("420x420")
            swin.grab_set()
            x=(self.winfo_screenwidth()-420)//2; y=(self.winfo_screenheight()-420)//2
            swin.geometry(f"420x420+{x}+{y}")

            tk.Label(swin, text="✅",  font=("Segoe UI",40), bg=BG, fg=GREEN).pack(pady=(20,4))
            tk.Label(swin, text="Payment Successful!",
                     font=("Georgia",18,"bold"), bg=BG, fg=GREEN).pack()
            tk.Label(swin, text=f"PKR {due:,}  •   {method}",
                     font=FONT_SMALL, bg=BG, fg=YELLOW).pack(pady=(2,10))

            card = tk.Frame(swin, bg=PANEL, padx=24, pady=14)
            card.pack(padx=24, fill="x")
            for label, value in [("Bus",bus_num),("Seat",seat),
                                  ("Ticket No",pay_data["ticket_no"]),
                                  ("Invoice No",pay_data["invoice_no"]),
                                  ("Reference",pay_data["txn_ref"])]:
                r = tk.Frame(card, bg=PANEL); r.pack(fill="x", pady=2)
                tk.Label(r, text=label, bg=PANEL, fg=YELLOW,
                         font=FONT_SMALL, width=14, anchor="w").pack(side="left")
                tk.Label(r, text=value, bg=PANEL, fg=WHITE,
                         font=FONT_SMALL).pack(side="left")

            btn_row = tk.Frame(swin, bg=BG)
            btn_row.pack(pady=14)
            tk.Button(btn_row, text="🎫 Ticket PDF",
                      bg=BLUE, fg=WHITE, font=FONT_BTN, cursor="hand2", bd=0,
                      command=lambda: _generate_ticket_pdf(
                          name, bus_num, seat, pay_data, due, method, disc, promo)
                      ).pack(side="left", padx=6, ipadx=8, ipady=6)
            tk.Button(btn_row, text="📄Invoice PDF",
                      bg=PURPLE, fg=WHITE, font=FONT_BTN, cursor="hand2", bd=0,
                      command=lambda: _generate_invoice_pdf(
                          name, bus_num, pay_data, due, disc, promo)
                      ).pack(side="left", padx=6, ipadx=8, ipady=6)
            tk.Button(swin, text="Close",
                      bg=ACCENT, fg=WHITE, font=FONT_BTN,
                      cursor="hand2", bd=0,
                      command=swin.destroy).pack(pady=(0,10))
    def _show_my_bookings(self):
        self._clear()
        self._heading("My Bookings", f"Your booking history — {self.user['username']}")
        wrap = self._scrollable()

        bookings = get_bookings_for_user(self.user["id"])

        # Summary card
        total = sum(b.get("amount_paid",1500) for b in bookings if b["status"]=="confirmed")
        card = tk.Frame(wrap, bg=CARD1, padx=24, pady=16)
        card.pack(padx=24, pady=(8,12), anchor="w")
        tk.Label(card, text=f"PKR {total:,.2f}",
                 font=("Georgia",24,"bold"), bg=CARD1, fg=GOLD).pack()
        tk.Label(card, text="Total Spent (confirmed bookings)",
                 font=FONT_SMALL, bg=CARD1, fg=WHITE).pack()
        tk.Label(card, text=f"{len(bookings)} booking(s) found",
                 font=FONT_SMALL, bg=CARD1, fg=YELLOW).pack()

        if not bookings:
            tk.Label(wrap,
                     text="No bookings yet — go to Book a Seat to make your first booking!",
                     bg=BG, fg=YELLOW, font=FONT_BODY).pack(pady=30)
            return

        cols = ("ID","Bus","Route","Date","Promo","Paid","Status")
        t_f  = tk.Frame(wrap, bg=BG)
        t_f.pack(fill="x", padx=24)
        tree = ttk.Treeview(t_f, columns=cols, show="headings", height=20)
        vsb  = ttk.Scrollbar(t_f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        for c,w in zip(cols,[50,90,180,130,80,100,90]):
            tree.heading(c,text=c); tree.column(c,width=w,anchor="w")
        tree.tag_configure("cancelled", foreground=RED)
        for b in bookings:
            tag = ("cancelled",) if b["status"]=="cancelled" else ()
            tree.insert("","end", tags=tag, values=(
                b["id"], b.get("bus_number","N/A"), b.get("route","N/A"),
                str(b["booking_date"])[:16],
                b.get("promo_code","—"),
                f"PKR {b.get('amount_paid',1500):,.0f}",
                b["status"]))
        tree.pack(side="left", fill="x", expand=True)
        vsb.pack(side="right", fill="y")
    def _show_my_waitlist(self):
        self._clear()
        self._heading("My Waitlist", f"Buses you're waiting for — {self.user['username']}")
        wrap = self._scrollable()

        rows = get_waitlist_for_user(self.user["id"])

        if not rows:
            tk.Label(wrap, text="You are not on any waitlist.",
                     bg=BG, fg=YELLOW, font=FONT_BODY).pack(pady=30)
            return

        cols = ("ID","Bus","Route","Joined At","Queue Position")
        t_f  = tk.Frame(wrap, bg=BG)
        t_f.pack(fill="x", padx=24, pady=8)
        tree = ttk.Treeview(t_f, columns=cols, show="headings", height=18)
        vsb  = ttk.Scrollbar(t_f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        for c,w in zip(cols,[50,90,200,150,120]):
            tree.heading(c,text=c); tree.column(c,width=w,anchor="w")
        for r in rows:
            tree.insert("","end", values=(
                r["id"], r["bus_number"], r["route"],
                str(r["booking_date"])[:16], f"#{r['position']}"))
        tree.pack(side="left", fill="x", expand=True)
        vsb.pack(side="right", fill="y")
    def _show_feedback(self):
        self._clear(); self._heading("Feedback & Reviews",f"Rate your journeys — {self.user['username']}")
        wrap=self._scrollable()
        pid=get_passenger_id_by_user_id(self.user["id"])
        sub_frame=tk.Frame(wrap,bg=PANEL,padx=24,pady=18); sub_frame.pack(padx=24,fill="x",pady=(8,4))
        tk.Label(sub_frame,text="Submit New Feedback",bg=PANEL,fg=WHITE,font=FONT_HEAD).pack(anchor="w",pady=(0,8))
        tk.Label(sub_frame,text="Select Bus:",bg=PANEL,fg=WHITE,font=FONT_BODY).pack(anchor="w")
        buses=get_all_buses(); bus_map={f"{b['bus_number']} — {b['route']}":b for b in buses}
        bus_var=tk.StringVar()
        ttk.Combobox(sub_frame,textvariable=bus_var,values=list(bus_map.keys()),width=36,state="readonly").pack(anchor="w",pady=(2,8))
        tk.Label(sub_frame,text="Rating:",bg=PANEL,fg=WHITE,font=FONT_BODY).pack(anchor="w")
        rating_var=tk.IntVar(value=5)
        star_row=tk.Frame(sub_frame,bg=PANEL); star_row.pack(anchor="w",pady=(2,8))
        for i in range(1,6):
            tk.Radiobutton(star_row,text="★"*i,variable=rating_var,value=i,bg=PANEL,fg=GOLD,
                           selectcolor=PANEL,activebackground=PANEL,font=("Segoe UI",12),cursor="hand2").pack(side="left",padx=2)
        tk.Label(sub_frame,text="Comment:",bg=PANEL,fg=WHITE,font=FONT_BODY).pack(anchor="w")
        comment_e=tk.Text(sub_frame,font=FONT_BODY,bg=ACCENT,fg=WHITE,insertbackground=WHITE,width=44,height=4)
        comment_e.pack(anchor="w",pady=(2,8))
        sub_err=tk.Label(sub_frame,text="",bg=PANEL,fg=RED,font=FONT_SMALL); sub_err.pack()
        def _submit():
            if not pid: sub_err.config(text="⚠ No passenger record found for your username."); return
            bk=bus_map.get(bus_var.get())
            if not bk: sub_err.config(text="⚠ Select a bus."); return
            comment=comment_e.get("1.0",tk.END).strip()
            submit_feedback(pid,bk["id"],rating_var.get(),comment)
            sub_err.config(text=""); messagebox.showinfo("Thanks","Feedback submitted! ⭐"); self._show_feedback()
        tk.Button(sub_frame,text="⭐  Submit Feedback",bg=GREEN,fg=BG,font=FONT_BTN,pady=7,cursor="hand2",bd=0,command=_submit).pack(anchor="w")
        if pid:
            tk.Label(wrap,text="Your Previous Feedback",font=FONT_HEAD,bg=BG,fg=YELLOW).pack(anchor="w",padx=24,pady=(16,4))
            for f in get_feedback_for_passenger(pid):
                card=tk.Frame(wrap,bg=PANEL,padx=16,pady=10); card.pack(fill="x",padx=24,pady=3)
                top_row=tk.Frame(card,bg=PANEL); top_row.pack(fill="x")
                tk.Label(top_row,text=f"{f['bus_number']} — {f['route']}",bg=PANEL,fg=WHITE,font=("Segoe UI",11,"bold")).pack(side="left")
                tk.Label(top_row,text="★"*f["rating"]+"☆"*(5-f["rating"]),bg=PANEL,fg=GOLD,font=("Segoe UI",12)).pack(side="left",padx=8)
                tk.Label(top_row,text=str(f["created_at"])[:16],bg=PANEL,fg=YELLOW,font=FONT_SMALL).pack(side="right")
                if f.get("comment"):
                    tk.Label(card,text=f["comment"],bg=PANEL,fg=WHITE,font=FONT_SMALL,wraplength=700,justify="left").pack(anchor="w",pady=(4,0))
                def _del(fid=f["id"]):
                    if messagebox.askyesno("Delete","Delete this feedback?"): delete_feedback(fid); self._show_feedback()
                tk.Button(card,text="🗑 Delete",bg=RED,fg=WHITE,font=FONT_SMALL,cursor="hand2",bd=0,command=_del).pack(anchor="w",pady=(6,0))


# PDF GENERATION
def _generate_ticket_pdf(name, bus_num, seat, pay_data, due, method, disc, promo):
    try:
        import pathlib, os
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm, mm
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                         Paragraph, Spacer)
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        folder = pathlib.Path(r"D:\BusSeatReservation")
        folder.mkdir(parents=True, exist_ok=True)
        path = str(folder / f"Ticket_{pay_data['ticket_no']}.pdf")

        BG_C    = colors.HexColor("#1C0F0A")
        HEADER_C= colors.HexColor("#6B3A2A")
        PANEL_C = colors.HexColor("#2C1810")
        ALT_C   = colors.HexColor("#3D1F0D")
        GOLD_C  = colors.HexColor("#E8A44A")
        CREAM_C = colors.HexColor("#F5E6D3")
        GREEN_C = colors.HexColor("#7D9B6A")
        ACC_C   = colors.HexColor("#6B3A2A")

        doc = SimpleDocTemplate(path, pagesize=A4,
              topMargin=2*cm, bottomMargin=2*cm,
              leftMargin=2.5*cm, rightMargin=2.5*cm)

        def sty(size=10, color=CREAM_C, bold=False, align=TA_LEFT, space=0):
            return ParagraphStyle("s", fontSize=size,
                textColor=color,
                fontName="Helvetica-Bold" if bold else "Helvetica",
                alignment=align, spaceAfter=space, leading=size*1.4)

        def row(label, value, alt=False):
            bg = ALT_C if alt else PANEL_C
            return ([Paragraph(label, sty(10, GOLD_C, bold=True)),
                     Paragraph(str(value), sty(10, CREAM_C))], bg)

        story = []

        # ── Header block ─────────────────────────────────────────────
        header_data = [[
            Paragraph("BUS TICKET", sty(22, GOLD_C, bold=True, align=TA_CENTER)),
        ]]
        h = Table(header_data, colWidths=[15*cm])
        h.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), HEADER_C),
            ("TOPPADDING",    (0,0),(-1,-1), 14),
            ("BOTTOMPADDING", (0,0),(-1,-1), 14),
            ("ROUNDEDCORNERS",[4]),
        ]))
        story.append(h)
        story.append(Spacer(1, 3*mm))

        sub_data = [[
            Paragraph(f"Ticket No: {pay_data['ticket_no']}", sty(9, GOLD_C, align=TA_CENTER)),
            Paragraph(f"Issued: {datetime.now().strftime('%d %B %Y  %H:%M')}", sty(9, CREAM_C, align=TA_RIGHT)),
        ]]
        sub = Table(sub_data, colWidths=[7.5*cm, 7.5*cm])
        sub.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,-1), PANEL_C),
            ("TOPPADDING", (0,0),(-1,-1), 6),
            ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ]))
        story.append(sub)
        story.append(Spacer(1, 5*mm))

        # ── Details table ─────────────────────────────────────────────
        rows_data = [
            row("Passenger",     name,       False),
            row("Bus",           bus_num,    True),
            row("Seat No.",      seat,       False),
            row("Payment Method",method,     True),
        ]
        if promo:
            rows_data.append(row("Promo Code", f"{promo['code']}  (discount: PKR {disc:,})", False))
            rows_data.append(row("Original Price", f"PKR {due+disc:,}", True))
        rows_data.append(row("Amount Paid", f"PKR {due:,}", False))
        rows_data.append(row("Invoice No.", pay_data['invoice_no'], True))
        rows_data.append(row("Reference",   pay_data['txn_ref'],   False))

        tbl_rows  = [r[0] for r in rows_data]
        tbl_style = [
            ("GRID",         (0,0),(-1,-1), 0.5, ACC_C),
            ("TOPPADDING",   (0,0),(-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("LEFTPADDING",  (0,0),(-1,-1), 12),
            ("RIGHTPADDING", (0,0),(-1,-1), 12),
            ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ]
        for i, (_, bg) in enumerate(rows_data):
            tbl_style.append(("BACKGROUND", (0,i),(1,i), bg))
        # Highlight amount paid row
        paid_idx = len(rows_data) - 3 if promo else len(rows_data) - 3
        amt_idx  = next(i for i,(r,_) in enumerate(rows_data) if "Amount Paid" in r[0].text)
        tbl_style.append(("BACKGROUND", (0,amt_idx),(1,amt_idx), colors.HexColor("#1A3A1A")))
        tbl_style.append(("TEXTCOLOR",  (0,amt_idx),(1,amt_idx), GREEN_C))

        tbl = Table(tbl_rows, colWidths=[5*cm, 10*cm])
        tbl.setStyle(TableStyle(tbl_style))
        story.append(tbl)
        story.append(Spacer(1, 8*mm))

        # ── Footer ────────────────────────────────────────────────────
        story.append(Paragraph(
            "BusRes  —  Bahria University  |  Thank you for traveling with us!",
            sty(8, ACC_C, align=TA_CENTER)))

        def _draw_bg(canvas, doc):
            canvas.saveState()
            canvas.setFillColor(BG_C)
            canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
            canvas.restoreState()

        doc.build(story, onFirstPage=_draw_bg, onLaterPages=_draw_bg)
        os.startfile(path)
    except Exception as ex:
        messagebox.showerror("Ticket Error", str(ex))


def _generate_invoice_pdf(name, bus_num, pay_data, due, disc, promo):
    try:
        import pathlib, os
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm, mm
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                         Paragraph, Spacer, HRFlowable)
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        folder = pathlib.Path(r"D:\BusSeatReservation")
        folder.mkdir(parents=True, exist_ok=True)
        path = str(folder / f"Invoice_{pay_data['invoice_no']}.pdf")
        orig = due + disc

        BG_C    = colors.HexColor("#1C0F0A")
        HEADER_C= colors.HexColor("#6B3A2A")
        PANEL_C = colors.HexColor("#2C1810")
        ALT_C   = colors.HexColor("#3D1F0D")
        GOLD_C  = colors.HexColor("#E8A44A")
        CREAM_C = colors.HexColor("#F5E6D3")
        GREEN_C = colors.HexColor("#7D9B6A")
        ACC_C   = colors.HexColor("#6B3A2A")
        RED_C   = colors.HexColor("#C0392B")

        doc = SimpleDocTemplate(path, pagesize=A4,
              topMargin=2*cm, bottomMargin=2*cm,
              leftMargin=2.5*cm, rightMargin=2.5*cm)

        def sty(size=10, color=CREAM_C, bold=False, align=TA_LEFT, space=0):
            return ParagraphStyle("s", fontSize=size,
                textColor=color,
                fontName="Helvetica-Bold" if bold else "Helvetica",
                alignment=align, spaceAfter=space, leading=size*1.5)

        story = []

        # ── Header: logo left, INVOICE right ─────────────────────────
        hdr = Table([[
            Paragraph("BusRes", sty(26, GOLD_C, bold=True)),
            Paragraph("INVOICE", sty(26, CREAM_C, bold=True, align=TA_RIGHT)),
        ]], colWidths=[7.5*cm, 7.5*cm])
        hdr.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), HEADER_C),
            ("TOPPADDING",    (0,0),(-1,-1), 16),
            ("BOTTOMPADDING", (0,0),(-1,-1), 16),
            ("LEFTPADDING",   (0,0),(-1,-1), 14),
            ("RIGHTPADDING",  (0,0),(-1,-1), 14),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ]))
        story.append(hdr)
        story.append(Spacer(1, 5*mm))

        # ── Meta info ────────────────────────────────────────────────
        meta = Table([[
            Paragraph(f"Invoice No:  {pay_data['invoice_no']}", sty(9, GOLD_C)),
            Paragraph(f"Date:  {datetime.now().strftime('%d %B %Y  %H:%M')}", sty(9, CREAM_C, align=TA_RIGHT)),
        ],[
            Paragraph(f"Bill To:  {name}", sty(10, CREAM_C, bold=True)),
            Paragraph("", sty(9)),
        ]], colWidths=[7.5*cm, 7.5*cm])
        meta.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), PANEL_C),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("RIGHTPADDING",  (0,0),(-1,-1), 10),
            ("LINEBELOW",     (0,1),(-1,1),  0.5, ACC_C),
        ]))
        story.append(meta)
        story.append(Spacer(1, 6*mm))

        # ── Line items table ─────────────────────────────────────────
        item_rows = [[
            Paragraph("Description", sty(10, CREAM_C, bold=True)),
            Paragraph("Amount",      sty(10, CREAM_C, bold=True, align=TA_RIGHT)),
        ],[
            Paragraph(f"Bus Booking  —  {bus_num}", sty(10, CREAM_C)),
            Paragraph(f"PKR {orig:,}", sty(10, CREAM_C, align=TA_RIGHT)),
        ]]
        if promo:
            item_rows.append([
                Paragraph(f"Promo Discount  ({promo['code']})", sty(10, GREEN_C)),
                Paragraph(f"- PKR {disc:,}", sty(10, GREEN_C, align=TA_RIGHT)),
            ])
        item_rows.append([
            Paragraph("Total Paid", sty(12, GOLD_C, bold=True)),
            Paragraph(f"PKR {due:,}", sty(12, GOLD_C, bold=True, align=TA_RIGHT)),
        ])

        n = len(item_rows)
        item_tbl = Table(item_rows, colWidths=[11*cm, 4*cm])
        item_style = [
            ("BACKGROUND",    (0,0),(-1,0),  HEADER_C),
            ("BACKGROUND",    (0,n-1),(-1,n-1), colors.HexColor("#1A3A1A")),
            ("GRID",          (0,0),(-1,-1),  0.5, ACC_C),
            ("TOPPADDING",    (0,0),(-1,-1),  10),
            ("BOTTOMPADDING", (0,0),(-1,-1),  10),
            ("LEFTPADDING",   (0,0),(-1,-1),  12),
            ("RIGHTPADDING",  (0,0),(-1,-1),  12),
            ("VALIGN",        (0,0),(-1,-1),  "MIDDLE"),
        ]
        for i in range(1, n-1):
            bg = ALT_C if i % 2 == 0 else PANEL_C
            item_style.append(("BACKGROUND", (0,i),(-1,i), bg))
        item_tbl.setStyle(TableStyle(item_style))
        story.append(item_tbl)
        story.append(Spacer(1, 8*mm))

        # ── Payment details row ───────────────────────────────────────
        pay_det = Table([[
            Paragraph(f"Payment Method:  {pay_data.get('method','N/A')}", sty(9, CREAM_C)),
            Paragraph(f"Reference:  {pay_data['txn_ref']}", sty(9, CREAM_C, align=TA_RIGHT)),
        ],[
            Paragraph(f"Ticket No:  {pay_data['ticket_no']}", sty(9, GOLD_C)),
            Paragraph("", sty(9)),
        ]], colWidths=[7.5*cm, 7.5*cm])
        pay_det.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), PANEL_C),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("RIGHTPADDING",  (0,0),(-1,-1), 10),
            ("LINEABOVE",     (0,0),(-1,0),  0.5, ACC_C),
        ]))
        story.append(pay_det)
        story.append(Spacer(1, 6*mm))
        story.append(Paragraph(
            "BusRes  —  Bahria University  |  Computer-generated invoice.",
            sty(8, ACC_C, align=TA_CENTER)))

        def _draw_bg(canvas, doc):
            canvas.saveState()
            canvas.setFillColor(BG_C)
            canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
            canvas.restoreState()

        doc.build(story, onFirstPage=_draw_bg, onLaterPages=_draw_bg)
        os.startfile(path)
    except Exception as ex:
        messagebox.showerror("Invoice Error", str(ex))


if __name__ == "__main__":
    ensure_schema()
    LoginWindow().mainloop()        
