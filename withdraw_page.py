import requests
import os


def recursive_scrape_withdrawal(my_dict, headers, max_value, min_value=20):
    if int(max_value) <= min_value:
        print("Complete")
        return
    else:
        params = {
            'operationName': 'TradeList',
            'variables': '{{"first":250,"orderBy":"TOTAL_VALUE_DESC","status":"LISTED","minTotalValue":{},'
                         '"maxTotalValue":{},"steamAppName":"CSGO"}}'.format(min_value, max_value),
            'extensions': '{"persistedQuery":{"version":1,'
                          '"sha256Hash":"558eeb601ea018453c249e84d465abf7e3c30c17858eafe37e237a979db85766"}} '
        }

        url = 'https://api.{}.com/graphql'.format(os.environ['DOMAIN'])

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print("Response not 200")
            return
        elif 'errors' in response.json():
            if response['errors']:
                error_message = response['errors'][0]['message']
                print(error_message)
                return
        else:
            data = response.json()['data']['trades']['edges']
            if not data:
                print("Empty Array Complete")
                return
            for node in data:
                name = node['node']['tradeItems'][0]['marketName']
                if "★" in name and any(x in name for x in ["Sapphire", "Ruby", "Emerald", "Black Pearl"]):
                    name = name.replace("| ", "| Doppler ")
                value = node['node']['tradeItems'][0]['value']
                markup = node['node']['tradeItems'][0]['markupPercent']
                my_dict[name] = {'value': value, 'markup': markup}

            recursive_scrape_withdrawal(my_dict, headers, max_value=int(value), min_value=min_value)
