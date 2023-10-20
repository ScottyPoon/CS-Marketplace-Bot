
# CS Marketplace Bot

## Basic Overview
A public version of a command line bot that monitors incoming websocket messages to buy items that meet the required return on investment percent and notify you when an item has been bought. 

## Features
* **Automated Purchases**: When an item meets the ROI criteria, the bot automatically executes the purchase process.
* **Item Scraping**: Fetch a list of items with the ROI, price and liquidity of each item.
* **Notification System**: You will receive detailed notifications via Discord whenever the bot successfully buys an item.
* **Retrieve Wallet Balance**: Fetch your current wallet balance.
* **Flexible Withdrawal Settings**:
  - Set a minimum ROI for item withdrawals
  - Set a minimum or maximum price threshold for item withdrawals
  - Set a minimum liquidity threshold for item withdrawals
  - Set a specific float range for item withdrawals
  - Set a blacklist of item(s) you don't want to withdraw
  - Use session cookie for authentication – no need for username and password.
  - Set your local timezone for timestamps. 

## Getting Started
To get a local copy up and running follow these simple example steps.

### Prerequisites
Required Modules
* discord.py
* requests
* websockets
* pytz

### Installation
To build and run this application locally, you'll need latest versions of Git installed on your computer. From your command line:
1. Clone the repo
```bash
$ git clone https://github.com/ScottyPoon/
```
2. Install required libraries
```bash
$ pip install -r requirements.txt
```
3. Run the script
```bash
$ python main.py
```

### Installation
Before running the script, you need to configure the following environment variables:

**DISCORD_TOKEN**: Set this variable to the value of the token of your Discord bot to recieve notifications from.

**LIQUIDITY**: Set this variable to the minimum liquidity threshold you want to bot to withdraw items at.

**MAX_PRICE**: Set this variable to the maximum price threshold you want to bot to withdraw items at.

**MIN_PRICE**: Set this variable to the minimum price threshold you want to bot to withdraw items at.

**RATIO**: Set this variable to your desired ROI/price per coin.

**SESSION_COOKIE**: Set this variable to the value of your session cookie.

**ADDITIONAL_BLACKLIST**: Set this variable to the name of the item(s) you want to blacklist in CSV format.

### Heroku Deployment

The program can be deployed locally or via Heroku, using Heroku you can setup a scheduler to withdraw items at a desired time interval. For the best results with the lowest latency to the marketplace deploy the app on the United States region

Set the environmental variables mentioned in the Configuration section:
* KEY ```SESSION_COOKIE``` VALUE ```your authentication cookie``` This can be found by going into the Browser's Developer Console (F12) > Cookies > corresponding value
* KEY ```DISCORD_TOKEN``` VALUE ```your Discord bot access token```
* KEY ```LIQUIDITY``` VALUE ```the minimum liquidity threshold```
* KEY ```MAX_PRICE``` VALUE ```the maximum price threshold```
* KEY ```MIN_PRICE``` VALUE ```the minimum price threshold```
* KEY ```RATIO``` VALUE ```your desired ROI/price per coin```
* KEY ```ADDITIONAL_BLACKLIST``` VALUE ```the blacklist of item(s) in CSV format```

Create a Procfile:
* inside the Procfile write ```worker: python script.py```

Running the app:
* Run the app by writing ```python main.py``` inside of the Heroku console.

Automatic running at certain times:
* Install the Heroku Scheduler add-on to run the ```python main.py``` command to your desired time interval.

## Authors

* **Scotty Poon** - *Initial work* - [ScottyPoon](https://github.com/ScottyPoon)