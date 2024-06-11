import sqlite3
from colorama import init, Fore, Style
import os
import pyfiglet

# تهيئة colorama
init(autoreset=True)

# إنشاء أو فتح قاعدة البيانات
conn = sqlite3.connect('inventory.db')
c = conn.cursor()

# إنشاء الجدول إذا لم يكن موجودًا
c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_name TEXT,
        item_name TEXT,
        item_price REAL,
        paid BOOLEAN
    )
''')

# إنشاء جدول للعناصر الثابتة إذا لم يكن موجودًا
c.execute('''
    CREATE TABLE IF NOT EXISTS fixed_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT,
        item_price REAL,
        printing_cost REAL,
        profit REAL
    )
''')

conn.commit()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def add_order(teacher_name, item_id, paid):
    c.execute('SELECT item_name, item_price FROM fixed_items WHERE id = ?', (item_id,))
    item = c.fetchone()
    if item is None:
        print(Fore.RED + "Invalid item ID!")
        return
    item_name, item_price = item
    c.execute('INSERT INTO orders (teacher_name, item_name, item_price, paid) VALUES (?, ?, ?, ?)', (teacher_name, item_name, item_price, paid))
    conn.commit()
    print(Fore.GREEN + "Order added successfully!")
    input(Fore.GREEN + "Press Enter to continue...")  # Pause before clearing screen
    clear_screen()

def select_items_for_group_order():
    selected_items = []
    while True:
        print(Fore.YELLOW + "Select item by ID (enter 0 to finish selection):")
        c.execute('SELECT id, item_name, item_price FROM fixed_items')
        items = c.fetchall()
        for item_id, item_name, item_price in items:
            print(Fore.YELLOW + f"  {item_id}: {item_name} - {item_price}")
        item_id = int(input(Fore.YELLOW + "Enter item ID: "))
        if item_id == 0:
            break
        c.execute('SELECT item_name FROM fixed_items WHERE id = ?', (item_id,))
        if c.fetchone() is None:
            print(Fore.RED + "Invalid item ID!")
        else:
            selected_items.append(item_id)
    return selected_items

def add_group_order(teacher_name, orders, paid):
    for item_id, quantity in orders.items():
        c.execute('SELECT item_name, item_price FROM fixed_items WHERE id = ?', (item_id,))
        item = c.fetchone()
        if item is None:
            print(Fore.RED + f"Invalid item ID: {item_id}")
            continue
        item_name, item_price = item
        for _ in range(quantity):
            c.execute('INSERT INTO orders (teacher_name, item_name, item_price, paid) VALUES (?, ?, ?, ?)', (teacher_name, item_name, item_price, paid))
    conn.commit()
    print(Fore.GREEN + "Group orders added successfully!")
    input(Fore.GREEN + "Press Enter to continue...")  # Pause before clearing screen
    clear_screen()

def update_payment_status(order_id):
    c.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = c.fetchone()
    if order:
        paid_status = input(Fore.YELLOW + "Is the order paid? (yes/no): ").strip().lower() == 'yes'
        c.execute('UPDATE orders SET paid = ? WHERE id = ?', (paid_status, order_id))
        conn.commit()
        print(Fore.GREEN + "Payment status updated successfully!")
    else:
        print(Fore.RED + "Order ID not found.")
    input(Fore.GREEN + "Press Enter to continue...")  # Pause before clearing screen
    clear_screen()

def calculate_total_for_teacher(teacher_name):
    c.execute('SELECT SUM(item_price) FROM orders WHERE teacher_name = ?', (teacher_name,))
    total = c.fetchone()[0]
    return total if total else 0

def calculate_printing_cost():
    total_cost = 0
    c.execute('SELECT item_name, printing_cost FROM fixed_items')
    items = c.fetchall()
    for item_name, cost in items:
        c.execute('SELECT COUNT(*) FROM orders WHERE item_name = ?', (item_name,))
        count = c.fetchone()[0]
        total_cost += count * cost
    return total_cost

def calculate_profits():
    total_profit = 0
    c.execute('SELECT item_name, profit FROM fixed_items')
    items = c.fetchall()
    for item_name, profit in items:
        c.execute('SELECT COUNT(*) FROM orders WHERE item_name = ? AND paid = 1', (item_name,))
        count = c.fetchone()[0]
        total_profit += count * profit
    return total_profit

def display_orders():
    c.execute('SELECT * FROM orders')
    orders = c.fetchall()
    for order in orders:
        paid_status = "Paid" if order[4] else "Unpaid"
        print(Fore.CYAN + f"Order ID: {order[0]}, Teacher: {order[1]}, Item: {order[2]}, Price: {order[3]}, Status: {paid_status}")
    print(Fore.CYAN + f"\nTotal Printing Cost: {calculate_printing_cost()}\n")
    input(Fore.CYAN + "Press Enter to continue...")  # Pause before clearing screen
    clear_screen()

def delete_all_data():
    c.execute('DELETE FROM orders')
    conn.commit()
    print(Fore.MAGENTA + "All data deleted successfully!")
    input(Fore.MAGENTA + "Press Enter to continue...")  # Pause before clearing screen
    clear_screen()

def add_new_item():
    item_name = input(Fore.YELLOW + "Enter item name: ")
    item_price = float(input(Fore.YELLOW + "Enter item price: "))
    printing_cost = float(input(Fore.YELLOW + "Enter printing cost: "))
    profit = float(input(Fore.YELLOW + "Enter profit: "))
    c.execute('INSERT INTO fixed_items (item_name, item_price, printing_cost, profit) VALUES (?, ?, ?, ?)', (item_name, item_price, printing_cost, profit))
    conn.commit()
    print(Fore.GREEN + "New item added successfully!")
    input(Fore.GREEN + "Press Enter to continue...")  # Pause before clearing screen
    clear_screen()

def display_logo():
    logo = pyfiglet.figlet_format("EMISHUB")
    print(Fore.GREEN + logo)

def main():
    clear_screen()
    display_logo()
    while True:
        print(Fore.YELLOW + "1. Add Order")
        print(Fore.YELLOW + "2. Add Group Order")
        print(Fore.YELLOW + "3. Display All Orders")
        print(Fore.YELLOW + "4. Update Payment Status")
        print(Fore.YELLOW + "5. Calculate Printing Cost")
        print(Fore.YELLOW + "6. Calculate Profits")
        print(Fore.YELLOW + "7. Delete All Data")
        print(Fore.YELLOW + "8. Add New Item")
        print(Fore.YELLOW + "9. Exit")
        choice = input(Fore.YELLOW + "Enter your choice: ")
        if choice == '1':
            clear_screen()
            teacher_name = input(Fore.YELLOW + "Enter teacher's name: ")
            print(Fore.YELLOW + "Select item by ID:")
            c.execute('SELECT id, item_name, item_price FROM fixed_items')
            items = c.fetchall()
            for item_id, item_name, item_price in items:
                print(Fore.YELLOW + f"  {item_id}: {item_name} - {item_price}")
            item_id = int(input(Fore.YELLOW + "Enter item ID: "))
            paid = input(Fore.YELLOW + "Is the order paid? (yes/no): ").strip().lower() == 'yes'
            add_order(teacher_name, item_id, paid)

        elif choice == '2':
            clear_screen()
            teacher_name = input(Fore.YELLOW + "Enter teacher's name or group: ")
            selected_items = select_items_for_group_order()
            if not selected_items:
                print(Fore.RED + "No items selected.")
                input(Fore.RED + "Press Enter to continue...")  # Pause before clearing screen
                clear_screen()
                continue
            orders = {}
            for item_id in selected_items:
                c.execute('SELECT item_name FROM fixed_items WHERE id = ?', (item_id,))
                item_name = c.fetchone()[0]
                quantity = int(input(Fore.YELLOW + f"Enter quantity for {item_name}: "))
                orders[item_id] = quantity
            paid = input(Fore.YELLOW + "Are all orders paid? (yes/no): ").strip().lower() == 'yes'
            add_group_order(teacher_name, orders, paid)

        elif choice == '3':
            clear_screen()
            display_orders()

        elif choice == '4':
            clear_screen()
            order_id = int(input(Fore.YELLOW + "Enter order ID to update payment status: "))
            update_payment_status(order_id)

        elif choice == '5':
            clear_screen()
            print(Fore.CYAN + f"Total Printing Cost: {calculate_printing_cost()}")
            input(Fore.CYAN + "Press Enter to continue...")  # Pause before clearing screen
            clear_screen()

        elif choice == '6':
            clear_screen()
            print(Fore.GREEN + f"Total Profits: {calculate_profits()}")
            input(Fore.GREEN + "Press Enter to continue...")  # Pause before clearing screen
            clear_screen()

        elif choice == '7':
            clear_screen()
            delete_all_data()

        elif choice == '8':
            clear_screen()
            add_new_item()

        elif choice == '9':
            break

        else:
            print(Fore.RED + "Invalid choice, please try again.")
            input(Fore.RED + "Press Enter to continue...")  # Pause before clearing screen
            clear_screen()

if __name__ == "__main__":
    main()

# إغلاق الاتصال بقاعدة البيانات
conn.close()
