import requests
import json
import os

headers = {
    'authority': 'api.{}.com'.format(os.environ['DOMAIN']),
    'accept': 'application/json, text/plain, */*',
    'ngsw-bypass': 'true',
    'origin': 'https://www.{}.com'.format(os.environ['DOMAIN']),
    'referer': 'https://www.{}.com/'.format(os.environ['DOMAIN']),
    'sec-ch-ua': '"Chromium";v="112", "Not_A Brand";v="24", "Opera";v="98"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
                  'Safari/537.36 OPR/98.0.0.0',
}


def get_coins_old(cookie):
    headers['cookie'] = f"{cookie}"

    params = {
        'operationName': 'UserSummary',
        'variables': '{"id":"{}"}'.format(os.environ['USER_ID']),
        'extensions': '{"persistedQuery":{"version":1,'
                      '"sha256Hash":"f3058db0904e8e26ccd43e96208ae58598cb217e3eb1599c3872126a018c4e21"}}'
    }

    url = 'https://api.{}.com/graphql'.format(os.environ['DOMAIN'])

    response = requests.get(url, headers=headers, params=params).json()

    if 'errors' in response:
        if response['errors']:
            error_message = response['errors'][0]['message']
            print(error_message)
            return
    else:
        user_info = response['data']['user']
        daily_withdraw_limit = user_info['dailyWithdrawLimit']
        supplier = user_info['supplier']
        suspected_trader = user_info['suspectedTrader']
        coins = user_info['wallets'][0]['amount']
        print(
            f'[Daily Withdraw Limit] {daily_withdraw_limit}\n[Is Supplier] {supplier}\n[Is Suspected Trader] {suspected_trader}\n[Balance] {coins}TKN')
        return coins


def get_coins(cookie):
    headers['cookie'] = f"{cookie}"

    params = {
        'operationName': 'UserSummary',
        'variables': '{"id":"{}"}'.format(os.environ['USER_ID']),
        'extensions': '{"persistedQuery":{"version":1,'
                      '"sha256Hash":"1d2c7e558da1c40575f81750bdc7e43bf47eae898194aaca16817a6fa7640954"}}'
    }

    url = 'https://api.{}.com/graphql'.format(os.environ['DOMAIN'])

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if 'errors' in data:
            error_message = data['errors'][0]['message']
            print(error_message)
            return None
        else:
            try:
                user_info = data.get('data', {}).get('user')
                if not user_info:
                    print('User info not found in the response.')
                    print(f'Response: {json.dumps(data, indent=2)}')
                    return None

                daily_withdraw_limit = user_info.get('dailyWithdrawLimit')
                supplier = user_info.get('supplier')
                suspected_trader = user_info.get('suspectedTrader')
                wallets = user_info.get('wallets')
                if not wallets or not isinstance(wallets, list) or len(wallets) < 1:
                    print('Wallets not found or not in the expected format.')
                    return None

                coins = wallets[0].get('amount')
                if coins is None:
                    print('Coins not found in the first wallet.')
                    return None
                print(
                    f'[Daily Withdraw Limit] {daily_withdraw_limit}\n[Is Supplier] {supplier}\n[Is Suspected Trader] {suspected_trader}\n[Balance] {coins}TKN')
                return coins
            except Exception as e:
                print(f'Error parsing user info: {str(e)}')
                print(f'Response: {json.dumps(data, indent=2)}')
                return None
    except requests.exceptions.RequestException as e:
        print(f'Request error: {str(e)}')
        return None
