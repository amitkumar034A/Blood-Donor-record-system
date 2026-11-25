"""
Blood Donor Record Management System
-------------------------------------
A menu-driven Python program that stores blood donor records in a JSON
file and helps staff quickly find potential donors in an emergency.

"""

import json
import re
from datetime import date, datetime

# ---------------------------------------------------------------
# Global constants
# ---------------------------------------------------------------
DATA_FILE = "donors.json"          # permanent storage file
STAFF_PIN = "1234"                 # simple access control (change it!)
VALID_BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
VALID_GENDERS = ["Male", "Female", "Other"]


# ---------------------------------------------------------------
# 1. FILE HANDLING FUNCTIONS (JSON storage)
# ---------------------------------------------------------------
def load_donors():
    """Read all donor records from the JSON file.
    Returns an empty list if the file is missing or damaged."""
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []                              # first run: no file yet
    except json.JSONDecodeError:
        print("Warning: data file is damaged. Starting with an empty list.")
        return []


def save_donors(donors):
    """Write the full donor list to the JSON file."""
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(donors, file, indent=4)
    except OSError as error:
        print("Error: could not save data ->", error)


# ---------------------------------------------------------------
# 2. INPUT VALIDATION FUNCTIONS
#    Each one loops until the user gives a valid value.
# ---------------------------------------------------------------
def get_text(prompt):
    """Ask for a non-empty text value."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def get_age():
    """Ask for age; must be a whole number between 18 and 65."""
    while True:
        try:
            age = int(input("Age (18-65): "))
            if 18 <= age <= 65:
                return age
            print("Age must be between 18 and 65.")
        except ValueError:                      # user typed letters
            print("Please enter a number.")


def get_gender():
    """Ask for gender from a fixed list."""
    while True:
        value = input("Gender (Male/Female/Other): ").strip().capitalize()
        if value in VALID_GENDERS:
            return value
        print("Enter Male, Female or Other.")


def get_blood_group(prompt="Blood Group (A+, A-, B+, B-, AB+, AB-, O+, O-): "):
    """Ask for a valid blood group and return it in upper case."""
    while True:
        value = input(prompt).strip().upper()
        if value in VALID_BLOOD_GROUPS:
            return value
        print("Invalid blood group.")


def get_phone(prompt="Contact Number (10 digits): "):
    """Ask for a 10-digit Indian mobile number starting with 6-9."""
    while True:
        value = input(prompt).strip()
        if re.fullmatch(r"[6-9]\d{9}", value):
            return value
        print("Enter a valid 10-digit mobile number.")


def get_email(prompt="Email Address: "):
    """Ask for an email in a basic valid format."""
    while True:
        value = input(prompt).strip().lower()
        if re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.]+", value):
            return value
        print("Enter a valid email like name@example.com.")


def get_last_donation_date():
    """Ask for last donation date (YYYY-MM-DD). Blank = never donated."""
    while True:
        value = input("Last Donation Date (YYYY-MM-DD, blank if never): ").strip()
        if value == "":
            return "Never"
        try:
            donated_on = datetime.strptime(value, "%Y-%m-%d").date()
            if donated_on > date.today():
                print("Date cannot be in the future.")
            else:
                return value
        except ValueError:
            print("Use the format YYYY-MM-DD.")


def get_availability():
    """Ask whether the donor says they are available (self-reported)."""
    while True:
        value = input("Available to donate? (yes/no) [self-reported]: ").strip().lower()
        if value in ("yes", "y"):
            return "Available"
        if value in ("no", "n"):
            return "Not Available"
        print("Please type yes or no.")


# ---------------------------------------------------------------
# 3. HELPER FUNCTIONS
# ---------------------------------------------------------------
def mask_phone(phone):
    """Hide middle digits of a phone number, e.g. 98XXXXXX10."""
    return phone[:2] + "X" * 6 + phone[-2:]


def find_by_id(donors, donor_id):
    """Return the donor dictionary with this ID, or None."""
    for donor in donors:
        if donor["donor_id"] == donor_id:
            return donor
    return None


def print_table(records, show_full_contact=False):
    """Print donor records as a neat table.
    Contact numbers are masked unless show_full_contact is True."""
    if not records:
        print("No records found.")
        return
    header = (f"{'ID':<7}{'Name':<20}{'Age':<5}{'Gender':<8}{'BG':<5}"
              f"{'Contact':<13}{'City':<12}{'Last Donation':<15}{'Status':<14}")
    print("\n" + header)
    print("-" * len(header))
    for d in records:
        phone = d["contact"] if show_full_contact else mask_phone(d["contact"])
        print(f"{d['donor_id']:<7}{d['name']:<20}{d['age']:<5}{d['gender']:<8}"
              f"{d['blood_group']:<5}{phone:<13}{d['city']:<12}"
              f"{d['last_donation']:<15}{d['availability']:<14}")
    print(f"\nTotal records shown: {len(records)}")


# ---------------------------------------------------------------
# 4. MAIN FEATURE FUNCTIONS
# ---------------------------------------------------------------
def add_donor(donors):
    """Register a new donor. Rejects duplicate IDs and phone numbers."""
    print("\n--- Add New Donor ---")
    donor_id = get_text("Donor ID (e.g. D001): ").upper()
    if find_by_id(donors, donor_id):
        print("Error: Donor ID already exists.")
        return

    name = get_text("Full Name: ").title()
    age = get_age()
    gender = get_gender()
    blood_group = get_blood_group()
    contact = get_phone()
    if any(d["contact"] == contact for d in donors):
        print("Error: a donor with this contact number already exists.")
        return
    email = get_email()
    city = get_text("City: ").title()
    last_donation = get_last_donation_date()
    availability = get_availability()

    donors.append({
        "donor_id": donor_id, "name": name, "age": age, "gender": gender,
        "blood_group": blood_group, "contact": contact, "email": email,
        "city": city, "last_donation": last_donation,
        "availability": availability,
    })
    save_donors(donors)
    print("Donor added successfully.")


def view_all(donors):
    """Display every donor in a table."""
    print("\n--- All Donors ---")
    print_table(donors)


def search_by_id(donors):
    """Exact search on Donor ID."""
    donor_id = get_text("Enter Donor ID: ").upper()
    print_table([d for d in donors if d["donor_id"] == donor_id])


def search_by_name(donors):
    """Partial, case-insensitive search on name."""
    text = get_text("Enter name (or part of it): ").lower()
    print_table([d for d in donors if text in d["name"].lower()])


def search_by_blood_group(donors):
    """Search by blood group."""
    group = get_blood_group()
    print_table([d for d in donors if d["blood_group"] == group])


def search_by_city(donors):
    """Case-insensitive search by city."""
    city = get_text("Enter city: ").lower()
    print_table([d for d in donors if d["city"].lower() == city])


def update_donor(donors):
    """Update contact, email, city, availability or last donation date."""
    print("\n--- Update Donor ---")
    donor = find_by_id(donors, get_text("Enter Donor ID: ").upper())
    if donor is None:
        print("Donor not found.")
        return

    print("1. Contact Number\n2. Email\n3. City\n4. Availability\n5. Last Donation Date")
    choice = input("What do you want to update? (1-5): ").strip()
    if choice == "1":
        new_phone = get_phone("New contact number: ")
        if any(d["contact"] == new_phone for d in donors):
            print("Error: this number belongs to another donor.")
            return
        donor["contact"] = new_phone
    elif choice == "2":
        donor["email"] = get_email("New email: ")
    elif choice == "3":
        donor["city"] = get_text("New city: ").title()
    elif choice == "4":
        donor["availability"] = get_availability()
    elif choice == "5":
        donor["last_donation"] = get_last_donation_date()
    else:
        print("Invalid choice.")
        return
    save_donors(donors)
    print("Record updated successfully.")


def delete_donor(donors):
    """Delete a donor by ID after confirmation."""
    print("\n--- Delete Donor ---")
    donor = find_by_id(donors, get_text("Enter Donor ID: ").upper())
    if donor is None:
        print("Donor not found.")
        return
    confirm = input(f"Delete {donor['name']} ({donor['donor_id']})? (y/n): ").lower()
    if confirm == "y":
        donors.remove(donor)
        save_donors(donors)
        print("Record deleted.")
    else:
        print("Deletion cancelled.")


def blood_group_statistics(donors):
    """Count donors in each blood group using a dictionary."""
    print("\n--- Blood Group Statistics ---")
    counts = {group: 0 for group in VALID_BLOOD_GROUPS}
    for donor in donors:
        counts[donor["blood_group"]] += 1
    for group, count in counts.items():
        print(f"{group:<4}: {count}")
    print(f"Total donors: {len(donors)}")


def find_potential_donors(donors):
    """List self-reported available donors with the requested blood group
    in the given city. Full contact numbers are shown for staff use."""
    print("\n--- Find Potential Donors ---")
    group = get_blood_group("Required Blood Group: ")
    city = get_text("City: ").lower()
    matches = [d for d in donors
               if d["blood_group"] == group
               and d["city"].lower() == city
               and d["availability"] == "Available"]
    print_table(matches, show_full_contact=True)
    if matches:
        print("NOTE: Availability is self-reported. Medical eligibility and "
              "blood compatibility must be confirmed by blood bank staff.")


# ---------------------------------------------------------------
# 5. LOGIN AND MAIN MENU
# ---------------------------------------------------------------
def login():
    """Allow 3 attempts to enter the staff PIN."""
    for attempt in range(3):
        if input("Enter staff PIN: ").strip() == STAFF_PIN:
            return True
        print(f"Wrong PIN. Attempts left: {2 - attempt}")
    return False


def show_menu():
    print("\n===== BLOOD DONOR RECORD MANAGEMENT SYSTEM =====")
    print("1. Add New Donor")
    print("2. View All Donors")
    print("3. Search Donor by ID")
    print("4. Search Donor by Name")
    print("5. Search Donor by Blood Group")
    print("6. Search Donor by City")
    print("7. Update Donor Details")
    print("8. Delete Donor Record")
    print("9. Blood Group Statistics")
    print("10. Find Potential Donors")
    print("11. Exit")


def main():
    """Program entry point: login, then loop over the menu."""
    if not login():
        print("Access denied.")
        return
    donors = load_donors()

    actions = {
        "1": add_donor, "2": view_all, "3": search_by_id,
        "4": search_by_name, "5": search_by_blood_group,
        "6": search_by_city, "7": update_donor, "8": delete_donor,
        "9": blood_group_statistics, "10": find_potential_donors,
    }

    while True:
        show_menu()
        choice = input("Enter your choice (1-11): ").strip()
        if choice == "11":
            print("Data saved. Thank you. Goodbye!")
            break
        elif choice in actions:
            try:
                actions[choice](donors)
            except Exception as error:          # safety net
                print("Unexpected error:", error)
        else:
            print("Invalid choice. Enter a number from 1 to 11.")


if __name__ == "__main__":
    main()