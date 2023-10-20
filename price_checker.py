import json
import requests
import os
from github import Github
import base64
import logging
from forex_python.converter import CurrencyRates
import time
from backoff import on_exception, expo
import re
from exchange_rate_utils import fetch_exchange_rate


# Fetch files >1MB from Github
def get_blob_content(repo, branch, path_name):
    ref = repo.get_git_ref(f'heads/{branch}')
    tree = repo.get_git_tree(ref.object.sha, recursive='/' in path_name).tree
    sha = [x.sha for x in tree if x.path == path_name]
    if not sha:
        return None
    return repo.get_git_blob(sha[0])


# Handle KeyError
def handle_key_error(name):
    logging.error(f'I got a KeyError - reason {name}')
    return 0



# Get the amount of times the item is listed on buff163
def get_buff_amount(name):
    if "Doppler" in name and "Factory New" in name:
        return 10

    try:
        buff_id = buff_ID_Dict[name]
        url = f"https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={buff_id}"
        response = requests.get(url)
        status = response.status_code

        if status != 200:
            raise requests.exceptions.RequestException()

        data = response.json()
        return len(data['data']['items'])

    except KeyError as e:
        return handle_key_error(e)
    except Exception as e:
        print('error', e)
        logging.error(f"An error occurred: {e}")
        return 0


USDRMBPRICE = fetch_exchange_rate()


# Gets prices from buff163 or github repository
async def check_price(name):
    try:
        return pricempire_prices[name]['price'] * USDRMBPRICE, pricempire_prices[name]['liquidity']
    except KeyError as e:
        # print(e)
        if "Doppler" in name:
            return _get_doppler_price(name)
        else:
            return get_buff_price(name)


def _get_doppler_price(name):
    gems = ["Emerald", "Sapphire", "Ruby", "Black Pearl"]  # Empire specific?
    if any(word in name for word in gems):
        name = _clean_doppler_name(name)
        return pricempire_prices.get(name, 0) * USDRMBPRICE
    else:
        return get_buff_price(name)


def _clean_doppler_name(name):
    name = name.replace(' - ', '')
    phase = name[name.find(')') + 1:]
    name = name.replace(f'{phase}', '')
    name = name.replace('Doppler', f'Doppler {phase}')

    return name


# Get prices directly from buff163
@on_exception(expo, requests.exceptions.RequestException, max_time=60)
def get_buff_price(name):
    try:
        buff_id = buff_ID_Dict[name]
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


# Use environment variables
token = os.environ['HUB_TOKEN']
repo_name = "buff-prices"

# Connect to Github
github = Github(token)
repository = github.get_user().get_repo(repo_name)

# Get prices from Github repository
# pricempire_prices = json.loads(repository.get_contents("buff_prices.json").decoded_content.decode())
blob = get_blob_content(repository, "main", "buff_prices.json")
b64 = base64.b64decode(blob.content)
pricempire_prices = json.loads(b64.decode())

# Get buff_id from Github repository
blob = get_blob_content(repository, "main", "buff_id.json")
b64 = base64.b64decode(blob.content)
buff_ID_Dict = json.loads(b64.decode())
# buff_ID_Dict = {v: k for k, v in buff_ID_Dict.items()}  # Swapping key value pair
