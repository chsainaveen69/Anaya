import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import os

# --- Product List ---
PRODUCTS = [
    {"Product Name": "water bottle basic (1000ml)", "Pack Size": "1000ml", "MRP": 20},
    {"Product Name": "water bottle basic (500ml)", "Pack Size": "500ml", "MRP": 10},
    {"Product Name": "fizzy lemon (160ml)", "Pack Size": "160ml", "MRP": 12},
    {"Product Name": "thunder cola (160ml)", "Pack Size": "160ml", "MRP": 12},
    {"Product Name": "nimbu fizz (160ml)", "Pack Size": "160ml", "MRP": 12},
    {"Product Name": "tangy orange (160ml)", "Pack Size": "160ml", "MRP": 12},
    {"Product Name": "mango mazza (160ml)", "Pack Size": "160ml", "MRP": 12},
    {"Product Name": "fresh jeera (160ml)", "Pack Size": "160ml", "MRP": 12},
    {"Product Name": "clear lemon (160ml)", "Pack Size": "160ml", "MRP": 12},
    {"Product Name": "strong soda (160ml)", "Pack Size": "160ml", "MRP": 12},
    {"Product Name": "strong soda (300ml)", "Pack Size": "300ml", "MRP": 20},
    {"Product Name": "water bottle basic (300ml)", "Pack Size": "300ml", "MRP": 0},
    {"Product Name": "water bottle premium (1000ml)", "Pack Size": "1000ml", "MRP": 0},
    {"Product Name": "water bottle premium (500ml)", "Pack Size": "500ml", "MRP": 0},
    {"Product Name": "water bottle premium (300ml)", "Pack Size": "300ml", "MRP": 0},
]

CUSTOMER_FILE = "customers.xlsx"

# --- Helper Functions ---
def ensure_customer_file():
    if not os.path.exists(CUSTOMER_FILE):
        df = pd.DataFrame(columns=["Outlet Name", "Contact Number", "Area", "City/Town", "Pincode", "State"])
        df.to_excel(CUSTOMER_FILE, index=False)

def load_customers():
    ensure_customer_file()
    df = pd.read_excel(CUSTOMER_FILE)
    return df.to_dict('records')

def save_customers(customers):
    df = pd.DataFrame(customers)
    df.to_excel(CUSTOMER_FILE, index=False)

def get_order_file():
    now = datetime.now()
    folder = "/storage/emulated/0/ayana"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return f"{folder}/orders_{now.year}_{now.month:02d}.xlsx"

def append_order(rows):
    order_file = get_order_file()
    if os.path.exists(order_file):
        df = pd.read_excel(order_file)
    else:
        df = pd.DataFrame()
    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    df.to_excel(order_file, index=False)

# --- Page 1: Customer Selection / Add Outlet ---
class AyanaApp:
    def _init_(self, master):
        self.master = master
        master.title("AYANA - Premium Water with Added Minerals")
        self.customers = load_customers()
        self.selected_customer = None

        # Heading and caption
        tk.Label(master, text="Welcome to AYANA", font=("Arial", 22, "bold"), fg="#1e90ff").pack(pady=10)
        tk.Label(master, text="Premium water with added minerals.", font=("Arial", 13, "italic"), fg="#008080").pack(pady=5)

        # Customer selection
        frame = tk.Frame(master)
        frame.pack(pady=10)
        tk.Label(frame, text="Select Outlet:", font=("Arial", 11)).grid(row=0, column=0, sticky="e")
        self.customer_combo = ttk.Combobox(frame, width=35, values=[c['Outlet Name'] for c in self.customers], state="readonly")
        self.customer_combo.grid(row=0, column=1, padx=5)

        tk.Button(frame, text="Add New Outlet", command=self.add_outlet_popup, bg="#cceeff").grid(row=0, column=2, padx=5)

        # Take order button
        tk.Button(master, text="Take Order", command=self.goto_page2, font=("Arial", 12, "bold"), bg="#90ee90").pack(pady=20)

    def add_outlet_popup(self):
        popup = tk.Toplevel(self.master)
        popup.title("Add New Outlet")
        labels = ["Outlet Name", "Contact Number", "Area", "City/Town", "Pincode", "State"]
        entries = {}
        for i, label in enumerate(labels):
            tk.Label(popup, text=label).grid(row=i, column=0, sticky="e", padx=3, pady=2)
            entry = tk.Entry(popup, width=30)
            entry.grid(row=i, column=1, padx=3, pady=2)
            entries[label] = entry

        def save_outlet():
            data = {label: entries[label].get().strip() for label in labels}
            if not all(data.values()):
                messagebox.showwarning("Missing Info", "Please fill all fields.")
                return
            self.customers.append(data)
            save_customers(self.customers)
            self.customer_combo['values'] = [c['Outlet Name'] for c in self.customers]
            popup.destroy()
            messagebox.showinfo("Outlet Added", "New outlet added successfully!")

        tk.Button(popup, text="Save", command=save_outlet, bg="#b0e0e6").grid(row=len(labels), column=0, columnspan=2, pady=8)

    def goto_page2(self):
        selected = self.customer_combo.get()
        if not selected:
            messagebox.showwarning("Select Outlet", "Please select or add an outlet.")
            return
        for c in self.customers:
            if c['Outlet Name'] == selected:
                self.selected_customer = c
                break
        self.master.destroy()
        page2(self.selected_customer)

# --- Page 2: Order Entry ---
def page2(customer):
    root = tk.Tk()
    root.title("AYANA - Take Order")
    order_items = []

    tk.Label(root, text=f"Order for: {customer['Outlet Name']}", font=("Arial", 15, "bold"), fg="#1e90ff").pack(pady=7)
    frame = tk.Frame(root)
    frame.pack()

    # Table headings
    headings = ["Select", "Product", "MRP", "Discount", "Quantity"]
    for col, heading in enumerate(headings):
        tk.Label(frame, text=heading, font=("Arial", 10, "bold")).grid(row=0, column=col, padx=4, pady=2)

    # Product selection rows
    product_vars = []
    qty_vars = []
    disc_vars = []
    check_vars = []

    # --- Bill Calculation ---
    def calculate_bill(event=None):
        total = 0
        order_items.clear()
        for i, var in enumerate(check_vars):
            if var.get():
                try:
                    qty = int(qty_vars[i].get())
                    disc = float(disc_vars[i].get())
                    if qty <= 0 or disc < 0:
                        continue
                except:
                    continue  # Ignore invalid input for now
                mrp = PRODUCTS[i]['MRP']
                amount = max((mrp - disc), 0) * qty
                total += amount
                order_items.append({
                    "Product": PRODUCTS[i]['Product Name'],
                    "MRP": mrp,
                    "Discount": disc,
                    "Quantity": qty,
                    "Amount": amount
                })
        bill_label.config(text=f"Total: Rs {total:.2f}")

    for i, prod in enumerate(PRODUCTS):
        var = tk.IntVar()
        chk = tk.Checkbutton(frame, variable=var)
        chk.grid(row=i+1, column=0)
        # Bind checkbox click to recalculate
        chk.bind("<ButtonRelease-1>", lambda e: root.after(10, calculate_bill))

        tk.Label(frame, text=prod["Product Name"]).grid(row=i+1, column=1, sticky="w")
        tk.Label(frame, text=str(prod["MRP"])).grid(row=i+1, column=2)
        
        disc = tk.Entry(frame, width=7)
        disc.insert(0, "0")
        disc.grid(row=i+1, column=3)
        # Bind discount entry changes
        disc.bind("<KeyRelease>", calculate_bill)
        
        qty = tk.Entry(frame, width=7)
        qty.insert(0, "0")
        qty.grid(row=i+1, column=4)
        # Bind quantity entry changes
        qty.bind("<KeyRelease>", calculate_bill)

        check_vars.append(var)
        disc_vars.append(disc)
        qty_vars.append(qty)

    bill_label = tk.Label(root, text="Total: Rs 0", font=("Arial", 13, "bold"), fg="#008000")
    bill_label.pack(pady=10)

    # --- Save Order ---
    def save_order():
        if not order_items:
            messagebox.showwarning("No Products", "Select at least one product and enter quantity.")
            return
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = []
        for item in order_items:
            row = {
                "DateTime": now,
                "Outlet Name": customer["Outlet Name"],
                "Contact Number": customer["Contact Number"],
                "Area": customer["Area"],
                "City/Town": customer["City/Town"],
                "State": customer["State"],
                "Pincode": customer["Pincode"],
                "Product": item["Product"],
                "Quantity": item["Quantity"],
                "Amount": item["Amount"]
            }
            rows.append(row)
        append_order(rows)
        # Show the file path to the user
        messagebox.showinfo("Order Saved", f"Order has been saved to:\n{get_order_file()}\n\nOpen your file manager and go to Internal storage > ayana.")
        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=8)
    tk.Button(btn_frame, text="Save Order", command=save_order, bg="#90ee90").grid(row=0, column=1, padx=10)
    root.mainloop()

# --- Main ---
if _name_ == "_main_":
    ensure_customer_file()
    root = tk.Tk()
    app = AyanaApp(root)
    root.mainloop()