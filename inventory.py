# inventory.py (Python 3 compatible)
import csv
import heapq
from datetime import datetime, timedelta

inventory = {}   # dictionary to store items
undo_stack = []  # stack to store undo actions
filename = "items.csv"  # CSV file to save inventory

# Function to extract number from string like "900 grams"
def extract_number(value):
    return int(''.join(filter(str.isdigit, value))) if value else 0

# Load existing items from CSV (if any)
try:
    with open(filename, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            inventory[row['name']] = {
                'quantity': int(row['quantity']),
                'category': row['category'],
                'expiry': row['expiry'],
                'popularity': int(row['popularity'])
            }
except FileNotFoundError:
    pass  # file will be created when first item is added

# Function to save inventory to CSV
def save_inventory():
    with open(filename, mode='w', newline='') as file:
        fieldnames = ['name', 'quantity', 'category', 'expiry', 'popularity']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for name, info in inventory.items():
            writer.writerow({
                'name': name,
                'quantity': info['quantity'],
                'category': info['category'],
                'expiry': info['expiry'],
                'popularity': info['popularity']
            })

# Function to display menu
def show_menu():
    print("\nDynamic Stock Manager")
    print("1. Add Item")
    print("2. Remove Item")
    print("3. Check Stock")
    print("4. Restock Suggestion")
    print("5. Expiry Alert")
    print("6. High-Demand Items")
    print("7. Category Summary")
    print("8. Undo Last Action")
    print("9. Exit")

# Main loop
while True:
    show_menu()
    choice = input("Enter your choice: ")

    # 1. Add Item
    if choice == "1":
        name = input("Enter item name: ")
        quantity_input = input("Enter quantity (e.g., 900 grams or 5): ")
        quantity = extract_number(quantity_input)
        category = input("Enter category: ")
        expiry = input("Enter expiry date (YYYY-MM-DD): ")
        popularity_input = input("Enter popularity score: ")
        popularity = extract_number(popularity_input)

        inventory[name] = {
            'quantity': quantity,
            'category': category,
            'expiry': expiry,
            'popularity': popularity
        }
        undo_stack.append(('add', name))
        save_inventory()
        print(f"Item '{name}' added successfully!")

    # 2. Remove Item
    elif choice == "2":
        name = input("Enter item name to remove: ")
        if name in inventory:
            undo_stack.append(('remove', name, inventory[name]))
            del inventory[name]
            save_inventory()
            print(f"Item '{name}' removed successfully!")
        else:
            print(f"Item '{name}' not found in inventory.")

    # 3. Check Stock
    elif choice == "3":
        if inventory:
            print("\nCurrent Inventory:")
            for name, info in inventory.items():
                print(f"{name} | Qty: {info['quantity']} | Category: {info['category']} | Expiry: {info['expiry']} | Popularity: {info['popularity']}")
        else:
            print("Inventory is empty.")

    # 4. Restock Suggestion
    elif choice == "4":
        min_quantity_input = input("Enter minimum quantity threshold: ")
        min_quantity = extract_number(min_quantity_input)
        restock_items = [(info['quantity'], name) for name, info in inventory.items() if info['quantity'] < min_quantity]
        if restock_items:
            heapq.heapify(restock_items)
            print("Items suggested for restock:")
            while restock_items:
                qty, name = heapq.heappop(restock_items)
                print(f"{name} | Qty: {qty}")
        else:
            print("No items need restocking.")

    # 5. Expiry Alert
    elif choice == "5":
        days_threshold = int(input("Enter number of days to check for expiry: "))
        today = datetime.today()
        expiring_items = []
        for name, info in inventory.items():
            try:
                expiry_date = datetime.strptime(info['expiry'], "%Y-%m-%d")
                days_left = (expiry_date - today).days
                if days_left <= days_threshold:
                    heapq.heappush(expiring_items, (days_left, name))
            except ValueError:
                continue
        if expiring_items:
            print(f"Items expiring in next {days_threshold} days:")
            while expiring_items:
                days_left, name = heapq.heappop(expiring_items)
                print(f"{name} | Days left: {days_left}")
        else:
            print("No items nearing expiry.")

    # 6. High-Demand Items
    elif choice == "6":
        top_n_input = input("Enter number of top items to show: ")
        top_n = extract_number(top_n_input)
        if inventory:
            demand_items = [(-info['popularity'], name) for name, info in inventory.items()]
            heapq.heapify(demand_items)
            print(f"Top {top_n} high-demand items:")
            for _ in range(min(top_n, len(demand_items))):
                pop, name = heapq.heappop(demand_items)
                print(f"{name} | Popularity: {-pop}")
        else:
            print("Inventory is empty.")

    # 7. Category Summary
    elif choice == "7":
        category_count = {}
        for info in inventory.values():
            category = info['category']
            category_count[category] = category_count.get(category, 0) + 1
        print("Category Summary:")
        for category, count in category_count.items():
            print(f"{category} : {count}")

    # 8. Undo Last Action
    elif choice == "8":
        if undo_stack:
            last_action = undo_stack.pop()
            action_type = last_action[0]
            if action_type == "add":
                name = last_action[1]
                if name in inventory:
                    del inventory[name]
                    print(f"Undo: Added item '{name}' removed.")
            elif action_type == "remove":
                name, info = last_action[1], last_action[2]
                inventory[name] = info
                print(f"Undo: Removed item '{name}' restored.")
            save_inventory()
        else:
            print("No actions to undo.")

    # 9. Exit
    elif choice == "9":
        print("Exiting...")
        break

    else:
        print("Invalid option! Please try again.")
