import random
import json

#Fix gen id
def generateID():
    hex_digits = "0123456789abcdef"
    # Use a random 16-byte (128-bit) array
    rand_bytes = bytearray(random.getrandbits(8) for _ in range(16))
    # Apply bit masking to the first 5 bytes
    rand_bytes[0] = rand_bytes[0] & 15  # Apply 00001111 bitmask
    rand_bytes[1] = rand_bytes[1] & 3  # Apply 00000011 bitmask
    # Generate a hex string from the bytes
    hex_str = ''.join([hex_digits[b >> 4] + hex_digits[b & 15] for b in rand_bytes])
    # Combine with prefix
    return "1e7{}-1e3{}-4e3{}-8e3{}-1e11{}".format(
        hex_str[:8], hex_str[8:12], hex_str[12:16], hex_str[16:20], hex_str[20:]
    )


async def subscribe_to_create_trade(websocket):
    subscription_message = {
        "id": generateID(),
        "type": "subscribe",
        "payload": {
            "variables": {},
            "extensions": {},
            "operationName": "OnCreateTrade",
            "query": "subscription OnCreateTrade($userId: ID) {\n  createTrade(userId: $userId) {\n    trade {\n      "
                     "id\n      markupPercent\n      totalValue\n      createdAt\n      tradeItems {\n        id\n        marketName\n "
                     "       value\n        customValue\n        itemVariant {\n          value\n          "
                     "displayValue\n        }\n        markupPercent\n        stickers {\n          value\n          "
                     "imageUrl\n          brand\n          name\n          color\n          wear\n        }\n      "
                     "}\n      avgPaintWear\n      hasStickers\n    }\n  }\n}\n "
        }
    }

    await websocket.send(json.dumps(subscription_message))


async def subscribe_to_create_trade_rarity(websocket):
    subscription_message = {
        "id": generateID(),
        "type": "subscribe",
        "payload": {
            "variables": {},
            "extensions": {},
            "operationName": "OnCreateTrade",
            "query": "subscription OnCreateTrade($userId: ID) {\n  createTrade(userId: $userId) {\n    trade {\n      "
                     "id\n      markupPercent\n      totalValue\n      createdAt\n      tradeItems {\n        id\n        marketName\n"
                     "        value\n        customValue\n        itemVariant {\n          displayValue\n          rarity\n        }\n"
                     "        markupPercent\n        stickers {\n          value\n          imageUrl\n          brand\n          name\n"
                     "          color\n          wear\n        }\n      }\n      avgPaintWear\n      hasStickers\n    }\n  }\n}\n"
        }
    }

    await websocket.send(json.dumps(subscription_message))




async def subscribe_to_join_trade2(websocket, trade_id):
    subscription_message = {
        "id": generateID(),
        "type": "subscribe",
        "payload": {
            "variables": {
                "input": {
                    "tradeIds": trade_id,
                    "recaptcha": ""
                }
            },
            "extensions": {},
            "operationName": 'JoinTrades',
            "query": 'mutation JoinTrades($input: JoinTradesInput!) {\n  joinTrades(input: $input) {\n    trades {\n  '
                     '    id\n      status\n      totalValue\n      updatedAt\n      expiresAt\n      withdrawer {\n  '
                     '      id\n        steamId\n        avatar\n        displayName\n        steamDisplayName\n      '
                     '  __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n '
        }
    }
    await websocket.send(json.dumps(subscription_message))


async def subscribe_to_join_trade(websocket, trade_id):
    subscription_message = {
        "id": generateID(),
        "type": "subscribe",
        "payload": {
            "variables": {
                "input": {
                    "tradeIds": trade_id,
                    "recaptcha": ""
                }
            },
            "extensions": {},
            "operationName": 'JoinTrades',
            "query": 'mutation JoinTrades($input: JoinTradesInput!) {\n  joinTrades(input: $input) {\n    trades {\n      '
                     'id\n      status\n      totalValue\n      updatedAt\n    }\n  }\n}\n'
        }
    }
    await websocket.send(json.dumps(subscription_message))


async def subscribe_to_list_item(websocket, items):
    query_variables = ""
    create_trade_queries = ""

    for i, (itemVariantId, value) in enumerate(items):
        input_variable_name = f"input{i}"
        query_variables += f"${input_variable_name}: CreateTradeInput!, "
        create_trade_queries += f"  trade{i}: createTrade(input: ${input_variable_name}) {{\n    trade {{\n      ...Trade\n      __typename\n    }}\n    __typename\n  }}\n"

    query = f"mutation CreateTrades({query_variables[:-2]}) {{\n{create_trade_queries}}}\n\nfragment Trade on Trade {{\n  id\n  status\n  steamAppName\n  cancelReason\n  canJoinAfter\n  markupPercent\n  createdAt\n  depositor {{\n    id\n    steamId\n    avatar\n    displayName\n    steamDisplayName\n    __typename\n  }}\n {{\n    id\n    percentageReward\n    maxBalance\n    __typename\n  }}\n  expiresAt\n  withdrawerSteamTradeUrl\n  customValue\n  withdrawer {{\n    id\n    steamId\n    avatar\n    displayName\n    steamDisplayName\n    __typename\n  }}\n  totalValue\n  updatedAt\n  tradeItems {{\n    id\n    marketName\n    value\n    customValue\n    itemVariant {{\n      ...ItemVariant\n      __typename\n    }}\n    markupPercent\n    __typename\n  }}\n  trackingType\n  suspectedTraderCanJoinAfter\n  joinedAt\n  __typename\n}}\n\nfragment ItemVariant on ItemVariant {{\n  id\n  itemId\n  name\n  brand\n  iconUrl\n  value\n  currency\n  displayValue\n  exchangeRate\n  shippingCost\n  usable\n  obtainable\n  withdrawable\n  depositable\n  externalId\n  type\n  category {{\n    id\n    name\n    __typename\n  }}\n  color\n  size\n  rarity\n  availableAssets {{\n    steamAssetId\n    availableAt\n    __typename\n  }}\n  purchasable\n  totalRequested\n  totalAvailable\n  totalFulfilled\n  totalUnfulfilled\n  createdAt\n  __typename\n}}\n"

    subscription_message = {
        "id": "f4af2941-4e79-42ba-a4fa-ac04c8af86f6",
        "type": "subscribe",
        "payload": {
            "variables": {},
            "extensions": {},
            "operationName": "CreateTrades",
            "query": query
        }
    }

    for i, (itemVariantId, value) in enumerate(items):
        input_variable_name = f"input{i}"
        subscription_message["payload"]["variables"][input_variable_name] = {
            "promoCode": None,
            "tradeItems": [
                {
                    "itemVariantId": itemVariantId,
                    "value": value
                }
            ],
            "recaptcha": "03AL8dmw8o0OH1ocYmya_H9r0D4Lre9NBFnFQTEsFuoMm7JPA7qqEOQpbP9CB6AKQ3E3yUFxIEk6jxkJyeiWNuFcPIC_CPZXC0535gWeVbdfZbB1mwOMoSiu"
        }

    await websocket.send(json.dumps(subscription_message))
    response3 = json.loads(await websocket.recv())
    print('3', response3)


async def subscribe_to_cancel_trade(websocket, trade_ids):
    for i, tradeID in enumerate(trade_ids):
        subscription_message = {
            "id": generateID(),
            "type": "subscribe",
            "payload": {
                "variables": {
                    f"input{i}": {
                        "tradeId": tradeID
                    }
                },
                "extensions": {},
                "operationName": "CancelTrades",
                "query": f"mutation CancelTrades($input{i}: CancelTradeInput!) {{\n  trade{i}: cancelTrade(input: $input{i}) {{\n    trade {{\n      ...TradeCancel\n      __typename\n    }}\n    __typename\n  }}\n}}\n\nfragment TradeCancel on Trade {{\n  id\n  cancelReason\n  expiresAt\n  status\n  totalValue\n  __typename\n}}\n"
            }
        }
        await websocket.send(json.dumps(subscription_message))


async def subscribe_to_onupdatetrade(websocket, userID):
    if not userID:
        variables = {}
    else:
        variables = {"userId": userID}
    subscription_message_id = generateID()
    subscription_message = {
        "id": subscription_message_id,
        "type": "subscribe",
        "payload": {
            "variables": variables,
            "extensions": {},
            "operationName": "OnUpdateTrade",
            "query": "subscription OnUpdateTrade($status: TradeStatus, $userId: ID) {\n  updateTrade(status: $status, userId: $userId) {\n    trade {\n      ...Trade\n    }\n  }\n}\n\nfragment Trade on Trade {\n  id\n  status\n  markupPercent\n  depositor {\n    id\n    steamId\n    avatar\n    displayName\n    steamDisplayName\n    online\n  }\n  depositorLastActiveAt\n  withdrawerSteamTradeUrl\n  customValue\n  withdrawer {\n    id\n    steamId\n    avatar\n    displayName\n    steamDisplayName\n  }\n  totalValue\n  updatedAt\n  tradeItems {\n    marketName\n    customValue\n    itemVariant {\n      displayValue\n      color\n    }\n    markupPercent\n    stickers {\n      ...SimpleSticker\n    }\n  }\n  joinedAt\n  avgPaintWear\n  hasStickers\n}\n\nfragment SimpleSticker on TradeItemSticker {\n  imageUrl\n  wear\n}\n"
        }
    }
    await websocket.send(json.dumps(subscription_message))


async def subscribe_to_OnUpdateTradeLong(websocket, userID):
    if not userID:
        variables = {}
    else:
        variables = {"userId": userID}
    subscription_message_id = generateID()
    subscription_message = {
        "id": subscription_message_id,
        "type": "subscribe",
        "payload": {
            "variables": variables,
            "extensions": {},
            "operationName": "OnUpdateTrade",
            "query": "subscription OnUpdateTrade($status: TradeStatus, $userId: ID) {\n  updateTrade(status: $status, userId: $userId) {\n    trade {\n      ...Trade\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment Trade on Trade {\n  id\n  status\n  steamAppName\n  cancelReason\n  canJoinAfter\n  markupPercent\n  createdAt\n  depositor {\n    id\n    steamId\n    avatar\n    displayName\n    steamDisplayName\n    online\n    __typename\n  }\n  depositorLastActiveAt\n  promoCode {\n    id\n    percentageReward\n    maxBalance\n    __typename\n  }\n  expiresAt\n  withdrawerSteamTradeUrl\n  customValue\n  withdrawer {\n    id\n    steamId\n    avatar\n    displayName\n    steamDisplayName\n    __typename\n  }\n  totalValue\n  updatedAt\n  tradeItems {\n    id\n    marketName\n    value\n    customValue\n    itemVariant {\n      ...ItemVariant\n      __typename\n    }\n    markupPercent\n    stickers {\n      ...SimpleSticker\n      __typename\n    }\n    steamExternalAssetId\n    __typename\n  }\n  trackingType\n  suspectedTraderCanJoinAfter\n  joinedAt\n  avgPaintWear\n  hasStickers\n  __typename\n}\n\nfragment ItemVariant on ItemVariant {\n  id\n  itemId\n  name\n  brand\n  iconUrl\n  value\n  currency\n  displayValue\n  exchangeRate\n  shippingCost\n  usable\n  obtainable\n  withdrawable\n  depositable\n  externalId\n  type\n  category {\n    id\n    name\n    __typename\n  }\n  color\n  size\n  rarity\n  availableAssets {\n    steamAssetId\n    availableAt\n    __typename\n  }\n  purchasable\n  totalRequested\n  totalAvailable\n  totalFulfilled\n  totalUnfulfilled\n  createdAt\n  deletedAt\n  __typename\n}\n\nfragment SimpleSticker on TradeItemSticker {\n  value\n  imageUrl\n  brand\n  name\n  color\n  wear\n  __typename\n}\n"
        }
    }
    await websocket.send(json.dumps(subscription_message))



#print(generateID())