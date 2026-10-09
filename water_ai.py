import tkinter as tk
from tkinter import ttk
import random, datetime
import matplotlib.pyplot as plt
import mysql.connector

# Safe limits
SAFE_TURBIDITY = 50
SAFE_PH_LOW, SAFE_PH_HIGH = 6.5, 8.5

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="MySQLlekha@3456",   # replace with your MySQL password
    database="water_ai"
)
cursor = db.cursor()

# Tkinter setup
root = tk.Tk()
root.title("AI Guardian - Water Safety Dashboard")

status_label = tk.Label(root, text="Status: Waiting...", font=("Arial", 16))
status_label.pack(pady=10)

log_box = tk.Listbox(root, width=60, height=10)
log_box.pack(pady=10)

# Transparency table (Treeview)
tree = ttk.Treeview(root, columns=("Time", "Turbidity", "pH", "Status"), show="headings")
for col in ("Time", "Turbidity", "pH", "Status"):
    tree.heading(col, text=col)
tree.pack(pady=10)

data_log = []

def read_sensor_data():
    turbidity = random.randint(10, 200)
    ph = round(random.uniform(6.0, 9.0), 2)
    return turbidity, ph

def send_sms_alert(message):
    # Simulation of SMS alert
    print(f"Sending SMS: {message}")
    # For real SMS, integrate Twilio/Fast2SMS API here

def detect_and_store():
    turbidity, ph = read_sensor_data()
    status = "UNSAFE → DIVERT SEWAGE" if turbidity > SAFE_TURBIDITY or ph < SAFE_PH_LOW or ph > SAFE_PH_HIGH else "SAFE → NORMAL FLOW"

    # Update GUI
    status_label.config(text=f"Status: {status}", fg="red" if "UNSAFE" in status else "green")
    log_box.insert(tk.END, f"{datetime.datetime.now().strftime('%H:%M:%S')} | Turbidity={turbidity}, pH={ph}, {status}")

    # Store in MySQL
    cursor.execute("INSERT INTO sensor_data (timestamp, turbidity, ph, status) VALUES (%s,%s,%s,%s)",
                   (datetime.datetime.now(), turbidity, ph, status))
    db.commit()

    cursor.execute("INSERT INTO actions (timestamp, command) VALUES (%s,%s)",
                   (datetime.datetime.now(), status))
    db.commit()

    # Transparency table update
    tree.insert("", tk.END, values=(datetime.datetime.now().strftime("%H:%M:%S"), turbidity, ph, status))

    # SMS alert if unsafe
    if "UNSAFE" in status:
        send_sms_alert(f"Unsafe water detected at {datetime.datetime.now().strftime('%H:%M:%S')}")

    data_log.append((datetime.datetime.now(), turbidity, ph, status))
    root.after(2000, detect_and_store)

def plot_graph():
    cursor.execute("SELECT timestamp, turbidity, ph FROM sensor_data ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    times = [row[0].strftime("%H:%M:%S") for row in rows]
    turbidity = [row[1] for row in rows]
    ph = [row[2] for row in rows]

    plt.figure(figsize=(10,5))
    plt.plot(times, turbidity, 'r-o', label="Turbidity")
    plt.axhline(y=SAFE_TURBIDITY, color='g', linestyle='--', label="Safe Limit")
    plt.plot(times, ph, 'b-s', label="pH")
    plt.axhline(y=SAFE_PH_LOW, color='y', linestyle='--', label="pH Safe Range")
    plt.axhline(y=SAFE_PH_HIGH, color='y', linestyle='--')
    plt.legend()
    plt.title("Water Quality Trends")
    plt.savefig("dashboard_chart.png")
    plt.show()

plot_button = tk.Button(root, text="Generate Graph", command=plot_graph)
plot_button.pack(pady=10)

detect_and_store()
root.mainloop()
