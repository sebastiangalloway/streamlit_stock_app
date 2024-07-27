import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define the logo file path (ensure the logo image is available in your working directory or provide a URL)
logo_path = "stock-market.png"  # Replace with your logo file path or URL

# Layout for title and logo on the same line
col1, col2 = st.columns([1, 5])  # Adjust the proportions as needed
with col1:
    st.image(logo_path, width=100)  # Adjust the width as needed
with col2:
    st.title("Stock Analysis Dashboard")

st.title("Stock Analysis Dashboard")

# Initialize session state for inputs if they don't exist
if 'user_input' not in st.session_state:
    st.session_state.user_input = "AAPL, MSFT, GOOGL"
if 'comparison_range_input' not in st.session_state:
    st.session_state.comparison_range_input = "2"

# Function to clear inputs
def clear_inputs():
    st.session_state.user_input = ""
    st.session_state.comparison_range_input = "2"

# Create a row with four columns for the "Clear All" button and checkboxes
col1, col2, col3, col4 = st.columns(4)
with col1:
    clear_button = st.button("Clear All")
with col2:
    show_dataframe = st.checkbox("Show Dataframe", value=True)
with col3:
    show_line_chart = st.checkbox("Show Line Chart", value=True)
with col4:
    show_bar_chart = st.checkbox("Show Bar Chart", value=True)

# If the "Clear All" button is pressed, clear inputs
if clear_button:
    clear_inputs()

# Streamlit input for stock symbols and comparison range, linked to session state
user_input = st.text_input("Enter Stock Symbols (comma-separated)", st.session_state.user_input, key="user_input")
symbols = [symbol.strip().upper() for symbol in user_input.split(",") if symbol.strip()]

comparison_range_input = st.text_input("Enter Comparison Length in Price. The Max is 252", st.session_state.comparison_range_input, key="comparison_range_input")
try:
    comparison_range = int(comparison_range_input)
    if comparison_range < 1 or comparison_range > 252:
        st.error("Please enter a valid comparison range between 1 and 252.")
        comparison_range = 5  # Default value if input is invalid
except ValueError:
    st.error("Invalid input. Please enter a number.")
    comparison_range = 5  # Default value if input is not a number

# Function to fetch stock data and compare prices over a specified number of days
def get_stock_data(symbols, comparison_range=2):
    data = {}
    stock_histories = {}
    try:
        for symbol in symbols:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y")  # Fetch data over the last year

            if len(hist) >= comparison_range:
                latest_price = hist['Close'].iloc[-1]
                previous_price = hist['Close'].iloc[-comparison_range] if comparison_range <= len(hist) else hist['Close'].iloc[0]
                change = latest_price - previous_price
                change_percent = (change / previous_price) * 100 if previous_price != 0 else 0
                stock_histories[symbol] = hist['Close'].iloc[-comparison_range:]  # Store the relevant closing prices
            else:
                latest_price = None
                change = None
                change_percent = None
                stock_histories[symbol] = pd.Series()  # Empty series if not enough data

            data[symbol] = {
                'Symbol': symbol,
                'Price': latest_price,
                'Change over ' + str(comparison_range) + ' days': change,
                'Change in %': change_percent
            }

        return pd.DataFrame.from_dict(data, orient='index'), stock_histories
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame(), {}

# Fetch stock data and histories
stock_data_df, stock_histories = get_stock_data(symbols, comparison_range)

# Dataframe display with success/error messages
if show_dataframe:
    if not stock_data_df.empty:
        st.write("**Stock Data**")
        st.dataframe(stock_data_df)
        st.success("Dataframe generated successfully.")
    else:
        st.error("Failed to generate dataframe. No data available.")

# Combine all stock histories into one DataFrame for the line chart
if show_line_chart:
    combined_histories = pd.DataFrame()
    for symbol, history in stock_histories.items():
        if not history.empty:
            combined_histories[symbol] = history

    if not combined_histories.empty:
        st.write(f"**Closing Prices for Selected Stocks over the last {comparison_range} days**")
        st.line_chart(combined_histories)
        st.success("Line chart generated successfully.")
    else:
        st.error("Failed to generate line chart. No data available.")

# Plotting percentage change over the comparison interval using a single bar chart with Matplotlib
if show_bar_chart:
    if not stock_data_df.empty:
        st.write("**Percentage Change Over Comparison Interval**")
        fig, ax = plt.subplots()
        colors = plt.cm.viridis(np.linspace(0, 1, len(stock_data_df)))
        ax.bar(stock_data_df.index, stock_data_df['Change in %'], color=colors, width=0.4)
        ax.set_ylabel('Percentage Change (%)')
        ax.set_title('Percentage Change Over Comparison Interval')
        ax.set_xlabel('Stock Symbol')
        plt.xticks(rotation=45)
        plt.tight_layout()  # Ensure everything fits without overlapping
        st.pyplot(fig)
        st.success("Bar chart generated successfully.")
    else:
        st.error("Failed to generate bar chart. No data available.")
