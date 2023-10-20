import requests
import os
from exchange_rate_utils import fetch_exchange_rate
import logging
from backoff import on_exception, expo

buff_prices = requests.get('https://raw.githubusercontent.com/ScottyPoon/buff-prices/main/buff_prices.json',
                           headers={'Authorization': 'Token ' + os.environ['HUB_TOKEN']}).json()

buff_ids = requests.get('https://raw.githubusercontent.com/ScottyPoon/buff-prices/main/buff_id.json',
                           headers={'Authorization': 'Token ' + os.environ['HUB_TOKEN']}).json()

USD = fetch_exchange_rate()
buff_prices_rmb = {
    key: {
        'price': round(value['price'] * USD, 2),
        'liquidity': value['liquidity'],
        'type': value['type']
    }
    for key, value in buff_prices.items()
}


# Handle KeyError
def handle_key_error(name):
    logging.error(f'I got a KeyError - reason {name}')
    return 0


# Get prices directly from buff163
@on_exception(expo, requests.exceptions.RequestException, max_time=60)
def get_buff_price(name):
    try:
        buff_id = buff_ids[name]
        url = f"https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={buff_id}"
        response = requests.get(url)
        status = response.status_code

        if status != 200:
            raise requests.exceptions.RequestException()

        data = response.json()
        if len(data['data']['items']) < 9:
            return 0

        lowest_price = data['data']['items'][0]['price']
        return float(lowest_price)
    except KeyError as e:
        return handle_key_error(e)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return 0


async def check_price(name):
    try:
        return buff_prices_rmb[name]['price'], buff_prices_rmb[name]['liquidity']
    except KeyError:
        if 'DYNO' in os.environ:
            return get_buff_price(name)
        else:
            return f'Not heroku instance'
    except Exception as e:
        print("Encountered error in check_price function:", e)

