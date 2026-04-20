# 📅 Calendar & Reminder App

A beautifully designed Python desktop application for managing a monthly calendar with reminders.

---

## ✨ Features

- 📆 Full monthly calendar view with navigation
- 🔔 Add, edit, and delete reminders per day
- 🕐 Set time-based reminders with titles and notes
- 🔴 Visual indicator (🔔) on dates with reminders
- ⏰ Background notification thread — alerts you at reminder time
- 💾 Persistent storage using JSON (reminders survive restarts)
- 🎨 Dark theme UI using Tkinter

---

## 🛠 Requirements

- Python 3.8 or higher
- **No third-party packages needed** — uses Python's built-in `tkinter`, `calendar`, `json`, `threading`, `datetime`

> Tkinter comes bundled with standard Python on Windows and macOS.
> On Linux, install it with:
> ```
> sudo apt install python3-tk
> ```

---

## 🚀 How to Run

### Step 1 — Install Python
Download from https://python.org if not already installed.
Make sure to check **"Add Python to PATH"** during installation.

### Step 2 — Verify Python version
```bash
python --version
```
Should show Python 3.8+

### Step 3 — Run the app
Navigate to the project folder and run:
```bash
python app.py
```
On Linux/macOS you may use:
```bash
python3 app.py
```

### That's it! No pip install needed.

---

## 📖 How to Use

| Action | How |
|---|---|
| Navigate months | Click **◀** / **▶** buttons |
| Go to today | Click **Today** button |
| Select a date | Click on any date cell |
| Add reminder | Select a date → click **＋ Add Reminder** |
| Edit reminder | Select it in the list → click **✏ Edit** or double-click |
| Delete reminder | Select it in the list → click **🗑 Delete** |
| Time notification | Set HH:MM in reminder → get a popup at that time |

---

## 📁 File Structure

```
calendar_reminder_app/
├── app.py            ← Main application file
├── reminders.json    ← Auto-created on first reminder (do not delete!)
└── README.md         ← This file
```

---

## 💡 Notes

- Reminders are saved in `reminders.json` in the same folder as `app.py`
- The notification system checks every 30 seconds; keep the app open for alerts
- Double-click a reminder in the list to edit it quickly

---

Made with ❤️ using Python's built-in Tkinter library.
