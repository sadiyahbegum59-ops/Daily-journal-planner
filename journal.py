#!/usr/bin/env python3
"""
Daily Journal Planner (simple CLI)

Features:
- Add daily journal entries (date, mood, goal, entry text).
- View all previous entries (persisted to journal.json).
- Shows a motivational exit message.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

JOURNAL_FILE = Path("journal.json")


@dataclass
class Entry:
    date: str        # ISO date string, e.g. 2025-11-18
    mood: str
    goal: str
    text: str
    created_at: str  # timestamp when entry was created


def load_entries() -> List[Entry]:
    if not JOURNAL_FILE.exists():
        return []
    try:
        data = json.loads(JOURNAL_FILE.read_text(encoding="utf-8"))
        return [Entry(**item) for item in data]
    except Exception as e:
        print(f"Warning: failed to read {JOURNAL_FILE} ({e}). Starting with empty journal.")
        return []


def save_entries(entries: List[Entry]) -> None:
    data = [asdict(e) for e in entries]
    JOURNAL_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def input_date(prompt: str = "Date (YYYY-MM-DD, leave empty for today): ") -> str:
    while True:
        s = input(prompt).strip()
        if s == "":
            return datetime.now().date().isoformat()
        try:
            # Validate date format
            dt = datetime.strptime(s, "%Y-%m-%d").date()
            return dt.isoformat()
        except ValueError:
            print("Invalid format. Please enter date as YYYY-MM-DD or leave empty for today.")


def input_multiline(prompt: str = "Entry text (type 'END' alone on a line to finish):\n") -> str:
    print(prompt, end="")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def add_entry(entries: List[Entry]) -> None:
    print("\n--- Add New Entry ---")
    date = input_date()
    mood = input("Mood (e.g. happy, anxious, excited — short): ").strip()
    if mood == "":
        mood = "unspecified"
    goal = input("Today's goal (short): ").strip()
    if goal == "":
        goal = "No specific goal"
    text = input_multiline()
    created_at = datetime.now().isoformat()
    entry = Entry(date=date, mood=mood, goal=goal, text=text, created_at=created_at)
    entries.append(entry)
    save_entries(entries)
    print("Saved ✅\n")


def display_entry(e: Entry, index: Optional[int] = None) -> None:
    header = f"Entry #{index} — {e.date}" if index is not None else f"{e.date}"
    print("-" * 40)
    print(header)
    print(f"Recorded at: {e.created_at}")
    print(f"Mood: {e.mood}")
    print(f"Goal: {e.goal}")
    print("")
    print(e.text if e.text else "(no text)")
    print("-" * 40)


def view_entries(entries: List[Entry]) -> None:
    print("\n--- All Journal Entries ---")
    if not entries:
        print("No entries yet. Try adding one!\n")
        return
    for i, e in enumerate(entries, start=1):
        display_entry(e, i)
    print(f"Total entries: {len(entries)}\n")


def search_by_date(entries: List[Entry]) -> None:
    date = input_date("Enter date to search (YYYY-MM-DD): ")
    found = [e for e in entries if e.date == date]
    if not found:
        print(f"No entries found for {date}.\n")
        return
    print(f"\n--- Entries on {date} ---")
    for i, e in enumerate(found, start=1):
        display_entry(e, i)
    print("")


def delete_entry(entries: List[Entry]) -> None:
    view_entries(entries)
    if not entries:
        return
    try:
        idx = int(input("Enter entry number to delete (0 to cancel): ").strip())
    except ValueError:
        print("Cancelled (invalid number).\n")
        return
    if idx == 0:
        print("Delete cancelled.\n")
        return
    if 1 <= idx <= len(entries):
        removed = entries.pop(idx - 1)
        save_entries(entries)
        print(f"Deleted entry from {removed.date}.\n")
    else:
        print("Invalid entry number.\n")


def menu_loop():
    entries = load_entries()
    MENU = """Choose an option:
1. Add new entry
2. View all entries
3. Search entries by date
4. Delete an entry
5. Quit
Enter choice (1-5): """
    try:
        while True:
            choice = input(MENU).strip()
            if choice == "1":
                add_entry(entries)
            elif choice == "2":
                view_entries(entries)
            elif choice == "3":
                search_by_date(entries)
            elif choice == "4":
                delete_entry(entries)
            elif choice == "5":
                # Motivational exit message
                print("\nThanks for journaling today ✨")
                print("Remember: small steps compound. Be proud of showing up.")
                break
            else:
                print("Please choose a number between 1 and 5.\n")
    except KeyboardInterrupt:
        print("\n\nInterrupted. Your entries are saved. Take care!")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        # ensure entries saved in case of any unsaved changes
        try:
            save_entries(entries)
        except Exception:
            pass


if __name__ == "__main__":
    menu_loop()
