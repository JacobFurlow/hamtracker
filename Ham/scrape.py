from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import tkinter as tk
from tkinter import ttk
import schedule
import threading
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to fetch ham prices from The Food XP
def fetch_ham_price():
    options = Options()
    options.headless = True
    options.add_argument("--headless")  # Ensure headless mode is activated
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")  # Necessary to set screen size in headless mode
    options.add_argument("--log-level=3")  # Suppress unnecessary logging
    service = Service('C:/WebDrivers/chromedriver.exe')  # Ensure this path points to the actual executable
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        logging.info("Fetching ham prices from The Food XP.")
        driver.get('https://thefoodxp.com/honey-baked-ham-menu-prices/')
        time.sleep(5)  # Give the page time to load

        # Scrape the ham prices
        prices = []
        rows = driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) == 2:
                item = cells[0].text.strip()
                price = cells[1].text.strip()
                prices.append(f"{item}: {price}")
        
        if prices:
            return "\n".join(prices)
        else:
            return "Prices not found"
    except Exception as e:
        logging.error(f"Error fetching prices: {e}")
        return f"Error: {str(e)}"
    finally:
        driver.quit()

# Function to update the prices in the GUI
def update_price():
    status_label.config(text="Fetching prices...")
    price_text.config(state=tk.NORMAL)
    price_text.delete('1.0', tk.END)
    price_text.insert(tk.END, "Fetching prices...\n")
    price_text.config(state=tk.DISABLED)

    def fetch_and_update():
        prices = fetch_ham_price()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        price_text.config(state=tk.NORMAL)
        price_text.delete('1.0', tk.END)
        price_text.insert(tk.END, prices)
        price_text.config(state=tk.DISABLED)
        status_label.config(text=f"Last updated: {current_time}")

    threading.Thread(target=fetch_and_update).start()

# Function to schedule the price check
def schedule_price_check():
    schedule.every(1).minutes.do(update_price)  # Adjust the interval as needed
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Function to run the scheduler in a separate thread
def run_scheduler():
    scheduler_thread = threading.Thread(target=schedule_price_check)
    scheduler_thread.daemon = True
    scheduler_thread.start()

# Function to save prices to a file
def save_to_file():
    prices = price_text.get('1.0', tk.END).strip()
    if prices and prices != "Fetching prices...":
        with open("ham_prices.txt", "w") as file:
            file.write(prices)
        status_label.config(text="Prices saved to ham_prices.txt")
    else:
        status_label.config(text="No prices to save")

# Function to toggle auto-refresh
def toggle_auto_refresh():
    global auto_refresh
    auto_refresh = not auto_refresh
    if auto_refresh:
        run_scheduler()
        toggle_button.config(text="Stop Auto-refresh")
    else:
        schedule.clear()
        toggle_button.config(text="Start Auto-refresh")

# Function to switch between dark and light modes
def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        root.configure(bg='#2c3e50')
        frame.configure(style="TFrame")
        price_text.configure(bg='#34495e', fg='#ecf0f1')
        button_frame.configure(style="TFrame")
        status_label.configure(background='#2c3e50', foreground='#ecf0f1')
    else:
        root.configure(bg='#ecf0f1')
        frame.configure(style="Light.TFrame")
        price_text.configure(bg='#ffffff', fg='#000000')
        button_frame.configure(style="Light.TFrame")
        status_label.configure(background='#ecf0f1', foreground='#000000')

# Create the main window
root = tk.Tk()
root.title("Ham Price Tracker")
root.geometry("500x450")
root.configure(bg='#2c3e50')

# Create and place the widgets
style = ttk.Style()
style.theme_use("clam")  # Use the 'clam' theme for a more modern look
style.configure("TFrame", background="#2c3e50")
style.configure("Light.TFrame", background="#ecf0f1")
style.configure("TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Helvetica", 14))
style.configure("Light.TLabel", background="#ecf0f1", foreground="#000000", font=("Helvetica", 14))
style.configure("TButton", background="#34495e", foreground="#ecf0f1", font=("Helvetica", 12), padding=10, borderwidth=0)
style.map("TButton",
          background=[("active", "#1abc9c")],
          foreground=[("active", "#2c3e50")])

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Create a canvas and scrollbar to make the price list scrollable
canvas = tk.Canvas(frame, bg='#2c3e50', highlightthickness=0)
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas, style="TFrame")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Add the price list text widget
price_text = tk.Text(scrollable_frame, wrap="word", font=("Helvetica", 12), state=tk.DISABLED, height=15, width=50, bg='#34495e', fg='#ecf0f1', bd=0, highlightthickness=0)
price_text.grid(row=0, column=0, padx=10, pady=5)

# Pack the canvas and scrollbar
canvas.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

# Create a frame for buttons at the bottom
button_frame = ttk.Frame(root, padding="10", style="TFrame")
button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

# Add the fetch prices button
fetch_button = ttk.Button(button_frame, text="Fetch Prices", command=update_price)
fetch_button.grid(row=0, column=0, pady=5, padx=5)

# Add the refresh button
refresh_button = ttk.Button(button_frame, text="Refresh Prices", command=update_price)
refresh_button.grid(row=0, column=1, pady=5, padx=5)

# Add the save to file button
save_button = ttk.Button(button_frame, text="Save to File", command=save_to_file)
save_button.grid(row=0, column=2, pady=5, padx=5)

# Add the auto-refresh toggle button
toggle_button = ttk.Button(button_frame, text="Start Auto-refresh", command=toggle_auto_refresh)
toggle_button.grid(row=1, column=0, pady=5, padx=5, columnspan=2)

# Add the theme toggle button
theme_button = ttk.Button(button_frame, text="Toggle Dark/Light Mode", command=toggle_theme)
theme_button.grid(row=1, column=2, pady=5, padx=5)

# Add the status label
status_label = ttk.Label(root, text="", style="TLabel")
status_label.grid(row=2, column=0, pady=5, padx=5)

# Initial state
auto_refresh = False
dark_mode = True

# Start the scheduler
run_scheduler()

# Start the GUI event loop
root.mainloop()

# Quit the WebDriver when the application exits
def on_closing():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
