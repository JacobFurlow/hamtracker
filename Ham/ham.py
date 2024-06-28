import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk
import schedule
import threading
import time

# Function to fetch ham price
def fetch_ham_price():
    url = 'https://www.walmart.com/ip/Marketside-Boneless-Spiral-Cut-Brown-Sugar-Double-Glazed-Ham-Pork-2-0-4-8-lbs/10452662?athbdg=L1600'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract price from the product page
        price_element = soup.find('span', class_='price-characteristic')
        if price_element:
            price = price_element.get('content')
            return [f"${price}"]
        else:
            return ["Price not found"]
    else:
        return [f"Failed to retrieve data. Status code: {response.status_code}"]

# Function to update the price in the GUI
def update_price_list():
    prices = fetch_ham_price()
    price_listbox.delete(0, tk.END)
    for price in prices:
        price_listbox.insert(tk.END, price)

# Function to schedule the price check
def schedule_price_check():
    schedule.every(10).minutes.do(update_price_list)  # Adjust the interval as needed
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Function to run the scheduler in a separate thread
def run_scheduler():
    scheduler_thread = threading.Thread(target=schedule_price_check)
    scheduler_thread.daemon = True
    scheduler_thread.start()

# Create the main window
root = tk.Tk()
root.title("Ham Price Tracker")

# Create and place the widgets
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

price_label = ttk.Label(frame, text="Ham Prices:")
price_label.grid(row=0, column=0, padx=5, pady=5)

price_listbox = tk.Listbox(frame, width=50, height=20)
price_listbox.grid(row=1, column=0, padx=5, pady=5)

refresh_button = ttk.Button(frame, text="Refresh Prices", command=update_price_list)
refresh_button.grid(row=2, column=0, padx=5, pady=5)

# Start the scheduler
run_scheduler()

# Start the GUI event loop
root.mainloop()
