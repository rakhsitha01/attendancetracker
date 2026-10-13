"""
Student Attendance Tracker
--------------------------
- Enter student names and mark each one present or absent.
- Display the attendance list.
- Calculate attendance percentage.
- Records are saved in attendance.csv (next to this script).

CSV columns: date, name, status
Taking attendance again for a date that already exists replaces that date.
"""

import csv
import os
from datetime import date, datetime

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.csv")
FIELDS = ["date", "name", "status"]
LOW_ATTENDANCE = 75  # percent; students below this are flagged


def percentage(present, total):
    """Attendance percentage, safe when total is zero."""
    return (present / total) * 100 if total else 0.0


def load_records():
    """Read all records from the CSV file (empty list if none yet)."""
    records = []
    if not os.path.exists(CSV_FILE):
        return records
    try:
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if (row.get("date") and row.get("name")
                        and row.get("status") in ("Present", "Absent")):
                    records.append({k: row[k] for k in FIELDS})
    except OSError as err:
        print(f"  Could not read {CSV_FILE}: {err}")
    return records


def save_records(records):
    """Write all records to the CSV file. Returns True on success."""
    try:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(records)
        return True
    except OSError as err:
        print(f"  Could not save to {CSV_FILE}: {err}")
        print("  If the file is open in Excel, close it and try again.")
        return False


def ask_date():
    """Ask for a date in YYYY-MM-DD form; Enter means today."""
    while True:
        raw = input("Date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not raw:
            return date.today().isoformat()
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date().isoformat()
        except ValueError:
            print("  Invalid date. Use the format YYYY-MM-DD, e.g. 2026-10-13.")


def ask_status(name):
    """Ask whether a student is present or absent."""
    while True:
        raw = input(f"  Is {name} present or absent? (p/a): ").strip().lower()
        if raw in ("p", "present"):
            return "Present"
        if raw in ("a", "absent"):
            return "Absent"
        print("  Please type p for present or a for absent.")


def take_attendance(records):
    """Enter students for one date. Returns the updated records list."""
    session_date = ask_date()

    if any(r["date"] == session_date for r in records):
        answer = input(
            f"Attendance for {session_date} already exists and will be replaced. "
            "Continue? (y/n): "
        ).strip().lower()
        if answer != "y":
            print("  Cancelled. Nothing was changed.")
            return records

    print("Enter student names one by one. Press Enter on an empty name to finish.")
    new_records = []
    seen = set()
    while True:
        name = input("Student name (press Enter to finish): ").strip()
        if not name:
            break
        if name.lower() in seen:
            print(f"  {name} was already entered for this date.")
            continue
        seen.add(name.lower())
        new_records.append({"date": session_date, "name": name, "status": ask_status(name)})

    if not new_records:
        print("  No students entered. Nothing was saved.")
        return records

    updated = [r for r in records if r["date"] != session_date] + new_records
    if save_records(updated):
        present = sum(1 for r in new_records if r["status"] == "Present")
        absent = len(new_records) - present
        print(f"\nSaved attendance for {session_date}: {present} present, {absent} absent.")
        return updated
    return records


def display_attendance(records):
    """Print the attendance list, grouped by date."""
    if not records:
        print("\nNo attendance records yet. Choose option 1 to take attendance.")
        return

    by_date = {}
    for r in records:
        by_date.setdefault(r["date"], []).append(r)

    width = max(4, max(len(r["name"]) for r in records))
    for day in sorted(by_date):
        rows = by_date[day]
        present = sum(1 for r in rows if r["status"] == "Present")
        print(f"\nDate: {day}")
        print(f"  {'No.':<5}{'Name':<{width + 2}}Status")
        print("  " + "-" * (5 + width + 2 + 7))
        for number, r in enumerate(rows, start=1):
            print(f"  {number:<5}{r['name']:<{width + 2}}{r['status']}")
        print(f"  Present: {present}/{len(rows)} ({percentage(present, len(rows)):.2f}%)")


def show_percentage(records):
    """Print each student's attendance percentage and the overall figure."""
    if not records:
        print("\nNo attendance records yet. Choose option 1 to take attendance.")
        return

    stats = {}  # lowercase name -> [display name, days present, days recorded]
    for r in records:
        entry = stats.setdefault(r["name"].lower(), [r["name"], 0, 0])
        entry[2] += 1
        if r["status"] == "Present":
            entry[1] += 1

    width = max(4, max(len(e[0]) for e in stats.values()))
    print("\nAttendance percentage")
    print("-" * (width + 30))
    print(f"  {'Name':<{width + 2}}{'Present':<12}Percentage")
    for display, present, total in sorted(stats.values(), key=lambda e: e[0].lower()):
        pct = percentage(present, total)
        flag = f"   <-- below {LOW_ATTENDANCE}%" if pct < LOW_ATTENDANCE else ""
        print(f"  {display:<{width + 2}}{f'{present} / {total}':<12}{pct:>6.2f}%{flag}")

    total_present = sum(1 for r in records if r["status"] == "Present")
    days = len({r["date"] for r in records})
    print("-" * (width + 30))
    print(f"  Overall: {total_present} / {len(records)} marks present "
          f"({percentage(total_present, len(records)):.2f}%) across {days} day(s)")


def main():
    records = load_records()
    print("=== Student Attendance Tracker ===")

    while True:
        print("\n1. Take attendance")
        print("2. Display attendance list")
        print("3. Show attendance percentage")
        print("4. Exit")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            records = take_attendance(records)
        elif choice == "2":
            display_attendance(records)
        elif choice == "3":
            show_percentage(records)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("  Invalid choice. Please enter a number from 1 to 4.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram ended. Saved records are in attendance.csv.")
