from flask import Flask, render_template, request
import requests
import pygal
from pygal.style import DarkSolarizedStyle
from datetime import datetime
import csv

app = Flask(__name__)
api_key = '5EW2VPXRG7XF7PWK'  

# Function to fetch stock data from Alpha Vantage
def get_stock_data(symbol, function, start_date, end_date):
    url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}&datatype=json'
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error: Failed to retrieve data. HTTP Status code: {response.status_code}")
        return None
    
    data = response.json()
    if 'Error Message' in data or not data:
        print("Error: No data received from API.")
        return None
    
    time_series_key = list(data.keys())[-1]
    if time_series_key not in data:
        print(f"Error: Time series data not found for {symbol}.")
        return None
    
    stock_data = data[time_series_key]
    filtered_data = {date: value for date, value in stock_data.items() if start_date <= date <= end_date}
    
    if not filtered_data:
        print(f"No data available for {symbol} in the specified date range.")
        return None
    
    return filtered_data

# Function to generate the chart with Open, High, Low, and Close prices
def create_chart(data, title, chart_type):
    if chart_type == 'Line':
        chart = pygal.Line(style=DarkSolarizedStyle)
    elif chart_type == 'Bar':
        chart = pygal.Bar(style=DarkSolarizedStyle)
    else:
        print("Invalid chart type!")
        return

    chart.title = title
    chart.x_labels = list(data.keys())
    open_prices = [float(info['1. open']) for info in data.values()]
    high_prices = [float(info['2. high']) for info in data.values()]
    low_prices = [float(info['3. low']) for info in data.values()]
    close_prices = [float(info['4. close']) for info in data.values()]

    chart.add('Open', open_prices)
    chart.add('High', high_prices)
    chart.add('Low', low_prices)
    chart.add('Close', close_prices)
    
    return chart.render_data_uri()

# Load stock symbols from CSV
def load_stock_symbols():
    symbols = []
    with open('stocks.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header if present
        symbols = [row[0] for row in reader]
    return symbols

@app.route('/', methods=['GET', 'POST'])
def index():
    symbols = load_stock_symbols()
    chart_uri = None
    if request.method == 'POST':
        symbol = request.form['symbol']
        chart_type = request.form['chart_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        stock_data = get_stock_data(symbol, "TIME_SERIES_DAILY", start_date, end_date)
        if stock_data:
            chart_uri = create_chart(stock_data, f"{symbol} Stock Prices", chart_type)
    
    return render_template('index.html', symbols=symbols, chart_uri=chart_uri)

if __name__ == '__main__':
    app.run(debug=True)
