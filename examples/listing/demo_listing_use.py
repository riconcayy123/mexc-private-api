# Full automated Listing Bot

import json
from typing import Dict, Any, Optional, List
import aiohttp
import asyncio
import logging

from tg_client import TelegramParser

from mexc_python.mexcpy.api import MexcFuturesAPI
from mexc_python.mexcpy.mexcTypes import CreateOrderRequest, OpenType, OrderSide, OrderType

from mexc_python.mexc_trade_lib import MexcTrader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def load_js_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def create_mexc_api(config) -> MexcFuturesAPI:
    proxy_data = config['proxy']
    return MexcFuturesAPI(
        token=config['web_token'],
        testnet=False,
        proxy=f"{proxy_data['ip']}:{proxy_data['port']}",
        proxy_auth=aiohttp.BasicAuth(proxy_data['user'], proxy_data['pass']),
        proxy_type=proxy_data['type']
    )

def create_mexc_trader(config_path: str) -> MexcTrader:
    config = load_js_config(config_path)
    mexc_api = create_mexc_api(config)
    return MexcTrader(mexc_api)

async def main():
    try:
        # example for 1 account
        # But it's possible to use multiple accounts for listing trading
        mexc_trader = create_mexc_trader("account_config.js")
        mexc_trader.setup_listing_config("listing_config.js")
        tg_parser = TelegramParser(mexc_trader, 'tg_config.yaml')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(tg_parser.run())
    except KeyboardInterrupt:
        logger.info("-- Bot stopped")
    except Exception as e:
        logger.error(f"-- Error in main cycle: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    
