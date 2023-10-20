import websockets
from graphql_subscriptions import subscribe_to_onupdatetrade, subscribe_to_OnUpdateTradeLong
import json
from datetime import datetime
import os
import discord
from discord.ext import commands
from discord import Intents
import asyncio
import pytz
import requests

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = Intents.default()
intents.typing = False  # Disable typing events
intents.presences = True  # Disable presence events
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_connect():
    print("Connected to Discord")
    print("Starting...")
    await track_trades_via_websockets_new(os.environ['USER_ID'], os.environ['SESSION_COOKIE'])  # Replace with your desired user ID


async def send_notification(joined_at, market_name, float_value, total_value, markup, withdrawer, withdrawer_trade_url):
    channel_id = os.environ['CHANNEL_ID']  # Replace with your Discord channel ID

    # Retrieve the channel object
    channel = bot.get_channel(channel_id)

    # Compose the notification message
    message = f"<@{os.environ['DISCORD_ID']}> [{joined_at}] {market_name} {float_value} {total_value} {markup}% {withdrawer} {withdrawer_trade_url}"

    # Send the notification message to the channel
    await channel.send(message)


async def send_notification_new(message):
    channel_id = os.environ['CHANNEL_ID']  # Replace with your Discord channel ID

    # Retrieve the channel object
    channel = bot.get_channel(channel_id)

    # Compose the notification message
    new_message = f"<@{os.environ['DISCORD_ID']}> {message}"

    # Send the notification message to the channel
    await channel.send(new_message)


async def extract(response):
    if response.get('type') != 'connection_ack':
        print(response)
    australia_tz = pytz.timezone('Australia/Sydney')
    current_time = datetime.now(australia_tz)
    joined_at = current_time.strftime("%H:%M")
    trade = response['payload']['data']['updateTrade']['trade']
    status = trade['status']
    markup = trade['markupPercent']
    withdrawer_trade_url = trade['withdrawerSteamTradeUrl'] if trade['withdrawerSteamTradeUrl'] is not None else ""
    withdrawer = trade['withdrawer'] if trade['withdrawer'] is not None else ""
    total_value = trade['totalValue']
    market_name = trade['tradeItems'][0]['marketName']
    # joined_at = datetime.strptime(trade['joinedAt'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H:%M:%S.%f")[:-3]
    float_value = trade['avgPaintWear']
    has_stickers = trade['hasStickers']

    if status == "PROCESSING":  # Change Status to JOINED if depositing
        print(
            f"PROCESSING [{joined_at}] {market_name} {float_value} {total_value} {markup}%{withdrawer}{withdrawer_trade_url}")
        await send_notification(joined_at, market_name, float_value, total_value, markup, withdrawer,
                                withdrawer_trade_url)
    elif status == "COMPLETED":
        print(
            f"COMPLETE [{joined_at}] {market_name} {float_value} {total_value} {markup}%{withdrawer}{withdrawer_trade_url}")


async def track_trades_via_websockets(userID):
    print("User ID is", userID)
    while True:
        async with websockets.connect('wss://api.{}.com/graphql'.format(os.environ['DOMAIN']),
                                      subprotocols=['graphql-transport-ws'],
                                      ) as websocket:

            try:
                await websocket.send('{"type": "connection_init"}')

                await subscribe_to_onupdatetrade(websocket, userID)
                while True:
                    response = json.loads(await websocket.recv())
                    try:
                        await extract(response)
                    except KeyError:
                        error_message = response.get('payload', {}).get('errors', [{}])[0].get('message')
                        if error_message:
                            print(f'[{datetime.now().strftime("%H:%M:%S.%f")[:-3]}] {error_message}')
                        if error_message == "This withdrawal exceeds your daily withdrawal limit":
                            print("Quitting Program")
                            return

            except websockets.exceptions.ConnectionClosed:
                pass
            except Exception as e:
                print('The Exception in last line is', e)


def fetch_buff_ids_github():
    buff_ids = requests.get('https://raw.githubusercontent.com/ScottyPoon/buff-prices/main/buff_id.json',
                            headers={'Authorization': 'Token ' + os.environ['HUB_TOKEN']}).json()
    return buff_ids


def get_buff_url(name, buff_id_dict):
    buff_id = buff_id_dict.get(name)
    if buff_id is None:
        return "item-not-found"

    url = f"https://buff.163.com/goods/{buff_id}?from=market#tab=selling"
    return url


async def extract_new(response, buff_id_dict):
    if response.get('type') != 'connection_ack':
        print(response)
    australia_tz = pytz.timezone('Australia/Sydney')
    current_time = datetime.now(australia_tz)
    joined_at = current_time.strftime("%H:%M")
    trade = response['payload']['data']['updateTrade']['trade']
    status = trade['status']
    markup = trade['markupPercent']

    withdrawer_trade_url = trade['withdrawerSteamTradeUrl'] if trade['withdrawerSteamTradeUrl'] is not None else ""
    withdrawer = trade['withdrawer'] if trade['withdrawer'] is not None else ""
    total_value = trade['totalValue']
    market_name = trade['tradeItems'][0]['marketName']
    # joined_at = datetime.strptime(trade['joinedAt'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H:%M:%S.%f")[:-3]
    float_value = trade['avgPaintWear']
    has_stickers = trade['hasStickers']
    transaction_type = 'deposit'
    depositor_info = trade['depositor']
    print('depo info', depositor_info)
    depositor_steam_id = depositor_info['steamId']
    print('depo steamid', depositor_steam_id)
    if depositor_steam_id is None:
        transaction_type = "withdraw"
    print('transaction type', transaction_type)
    print("Status", status)
    if status == "PROCESSING":
        if transaction_type == "withdraw":  # Change Status to JOINED if depositing
            message = f"PROCESSING WITHDRAW [{joined_at}] {market_name} {float_value} {total_value} {markup}% {get_buff_url(market_name, buff_id_dict)}"
            print(message)
            await send_notification_new(message)
    elif status == "JOINED":
        message = f"PROCESSING DEPOSIT [{joined_at}] {market_name} {float_value} {total_value} {markup}%{withdrawer}{withdrawer_trade_url}"
        if transaction_type == "deposit":
            print(message)
            await send_notification_new(message)
    elif status == "COMPLETED":
        print(
            f"COMPLETE [{joined_at}] {market_name} {float_value} {total_value} {markup}%{withdrawer}{withdrawer_trade_url}")


async def track_trades_via_websockets_new(userID, cookie):
    print("User ID is", userID)
    buff_id_dictionary = fetch_buff_ids_github()
    while True:
        async with websockets.connect('wss://api.{}.com/graphql'.format(os.environ['DOMAIN']),
                                      subprotocols=['graphql-transport-ws'],
                                      extra_headers={'cookie': f'{cookie}'}
                                      ) as websocket:

            try:
                await websocket.send('{"type": "connection_init"}')

                await subscribe_to_OnUpdateTradeLong(websocket, userID)
                while True:
                    response = json.loads(await websocket.recv())
                    try:
                        await extract_new(response, buff_id_dictionary)
                    except KeyError:
                        error_message = response.get('payload', {}).get('errors', [{}])[0].get('message')
                        if error_message:
                            print(f'[{datetime.now().strftime("%H:%M:%S.%f")[:-3]}] {error_message}')
                        if error_message == "This withdrawal exceeds your daily withdrawal limit":
                            print("Quitting Program")
                            return

            except websockets.exceptions.ConnectionClosed:
                pass
            except Exception as e:
                print('The Exception in last line is', e)


async def start_discord_notifier():
    await bot.start(DISCORD_TOKEN)
    print("Bot started")
