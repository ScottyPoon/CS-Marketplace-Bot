import re
import requests
import os


def fetch_exchange_rate():
    url = "https://www.forbes.com/advisor/money-transfer/currency-converter/usd-cny/"

    # Send a GET request to the website
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        pattern = r'(\d+\.\d+) CNY'

        # Find the exchange rate using the pattern
        match = re.search(pattern, response.text)

        if match:
            # Extract the exchange rate value
            exchange_rate = match.group(1)

            # Return the exchange rate
            return float(exchange_rate)
        else:
            print("Failed to find the exchange rate")
            return None
    else:
        print("Using ENV for ex rate")
        os_exchange_rate = os.getenv('EXCHANGE_RATE')
        if os_exchange_rate:
            return float(os_exchange_rate)
        else:
            print("No exchange rate ENV detected")