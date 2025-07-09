# Simplified Binance Futures Trading Bot

This is a Python-based command-line trading bot for interacting with the Binance Futures Testnet (USDT-M). It allows users to check account status and place Market, Limit, and Stop-Limit orders.

## Features

- **Reusable Class:** `BasicBot` class encapsulates all API interaction logic.
- **Multiple Order Types:** Supports `MARKET`, `LIMIT`, and `STOP_LIMIT` orders.
- **Robust CLI:** Easy-to-use command-line interface powered by `argparse`.
- **Secure:** Uses a `.env` file to manage API credentials, keeping them out of the source code.
- **Comprehensive Logging:** Logs all actions, API responses, and errors to `bot.log` and the console.
- **Testnet Focused:** Pre-configured for the Binance Futures Testnet.

## Setup

### 1. Prerequisites

- Python 3.7+
- A Binance Futures Testnet account. You can register here: [Binance Futures Testnet](https://testnet.binancefuture.com/)

### 2. Get API Credentials

1.  Log in to your Binance Futures Testnet account.
2.  Click on **"API Key"** at the bottom of the page.
3.  Generate a new API Key. Make sure to save both the **API Key** and the **Secret Key**.

### 3. Installation

1.  Clone this repository or download the files.
2.  Create and activate a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a `.env` file in the project root and add your API credentials:
    ```
    # .env
    BINANCE_API_KEY="YOUR_TESTNET_API_KEY"
    BINANCE_API_SECRET="YOUR_TESTNET_API_SECRET"
    ```

## Usage

All commands are run from your terminal.

### Check Account Status

To check your API connection and USDT balance:

```bash
python trading_bot.py status
