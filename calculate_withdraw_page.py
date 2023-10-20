import requests
import math
from price_check import check_price
import os

headers = {
    'cookie': os.environ['SESSION_COOKIE'],
    'referer': 'https://www.{}.com/'.format(os.environ['DOMAIN']),
}


def recursive_scrape_withdrawal(my_dict, max_value, min_value=20):
    if int(max_value) <= min_value:
        print("Complete")
        return
    else:
        params = {
            'operationName': 'TradeList',
            'variables': '{{"first":250,"orderBy":"TOTAL_VALUE_DESC","status":"LISTED","minTotalValue":{},'
                         '"maxTotalValue":{},"steamAppName":"CSGO"}}'.format(min_value, max_value),
            'extensions': '{"persistedQuery":{"version":1,'
                          '"sha256Hash":"e0cdf4dff95e785c2633abca231d02adb7a640f519e891131f5c6c0dddb0de60"}}'
        }

        url = 'https://api.{}.com/graphql'.format(os.environ['DOMAIN'])

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print("Response not 200")
            return
        elif 'errors' in response.json():
            if response.json()['errors']:
                error_message = response.json()['errors'][0]['message']
                if error_message == 'PersistedQueryNotFound':
                    print('PersistedQueryNotFound this might indicate sha256Hash is old')
                else:
                    print(error_message)
                return
        else:
            data = response.json()['data']['trades']['edges']
            if not data:
                print("Empty Array Complete")
                return
            for node in data:
                name = node['node']['tradeItems'][0]['marketName']
                if "★" in name and "Gloves" not in name and any(
                        x in name for x in ["Sapphire", "Ruby", "Emerald", "Black Pearl"]):
                    name = name.replace("| ", "| Doppler ")
                value = node['node']['tradeItems'][0]['value']
                display_value = node['node']['tradeItems'][0]['itemVariant']['displayValue']
                if display_value < min_value * 1.12:
                    continue
                markup = node['node']['tradeItems'][0]['markupPercent']
                print(name, value, display_value, markup)
                my_dict[name] = {'value': value, 'display_value': display_value, 'markup': markup}

            recursive_scrape_withdrawal(my_dict, max_value=int(value), min_value=min_value)


async def calculate_withdrawal_ratio(min_value, max_value):
    my_dict = {}
    recursive_scrape_withdrawal(my_dict, max_value=max_value, min_value=min_value)

    new_dict = {}
    for item_name, item_value in my_dict.items():

        markup = item_value['markup']
        markup_multiplier = 1.12
        if markup < 12:
            markup_multiplier = (markup / 100) + 1
        buff_item_info = await check_price(item_name)
        if isinstance(buff_item_info, tuple):
            buff_value = buff_item_info[0]
            liquidity = float(buff_item_info[1])
        else:
            print("Item", item_name)
            buff_value = buff_item_info
            liquidity = float('nan')
        ratio = buff_value / (item_value['display_value'] * markup_multiplier)
        if ratio == 0:
            continue
        if math.isnan(liquidity) or liquidity >= 0.7:
            if math.isnan(liquidity):
                liquidity_str = "NaN"
            else:
                liquidity_str = f"{liquidity:.2f}"

            new_dict[item_name] = {
                'roll_price': item_value['display_value'],
                'buff_price': buff_value,
                'liquidity': liquidity_str,
                'ratio': ratio,
                'markup': markup
            }

    sorted_items = sorted(new_dict.items(), key=lambda x: x[1]["ratio"], reverse=True)
    max_name_len = max(len(item[0]) for item in sorted_items)

    for name, values in sorted_items:
        ratio = round(values["ratio"], 2)
        buff_price = round(values["buff_price"], 2)
        if "龍王" in name:
            print(
                f"{ratio:.2f} | {name:{max_name_len}} | {values['roll_price']:>9} | {buff_price:>7} | {values['liquidity']:>5} | {values['markup']:>5}")
        else:
            print(
                f"{ratio:.2f} | {name:{max_name_len + 2}} | {values['roll_price']:>9} | {buff_price:>7} | {values['liquidity']:>5} | {values['markup']:>5}")
