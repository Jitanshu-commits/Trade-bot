import logging
import os
import argparse
from pprint import pprint

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv

#  Configuration 
def setup_logging():
    """Configures logging to output to both file and console."""
    logger = logging.getLogger("binance_bot")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        file_handler = logging.FileHandler("bot.log")
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger

logger = setup_logging()

# Bot Class 
class BasicBot:
    """A simplified trading bot for Binance (using python-binance v0.7.x)."""

    def __init__(self, api_key, api_secret, testnet=True):
        """Initializes the Bot."""
        self.client = Client(api_key, api_secret)
        
        if testnet:
            #  FINAL FIX: Added /fapi to the URL to fix the 404 error 
            self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
            logger.info(f"Client configured for Futures Testnet: {self.client.FUTURES_URL}")
        
        logger.info("Bot initialized.")
        self.check_connection()

    def check_connection(self):
        """Checks API connection and credentials."""
        try:
            #  FINAL FIX: Used the correct function name 'futures_account()' 
            self.client.futures_account() 
            logger.info("Successfully connected to Binance Futures API.")
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"API Connection Error: {e.status_code} - {e.message}")
            raise

    def get_account_balance(self, asset='USDT'):
        """Retrieves the balance for a specific asset in the futures account."""
        try:
            balances = self.client.futures_account_balance()
            for balance in balances:
                if balance['asset'] == asset:
                    logger.info(f"Account balance for {asset}: {balance['balance']}")
                    return balance
            logger.warning(f"Asset {asset} not found in account balance.")
            return None
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Error fetching account balance: {e}")
            return None

    def _place_order(self, order_details):
        """Internal method to place an order and handle logging/errors."""
        try:
            logger.info(f"Placing order with details: {order_details}")
            order = self.client.futures_create_order(**order_details)
            logger.info("Order placed successfully.")
            logger.debug(f"API Response: {order}")
            return order
        except BinanceAPIException as e:
            logger.error(f"API Error placing order: {e.status_code} - {e.message}")
        except BinanceRequestException as e:
            logger.error(f"Request Error placing order: {e.status_code} - {e.message}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        return None

    def place_market_order(self, symbol, side, quantity):
        """Places a market order."""
        details = {
            "symbol": symbol,
            "side": side,
            "type": Client.ORDER_TYPE_MARKET,
            "quantity": quantity
        }
        return self._place_order(details)

    def place_limit_order(self, symbol, side, quantity, price):
        """Places a limit order."""
        details = {
            "symbol": symbol,
            "side": side,
            "type": Client.ORDER_TYPE_LIMIT,
            "quantity": quantity,
            "price": price,
            "timeInForce": Client.TIME_IN_FORCE_GTC
        }
        return self._place_order(details)

    def place_stop_limit_order(self, symbol, side, quantity, price, stop_price):
        """Places a stop-limit order."""
        details = {
            "symbol": symbol,
            "side": side,
            "type": Client.ORDER_TYPE_STOP_MARKET,
            "quantity": quantity,
            "price": price,
            "stopPrice": stop_price,
            "timeInForce": Client.TIME_IN_FORCE_GTC
        }
        return self._place_order(details)

# Command-Line Interface 
def main():
    """Main function to run the CLI."""
    parser = argparse.ArgumentParser(
        description="A simplified CLI trading bot for Binance Futures Testnet.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logger.error("API key and/or secret not found in .env file. Exiting.")
        return

    try:
        bot = BasicBot(api_key, api_secret, testnet=True)
    except Exception:
        logger.error("Failed to initialize bot. Please check connection and credentials.")
        return

    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)
    status_parser = subparsers.add_parser("status", help="Check API connection and account balance.")
    order_parser = subparsers.add_parser("order", help="Place a new order.")
    order_parser.add_argument("--symbol", required=True, help="Trading symbol (e.g., BTCUSDT)")
    order_parser.add_argument("--side", required=True, choices=['BUY', 'SELL'], help="Order side")
    order_parser.add_argument("--type", required=True, choices=['MARKET', 'LIMIT', 'STOP_LIMIT'], help="Order type")
    order_parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    order_parser.add_argument("--price", type=float, help="Limit price (required for LIMIT and STOP_LIMIT)")
    order_parser.add_argument("--stop-price", type=float, help="Stop price (required for STOP_LIMIT)")

    args = parser.parse_args()

    if args.command == "status":
        print("\n--- Account Status ---")
        bot.get_account_balance(asset='USDT')
        print("----------------------\n")

    elif args.command == "order":
        if args.type in ['LIMIT', 'STOP_LIMIT'] and not args.price:
            parser.error("--price is required for LIMIT and STOP_LIMIT orders.")
        if args.type == 'STOP_LIMIT' and not args.stop_price:
            parser.error("--stop-price is required for STOP_LIMIT orders.")

        print("\n--- Placing Order ---")
        result = None
        if args.type == 'MARKET':
            result = bot.place_market_order(args.symbol, args.side.upper(), args.quantity)
        elif args.type == 'LIMIT':
            result = bot.place_limit_order(args.symbol, args.side.upper(), args.quantity, args.price)
        elif args.type == 'STOP_LIMIT':
            result = bot.place_stop_limit_order(args.symbol, args.side.upper(), args.quantity, args.price, args.stop_price)

        if result:
            print("✅ Order placed successfully!")
            print("\n--- Order Details ---")
            pprint(result)
            print("---------------------\n")
        else:
            print("❌ Order placement failed. Check logs for details.")

if __name__ == "__main__":
    main()