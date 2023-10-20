import requests
import math
from price_check import check_price
import os

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 '
                  'Safari/537.36',
}


def recursive_scrape_crash(my_dict, max_value, min_value=10, prev_name=None, prev_max_value=None):
    if max_value <= min_value:
        print("Max value is greater than the min value")
        return
    else:
        params = {
            'operationName': 'ItemVariantList',
            'variables': '{{"first":250,"minValue":{},"maxValue":{},"categoryId":"","marketId":null,"name":"",'
                         '"orderBy":"VALUE_DESC","size":"","distinctValues":true,"minValueUpdatedAt":null,'
                         '"usable":true,"obtainable":true,"withdrawable":true}}'.format(min_value, max_value),
            'extensions': '{"persistedQuery":{"version":1,'
                          '"sha256Hash":"f52769449b71d7e80961cc95fd22a368eb309a40442809953b9181d3428cfa03"}} '
        }

        url = 'https://api.{}.com/graphql'.format(os.environ['DOMAIN'])

        response = requests.get(url, headers=headers, params=params)

        data = response.json()['data']['itemVariants']['edges']
        for i in data:
            name = i['node']['externalId']
            if "★" in name and "Gloves" not in name and any(x in name for x in ["Sapphire", "Ruby", "Emerald", "Black Pearl"]):
                name = name.replace("| ", "| Doppler ")
            value = i['node']['value']
            my_dict[name] = value

            # Check if the current name and max_value are equal to the previous ones
            if name == prev_name and max_value == prev_max_value:
                return

            prev_name = name
            prev_max_value = max_value
            print(max_value, name, value)
        recursive_scrape_crash(my_dict, max_value=value, min_value=min_value, prev_name=prev_name,
                               prev_max_value=prev_max_value)


async def calculate_crash_ratio(min_value, max_value):
    roll_item_prices = {}
    recursive_scrape_crash(roll_item_prices, min_value=min_value, max_value=max_value)

    item_data = {}
    for item_name, item_value in roll_item_prices.items():
        buff_item_info = await check_price(item_name)
        if isinstance(buff_item_info, tuple):
            buff_value = buff_item_info[0]
            liquidity = float(buff_item_info[1])
        else:
            print("Item", item_name)
            buff_value = buff_item_info
            liquidity = float('nan')

        ratio = buff_value / (item_value * 1.12)
        if ratio == 0:
            continue
        if math.isnan(liquidity) or liquidity >= 0.7:
            if math.isnan(liquidity):
                liquidity_str = "NaN"
            else:
                liquidity_str = f"{liquidity:.2f}"

            item_data[item_name] = {
                'roll_price': item_value,
                'buff_price': buff_value,
                'liquidity': liquidity_str,
                'ratio': ratio
            }

    sorted_items = sorted(item_data.items(), key=lambda x: x[1]["ratio"], reverse=True)
    max_name_len = max(len(item[0]) for item in sorted_items)

    for item in sorted_items:
        ratio = round(item[1]["ratio"], 2)
        buff_price = round(item[1]["buff_price"], 2)
        print(
            f"{ratio:.2f} | {item[0]:{max_name_len}} | {item[1]['roll_price']:>5} | {buff_price:>8} | {item[1]['liquidity']}")
