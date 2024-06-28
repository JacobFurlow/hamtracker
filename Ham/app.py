from flask import Flask, render_template_string
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Ham Price Tracker</title>
        </head>
        <body>
            <h1>Ham Prices</h1>
            <textarea id="prices" rows="20" cols="50" readonly></textarea><br>
            <button onclick="fetchPrices()">Fetch Prices</button>
            <script>
                function fetchPrices() {
                    fetch('/fetch_prices')
                        .then(response => response.text())
                        .then(data => {
                            document.getElementById('prices').value = data;
                        });
                }
            </script>
        </body>
        </html>
    ''')

@app.route('/fetch_prices')
def fetch_prices():
    # Replace with your actual price fetching logic
    return "Fetching prices..."

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
