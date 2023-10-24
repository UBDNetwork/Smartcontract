import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

AMOUNT_IN_USDT = 28_000e6
AMOUNT_OUT_WBTC = 1e8
AMOUNT_OUT_ETH = 20e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def init_market_registry(
    accounts, mockuniv2, 
    dai, usdt, sandbox1, sandbox2, treasury, ubd, 
    markets, wbtc, market_adapter, weth, usdc):
### Old style market info set ## 
    # markets.setMarket(usdt, market_adapter, {'from':accounts[0]})
    # markets.setOracle(usdt, market_adapter, {'from':accounts[0]})
    # markets.setMarket(wbtc, market_adapter, {'from':accounts[0]})
    # markets.setOracle(wbtc, market_adapter, {'from':accounts[0]})
    # markets.setMarket(usdc, market_adapter, {'from':accounts[0]})
    # markets.setOracle(usdc, market_adapter, {'from':accounts[0]})
    # markets.setMarket(dai, market_adapter, {'from':accounts[0]})
    # markets.setOracle(dai, market_adapter, {'from':accounts[0]})
    
    # markets.setMarket(weth, market_adapter, {'from':accounts[0]})
    # markets.setOracle(weth, market_adapter, {'from':accounts[0]})
    # markets.setMarket(ZERO_ADDRESS, market_adapter, {'from':accounts[0]})
    # markets.setOracle(ZERO_ADDRESS, market_adapter, {'from':accounts[0]})

### New style market info set ##
    markets.setMarketParams(usdt, (market_adapter, market_adapter, 0), {'from':accounts[0]})
    markets.setMarketParams(usdc, (market_adapter, market_adapter, 0), {'from':accounts[0]})
    markets.setMarketParams(wbtc, (market_adapter, market_adapter, 0), {'from':accounts[0]})
    markets.setMarketParams(dai, (market_adapter, market_adapter, 0), {'from':accounts[0]})

    markets.setMarketParams(weth, (market_adapter, market_adapter, 0), {'from':accounts[0]})
    markets.setMarketParams(ZERO_ADDRESS, (market_adapter, market_adapter, 0), {'from':accounts[0]})
#################################   
    markets.setSandbox1(sandbox1, {'from':accounts[0]})
    markets.setSandbox2(sandbox2, {'from':accounts[0]})
    markets.setTreasury(treasury, {'from':accounts[0]})
    markets.addERC20AssetToTreasury((wbtc, 50), {'from':accounts[0]})
    #markets.addERC20AssetToTreasury((wbtc, 50), {'from':accounts[0]})
    markets.setTeamAddress(accounts[8], {'from':accounts[0]})


    
   