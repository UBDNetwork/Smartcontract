import pytest
import logging
import math
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1005e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
def test_hackECR20_reentrancy(accounts, ubd, sandbox1, usdt, hackERC20, markets, market_adapter, mockuniv2, sandbox2, wbtc, weth, usdc, dai, treasury):
    logging.info('!!!!!!!!!!!!!!!!!   REENTRANCY attack    !!!!!!!!!!!!!!!')
    sandbox1.setUBDToken(ubd, {'from':accounts[0]})
    sandbox1.setBeneficiary(accounts[1], {'from':accounts[0]})

    init_market_registry(accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury, ubd, markets, wbtc, market_adapter, weth, usdc)

    mockuniv2.setRate(usdt.address, hackERC20.address, (1, 1))
    mockuniv2.setRate(hackERC20.address, usdt.address, (1, 1))
    #markets.setMarketParams(hackERC20, (market_adapter, market_adapter, 0), {'from':accounts[0]})
    
    hackERC20.approve(markets, PAY_AMOUNT*1000, {'from':accounts[0]})
    
    chain.sleep(10)
    
    tx = sandbox1.swapExactInput(
        hackERC20, 
        PAY_AMOUNT,
        0,
        0,
        {'from':accounts[0]}
    )
    logging.info(tx.return_value)
    logging.info(tx.events)
    logging.info(accounts[0])
    logging.info(markets.address)
    logging.info(sandbox1)
    logging.info(hackERC20.address)

    logging.info(hackERC20.balanceOf(accounts[0]))
    logging.info(ubd.balanceOf(accounts[0]))