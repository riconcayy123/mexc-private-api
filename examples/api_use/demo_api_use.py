import json
from typing import Dict, Any, Optional, List
import aiohttp

from mexc_python.mexcpy.helpers import sleep
from mexc_python.mexcpy.api import MexcFuturesAPI
from mexc_python.mexcpy.mexcTypes import CreateOrderRequest, OpenType, OrderSide, OrderType


def load_js_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def create_mexc_api(config_path) -> MexcFuturesAPI:
    config = load_js_config(config_path)
    proxy_data = config['proxy']
    return MexcFuturesAPI(
        token=config['web_token'],
        testnet=False,
        proxy=f"{proxy_data['ip']}:{proxy_data['port']}",
        proxy_auth=aiohttp.BasicAuth(proxy_data['user'], proxy_data['pass']),
        proxy_type=proxy_data['type']
    )

async def example1(api):
    # open and close position
    # 200   -- position size (margin x leverage)
    # 35    -- leverage 
    ticker = "BTC_USDT"
    position_volume = 200
    leverage = 35

    await api.create_market_order(ticker, OrderSide.OpenLong, position_volume, leverage)
    await sleep(2100) # 2.1 seconds
    await api.create_market_order(ticker, OrderSide.CloseLong, position_volume, leverage)

async def example2(api):
    # open and close 50% position two times
    # 200   -- position size (margin x leverage)
    # 35    -- leverage 
    ticker = "BTC_USDT"
    position_volume = 200
    leverage = 35

    order_open = await api.create_market_order(ticker, OrderSide.OpenLong, position_volume, leverage)
    order_id = order_open.data.orderId

    await sleep(600000) # 600 seconds

    result = await api.get_order_by_order_id(order_id)
    current_position_volume = result.data.vol

    order_close = await api.create_market_order(ticker, OrderSide.CloseShort, current_position_volume/2, leverage)
    await sleep(5000)
    order_close = await api.create_market_order(ticker, OrderSide.CloseShort, current_position_volume/2, leverage)

async def example3(api):
    # open position, setup TP and SL.
    # 200   -- position size (margin x leverage)
    # 35    -- leverage 
    ticker = "BTC_USDT"
    position_volume = 200
    leverage = 35
    tp_perc = 20 # 20%
    sl_perc = 10 # 10%

    order = await api.create_market_order(ticker, OrderSide.OpenLong, position_volume, leverage)
    if not order.success:
        print(f"Failed to open order: {order}")
        return 

    order_response = await api.get_order_by_order_id(str(order.data.orderId))
    entry_price = order_response.data.price

    take_profit_price = round_to_tick(entry_price * (1 + tp_perc / 100))
    stop_loss_price = round_to_tick(entry_price * (1 - sl_perc / 100) )

    print(f"entry_price: {entry_price},\ntakeProfitPrice: {take_profit_price}\nstopLossPrice: {stop_loss_price}")

    close_side = OrderSide.CloseLong
    # create limit (not market) take profit
    await api.create_order(CreateOrderRequest(
        symbol=symbol,
        side=close_side,
        vol=vol,
        leverage=leverage,
        price=take_profit_price,
        openType=OpenType.Isolated,
        type=OrderType.PriceLimited,
        
    ))
    await api.create_stop_loss(symbol, close_side, vol, stop_loss_price)

    await sleep(2500)
    # close position
    await api.cancel_order_by_external_oid(symbol, str(order.data.orderId))


async def demo(api):
    await example1(api)
    await example2(api)
    await example3(api)

if __name__ == "__main__":
    mexc_api = create_mexc_api("config.js")
    await demo(mexc_api)