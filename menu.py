import os
import sys
import subprocess
from pathlib import Path

from art import LOGO

BUILDS = {
    "1": Path(__file__).parent / "original" / "main2.py",
    "2": Path(__file__).parent / "advanced" / "main.py",
}

clear = True
while True:
    if clear:
        os.system("cls" if os.name == "nt" else "clear")
    clear = True
    print(LOGO)
    print("Select a build:")
    print("  1 — Original  (course exercise, verbatim)")
    print("  2 — Advanced  (OOP refactor, interactive CLI)")
    print("  q — Quit")
    choice = input("\n> ").strip().lower()

    if choice in BUILDS:
        path = BUILDS[choice]
        subprocess.run([sys.executable, str(path)], cwd=str(path.parent))
        input("\nPress Enter to return to menu...")
    elif choice == "q":
        break
    else:
        print("Invalid choice. Try again.")
        clear = False
