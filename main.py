import websockets
import requests
import graphql_subscriptions
import json
import os
import asyncio
import socket
from datetime import datetime
from exchange_rate_utils import fetch_exchange_rate
from websocket_withdraw import withdraw_via_websockets
from trades_tracker import start_discord_notifier
from monitor_withdraws import monitor_withdraw
from calculate_crash_game import calculate_crash_ratio
from calculate_withdraw_page import calculate_withdrawal_ratio
from calculate_inventory import calculate_deposit


def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


def start():
    # Original blacklist
    blacklist = []

    # Retrieve additional strings from environment variable
    additional_strings = os.getenv("ADDITIONAL_BLACKLIST", "")
    additional_strings = additional_strings.split(",")

    # Add additional strings to the blacklist if not empty
    if additional_strings != ['']:
        blacklist += additional_strings

    min_price = float(os.environ['MIN_PRICE'])
    ratio = float(os.environ['RATIO'])
    liquidity = float(os.environ['LIQUIDITY'])
    cookie = os.environ['SESSION_COOKIE']

    choice = None

    print(f'Machine IP Address: {get_ip_address()}')
    print(f'Blacklist: {blacklist}')
    while True:
        if choice is None:
            print('-------------------------------------')
            print('Select an option:')
            print(f'[1] Withdraw Ratio {ratio}')
            print('[2] Withdraw Low Float Gloves')
            print('[3] Withdraw Floats')
            print('[4] Trade Notifier')
            print('[5] Monitor Websocket')
            print('[6] Calculate Crash Items')
            print('[7] Calculate Withdrawal Page')
            print('[8] Calculate Deposit')
            print('[0] Exit')
            print('-------------------------------------')

        choice = input('>>')

        if choice == '1':
            asyncio.run(
                withdraw_via_websockets(cookie, blacklist, min_price, liquidity, ratio))
        elif choice == '2':
            print("Not for public version")
        elif choice == '3':
            print("Not for public version")
        elif choice == '4':
            asyncio.run(start_discord_notifier())
        elif choice == '5':
            asyncio.run(monitor_withdraw())
        elif choice == '6':
            if 'DYNO' in os.environ:
                crash_min_price_input = int(input("Enter Min Price "))
                crash_max_price_input = int(input("Enter Max Price "))
                asyncio.run(calculate_crash_ratio(crash_min_price_input, crash_max_price_input))
            else:
                print("Unable to be used in this environment")
        elif choice == '7':
            if 'DYNO' in os.environ:
                min_price_input = int(input("Enter Min Price "))
                max_price_input = int(input("Enter Max Price "))
                asyncio.run(calculate_withdrawal_ratio(min_price_input, max_price_input))
            else:
                print("Unable to be used in this environment")
        elif choice == '8':
            asyncio.run(calculate_deposit())
        elif choice == '0':
            break  # Exit the loop and end the program
        else:
            print("Invalid option.")
        choice = None  # Reset choice to None to print the menu again


if __name__ == "__main__":
    start()
