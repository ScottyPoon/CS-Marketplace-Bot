import requests
from price_check import check_price
import os

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 '
                  'Safari/537.36',
}


async def calculate_deposit():
    thin_space = "\u2009"
    cookie = os.environ['SESSION_COOKIE']
    headers['cookie'] = f"{cookie}"

    params = {
        'operationName': 'InventoryItemVariants',
        'variables': '{"steamAppName":"CSGO","userId":"{}"}'.format(os.environ['USER_ID']),
        'extensions': '{"persistedQuery":{"version":1,'
                      '"sha256Hash":"c64c734bfdbe803f4efacaa1cb1526a113b2cbf09e09e8a6b1660c0de72035fa"}} '
    }

    url = 'https://api.{}.com/graphql'.format(os.environ['DOMAIN'])

    response = requests.get(url, headers=headers, params=params).json()
    if 'errors' in response:
        if response['errors']:
            error_message = response['errors'][0]['message']
            print(error_message)
            return
    else:
        my_dict = {}
        items_array = response['data']['inventoryItemVariants']['steamItems']
        for items in items_array:
            item = items['itemVariant']
            name = item['externalId']
            if "★" in name and any(x in name for x in ["Sapphire", "Ruby", "Emerald", "Black Pearl"]):
                name = name.replace("| ", "| Doppler ")
            value = item['value']
            if value < 1: break
            my_dict[name] = value

        new_dict = {}
        for item_name, item_value in my_dict.items():
            buff_item_info = await check_price(item_name)
            if isinstance(buff_item_info, tuple):
                buff_value = buff_item_info[0]
                liquidity = float(buff_item_info[1])
            else:
                buff_value = buff_item_info
                liquidity = float('nan')
            ratio = buff_value / (item_value * 1.12)
            new_dict[item_name] = {'roll_price': item_value, 'buff_price': buff_value, 'liquidity': liquidity,
                                   'ratio': ratio}

        sorted_items = sorted(new_dict.items(), key=lambda x: x[1]["ratio"], reverse=False)
        max_name_len = max(len(item[0]) for item in sorted_items)

        for name, values in sorted_items:
            ratio = round(values["ratio"], 2)
            buff_price = round(values["buff_price"], 2)
            if "★" in item:
                print(
                    f"{ratio:.2f} | {name:{max_name_len}} | {values['roll_price']:>7} | {buff_price:>7} | {values['liquidity']:.2f}")
            else:
                print(
                    f"{ratio:.2f} | {name:{max_name_len}}{thin_space} | {values['roll_price']:>7} | {buff_price:>7} | {values['liquidity']:.2f}")
