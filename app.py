import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import calendar
import json
import os
from datetime import datetime, date
import threading
import time

# ─────────────────────────── Data Storage ────────────────────────────

DATA_FILE = "reminders.json"

def load_reminders():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_reminders(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─────────────────────────── Reminder Dialog ──────────────────────────

class ReminderDialog(tk.Toplevel):
    def __init__(self, parent, date_str, existing=None):
        super().__init__(parent)
        self.title(f"📅 Reminder — {date_str}")
        self.geometry("420x400")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")
        self.result = None
        self.date_str = date_str

        self.transient(parent)
        self.grab_set()

        # Center on screen
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 420) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 320) // 2
        self.geometry(f"+{x}+{y}")

        self._build_ui(existing)

    def _build_ui(self, existing):
        # Header
        header = tk.Frame(self, bg="#313244", pady=12)
        header.pack(fill="x")
        tk.Label(header, text="✨ Add / Edit Reminder",
                 font=("Georgia", 14, "bold"),
                 bg="#313244", fg="#cba6f7").pack()
        tk.Label(header, text=self.date_str,
                 font=("Courier New", 10),
                 bg="#313244", fg="#a6e3a1").pack()

        body = tk.Frame(self, bg="#1e1e2e", padx=24, pady=16)
        body.pack(fill="both", expand=True)

        # Title
        tk.Label(body, text="Title", font=("Georgia", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(anchor="w")
        self.title_var = tk.StringVar(value=existing.get("title", "") if existing else "")
        title_entry = tk.Entry(body, textvariable=self.title_var,
                               font=("Courier New", 11),
                               bg="#313244", fg="#cdd6f4",
                               insertbackground="#cba6f7",
                               relief="flat", bd=6)
        title_entry.pack(fill="x", pady=(2, 10))
        title_entry.focus()

        # Time
        tk.Label(body, text="Time (HH:MM, optional)", font=("Georgia", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(anchor="w")
        self.time_var = tk.StringVar(value=existing.get("time", "") if existing else "")
        tk.Entry(body, textvariable=self.time_var,
                 font=("Courier New", 11),
                 bg="#313244", fg="#cdd6f4",
                 insertbackground="#cba6f7",
                 relief="flat", bd=6).pack(fill="x", pady=(2, 10))

        # Note
        tk.Label(body, text="Note (optional)", font=("Georgia", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(anchor="w")
        self.note_text = tk.Text(body, height=3,
                                  font=("Courier New", 10),
                                  bg="#313244", fg="#cdd6f4",
                                  insertbackground="#cba6f7",
                                  relief="flat", bd=6, wrap="word")
        self.note_text.pack(fill="x", pady=(2, 14))
        if existing and existing.get("note"):
            self.note_text.insert("1.0", existing["note"])

        # Buttons
        btn_frame = tk.Frame(body, bg="#1e1e2e")
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="Save ✓",
                  font=("Georgia", 10, "bold"),
                  bg="#a6e3a1", fg="#1e1e2e", relief="flat",
                  padx=18, pady=6, cursor="hand2",
                  command=self._save).pack(side="left", padx=(0, 8))
        tk.Button(btn_frame, text="Cancel ✗",
                  font=("Georgia", 10),
                  bg="#f38ba8", fg="#1e1e2e", relief="flat",
                  padx=18, pady=6, cursor="hand2",
                  command=self.destroy).pack(side="left")

    def _save(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Missing Title", "Please enter a title.", parent=self)
            return
        self.result = {
            "title": title,
            "time": self.time_var.get().strip(),
            "note": self.note_text.get("1.0", "end").strip()
        }
        self.destroy()


# ─────────────────────────── Main App ────────────────────────────────

class CalendarReminderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📅 Calendar & Reminder App")
        self.geometry("900x640")
        self.minsize(780, 580)
        self.configure(bg="#1e1e2e")

        self.reminders = load_reminders()
        self.today = date.today()
        self.current_year = self.today.year
        self.current_month = self.today.month
        self.selected_date = None

        self._setup_styles()
        self._build_ui()
        self._render_calendar()
        self._start_notification_thread()

    # ── Styles ──
    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TScrollbar", background="#313244", troughcolor="#1e1e2e",
                        arrowcolor="#cba6f7", bordercolor="#1e1e2e")

    # ── UI Layout ──
    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self, bg="#181825", pady=14)
        header.pack(fill="x")

        tk.Label(header, text="📅", font=("Segoe UI Emoji", 22),
                 bg="#181825", fg="#cba6f7").pack(side="left", padx=(20, 6))
        tk.Label(header, text="Calendar & Reminder",
                 font=("Georgia", 20, "bold"),
                 bg="#181825", fg="#cdd6f4").pack(side="left")

        self.clock_label = tk.Label(header, text="",
                                     font=("Courier New", 12),
                                     bg="#181825", fg="#89b4fa")
        self.clock_label.pack(side="right", padx=20)
        self._tick_clock()

        # ── Body ──
        body = tk.Frame(self, bg="#1e1e2e")
        body.pack(fill="both", expand=True, padx=18, pady=12)

        # Left — calendar panel
        left = tk.Frame(body, bg="#1e1e2e")
        left.pack(side="left", fill="both", expand=True)

        # Month navigation
        nav = tk.Frame(left, bg="#313244", pady=8)
        nav.pack(fill="x", pady=(0, 8))

        btn_style = {"font": ("Georgia", 13, "bold"), "bg": "#313244",
                     "fg": "#cba6f7", "relief": "flat", "cursor": "hand2",
                     "activebackground": "#45475a", "activeforeground": "#cba6f7"}

        tk.Button(nav, text="◀", command=self._prev_month, **btn_style).pack(side="left", padx=10)
        self.month_label = tk.Label(nav, text="",
                                     font=("Georgia", 15, "bold"),
                                     bg="#313244", fg="#cdd6f4", width=18)
        self.month_label.pack(side="left", expand=True)
        tk.Button(nav, text="▶", command=self._next_month, **btn_style).pack(side="right", padx=10)
        tk.Button(nav, text="Today", command=self._go_today,
                  font=("Georgia", 10), bg="#89b4fa", fg="#1e1e2e",
                  relief="flat", padx=10, pady=3, cursor="hand2").pack(side="right", padx=6)

        # Day headers
        day_frame = tk.Frame(left, bg="#1e1e2e")
        day_frame.pack(fill="x")
        for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            color = "#f38ba8" if d in ("Sat", "Sun") else "#89b4fa"
            tk.Label(day_frame, text=d, font=("Georgia", 10, "bold"),
                     bg="#1e1e2e", fg=color, width=7).grid(row=0, column=i, pady=4)

        # Calendar grid
        self.cal_frame = tk.Frame(left, bg="#1e1e2e")
        self.cal_frame.pack(fill="both", expand=True)

        # Right — reminders panel
        right = tk.Frame(body, bg="#181825", width=260, padx=14, pady=14)
        right.pack(side="right", fill="y", padx=(16, 0))
        right.pack_propagate(False)

        tk.Label(right, text="🔔 Reminders",
                 font=("Georgia", 13, "bold"),
                 bg="#181825", fg="#cba6f7").pack(anchor="w")

        self.sel_date_label = tk.Label(right, text="Select a date",
                                        font=("Courier New", 10),
                                        bg="#181825", fg="#6c7086")
        self.sel_date_label.pack(anchor="w", pady=(2, 8))

        # Add button
        tk.Button(right, text="＋ Add Reminder",
                  font=("Georgia", 10, "bold"),
                  bg="#a6e3a1", fg="#1e1e2e", relief="flat",
                  pady=6, cursor="hand2",
                  command=self._add_reminder).pack(fill="x", pady=(0, 10))

        # Reminder list
        list_frame = tk.Frame(right, bg="#181825")
        list_frame.pack(fill="both", expand=True)

        scroll = ttk.Scrollbar(list_frame, orient="vertical")
        scroll.pack(side="right", fill="y")

        self.reminder_listbox = tk.Listbox(list_frame,
                                            font=("Courier New", 10),
                                            bg="#313244", fg="#cdd6f4",
                                            selectbackground="#cba6f7",
                                            selectforeground="#1e1e2e",
                                            relief="flat", bd=0,
                                            yscrollcommand=scroll.set,
                                            activestyle="none", cursor="hand2")
        self.reminder_listbox.pack(fill="both", expand=True)
        scroll.config(command=self.reminder_listbox.yview)
        self.reminder_listbox.bind("<Double-Button-1>", self._edit_reminder)

        # Action buttons
        action_frame = tk.Frame(right, bg="#181825", pady=6)
        action_frame.pack(fill="x")
        tk.Button(action_frame, text="✏ Edit",
                  font=("Georgia", 9), bg="#89b4fa", fg="#1e1e2e",
                  relief="flat", padx=10, pady=4, cursor="hand2",
                  command=self._edit_reminder).pack(side="left", padx=(0, 6))
        tk.Button(action_frame, text="🗑 Delete",
                  font=("Georgia", 9), bg="#f38ba8", fg="#1e1e2e",
                  relief="flat", padx=10, pady=4, cursor="hand2",
                  command=self._delete_reminder).pack(side="left")

        # ── Status bar ──
        self.status_bar = tk.Label(self, text="Welcome! Click a date to manage reminders.",
                                    font=("Courier New", 9),
                                    bg="#11111b", fg="#6c7086",
                                    anchor="w", padx=14, pady=4)
        self.status_bar.pack(fill="x", side="bottom")

    # ── Calendar Rendering ──
    def _render_calendar(self):
        for widget in self.cal_frame.winfo_children():
            widget.destroy()

        self.month_label.config(
            text=f"{calendar.month_name[self.current_month]}  {self.current_year}")

        cal = calendar.monthcalendar(self.current_year, self.current_month)

        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    tk.Label(self.cal_frame, text="", bg="#1e1e2e",
                             width=7, height=3).grid(row=week_num, column=day_num, padx=2, pady=2)
                    continue

                date_obj = date(self.current_year, self.current_month, day)
                date_str = date_obj.strftime("%Y-%m-%d")
                has_reminder = date_str in self.reminders and len(self.reminders[date_str]) > 0
                is_today = date_obj == self.today
                is_selected = date_str == self.selected_date
                is_weekend = day_num >= 5  # Sat, Sun

                # Styling
                if is_selected:
                    bg = "#cba6f7"; fg = "#1e1e2e"
                elif is_today:
                    bg = "#89b4fa"; fg = "#1e1e2e"
                elif is_weekend:
                    bg = "#2a2040"; fg = "#f38ba8"
                else:
                    bg = "#313244"; fg = "#cdd6f4"

                cell = tk.Frame(self.cal_frame, bg=bg, cursor="hand2")
                cell.grid(row=week_num, column=day_num, padx=2, pady=2, sticky="nsew")
                self.cal_frame.grid_columnconfigure(day_num, weight=1)
                self.cal_frame.grid_rowconfigure(week_num, weight=1)

                tk.Label(cell, text=str(day),
                         font=("Georgia", 13, "bold") if is_today or is_selected else ("Georgia", 12),
                         bg=bg, fg=fg).pack(expand=True)

                if has_reminder:
                    count = len(self.reminders[date_str])
                    tk.Label(cell,
                             text=f"{'🔔' * min(count, 3)}",
                             font=("Segoe UI Emoji", 7),
                             bg=bg, fg=fg).pack()

                cell.bind("<Button-1>", lambda e, ds=date_str: self._select_date(ds))
                for child in cell.winfo_children():
                    child.bind("<Button-1>", lambda e, ds=date_str: self._select_date(ds))

    def _select_date(self, date_str):
        self.selected_date = date_str
        self._render_calendar()
        self._refresh_reminders()
        d = datetime.strptime(date_str, "%Y-%m-%d")
        self.sel_date_label.config(text=d.strftime("%A, %d %B %Y"), fg="#a6e3a1")
        self.status_bar.config(text=f"Selected: {date_str}")

    # ── Navigation ──
    def _prev_month(self):
        if self.current_month == 1:
            self.current_month = 12; self.current_year -= 1
        else:
            self.current_month -= 1
        self._render_calendar()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1; self.current_year += 1
        else:
            self.current_month += 1
        self._render_calendar()

    def _go_today(self):
        self.current_year = self.today.year
        self.current_month = self.today.month
        self.selected_date = self.today.strftime("%Y-%m-%d")
        self._render_calendar()
        self._select_date(self.selected_date)

    # ── Reminder CRUD ──
    def _refresh_reminders(self):
        self.reminder_listbox.delete(0, "end")
        if not self.selected_date:
            return
        items = self.reminders.get(self.selected_date, [])
        for i, r in enumerate(items):
            time_str = f"[{r['time']}] " if r.get("time") else ""
            self.reminder_listbox.insert("end", f"  {time_str}{r['title']}")
        if not items:
            self.reminder_listbox.insert("end", "  No reminders for this day.")

    def _add_reminder(self):
        if not self.selected_date:
            messagebox.showinfo("Select a Date", "Please click a date on the calendar first.")
            return
        dlg = ReminderDialog(self, self.selected_date)
        self.wait_window(dlg)
        if dlg.result:
            if self.selected_date not in self.reminders:
                self.reminders[self.selected_date] = []
            self.reminders[self.selected_date].append(dlg.result)
            save_reminders(self.reminders)
            self._render_calendar()
            self._refresh_reminders()
            self.status_bar.config(text=f"✅ Reminder added for {self.selected_date}")

    def _edit_reminder(self, event=None):
        if not self.selected_date:
            return
        sel = self.reminder_listbox.curselection()
        if not sel:
            messagebox.showinfo("Select Reminder", "Please select a reminder to edit.")
            return
        idx = sel[0]
        items = self.reminders.get(self.selected_date, [])
        if idx >= len(items):
            return
        dlg = ReminderDialog(self, self.selected_date, existing=items[idx])
        self.wait_window(dlg)
        if dlg.result:
            items[idx] = dlg.result
            save_reminders(self.reminders)
            self._render_calendar()
            self._refresh_reminders()
            self.status_bar.config(text=f"✏ Reminder updated for {self.selected_date}")

    def _delete_reminder(self):
        if not self.selected_date:
            return
        sel = self.reminder_listbox.curselection()
        if not sel:
            messagebox.showinfo("Select Reminder", "Please select a reminder to delete.")
            return
        idx = sel[0]
        items = self.reminders.get(self.selected_date, [])
        if idx >= len(items):
            return
        confirm = messagebox.askyesno("Delete Reminder",
                                       f"Delete '{items[idx]['title']}'?")
        if confirm:
            items.pop(idx)
            if not items:
                del self.reminders[self.selected_date]
            save_reminders(self.reminders)
            self._render_calendar()
            self._refresh_reminders()
            self.status_bar.config(text=f"🗑 Reminder deleted.")

    # ── Clock ──
    def _tick_clock(self):
        now = datetime.now().strftime("%A, %d %b %Y  |  %H:%M:%S")
        self.clock_label.config(text=now)
        self.after(1000, self._tick_clock)

    # ── Notification Thread ──
    def _start_notification_thread(self):
        def check_loop():
            notified = set()
            while True:
                now = datetime.now()
                today_str = now.strftime("%Y-%m-%d")
                now_time = now.strftime("%H:%M")
                for reminder in self.reminders.get(today_str, []):
                    key = f"{today_str}_{reminder.get('title')}_{reminder.get('time')}"
                    if reminder.get("time") == now_time and key not in notified:
                        notified.add(key)
                        self.after(0, lambda r=reminder: messagebox.showinfo(
                            "🔔 Reminder!",
                            f"{r['title']}\n{r.get('note', '')}"
                        ))
                time.sleep(30)
        t = threading.Thread(target=check_loop, daemon=True)
        t.start()


# ─────────────────────────── Entry Point ────────────────────────────

if __name__ == "__main__":
    app = CalendarReminderApp()
    app.mainloop()
