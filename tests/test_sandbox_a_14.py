import pytest
import logging
import math
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1005e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def test_usdt_to_ubd_100k_1(accounts, ubd, sandbox1, usdt):
    sandbox1.setUBDToken(ubd, {'from':accounts[0]})
    sandbox1.setBeneficiary(accounts[1], {'from':accounts[0]})
    chain.sleep(10)
    usdt.approve(sandbox1, PAY_AMOUNT * 101, {'from':accounts[0]})
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT * 101,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    
    assert tx.return_value == MINT_UBD_AMOUNT * 101


def test_topup_treasury_from_sandbox1(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    logging.info('!!!!!!!!!!!!!!!!!   topup treasury from sandbox1 !!!!!!!!!!!!!!!')
    
    init_market_registry(accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury, ubd, markets, wbtc, market_adapter, weth, usdc)
    
    accounts[1].transfer(mockuniv2, 50e18)

    #sandbox has 1% of balance > 1000 usdt - can exchange usdt to ether and wbtc
    tx = sandbox1.topupTreasury({'from':accounts[1]})


#decrease rates of all assets in two time 
def test_rebalance_1(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    
    #change rates
    mockuniv2.setRate(usdt.address, wbtc.address, (14000, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 14000))
    mockuniv2.setRate(usdt.address, weth.address, (700, 1))
    mockuniv2.setRate(weth.address, usdt.address, (1, 700))

    before_usdt_balance_sandbox1 = usdt.balanceOf(sandbox1)
    before_wbtc_balance = wbtc.balanceOf(treasury)
    before_eth_balance = treasury.balance()
   
    markets.rebalance({"from": accounts[0]})

    #check rebalance
    assert wbtc.balanceOf(treasury) - before_wbtc_balance == 0 
    assert treasury.balance() - before_eth_balance == 0
    assert before_usdt_balance_sandbox1 - usdt.balanceOf(sandbox1) == 0 #diff_in_usdt_weth + diff_in_usdt_wbtc

#add eth to treasury a little
def test_rebalance_2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    
    accounts[0].transfer(treasury, 1000000000000000)

    before_usdt_balance_sandbox1 = usdt.balanceOf(sandbox1)
    before_wbtc_balance = wbtc.balanceOf(treasury)
    before_eth_balance = treasury.balance()
   
    markets.rebalance({"from": accounts[0]})

    #check rebalance
    assert wbtc.balanceOf(treasury) - before_wbtc_balance == 0 
    assert treasury.balance() - before_eth_balance == 0
    assert before_usdt_balance_sandbox1 - usdt.balanceOf(sandbox1) == 0

#usdt billions
def test_usdt_to_ubd_billions(accounts, ubd, sandbox1, usdt):
    usdt.approve(sandbox1, PAY_AMOUNT * 1000000000, {'from':accounts[0]})
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT * 1000000000,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    
    assert tx.return_value == MINT_UBD_AMOUNT * 1000000000

def test_topup_treasury_from_sandbox1_1(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    chain.sleep(sandbox1.TREASURY_TOPUP_PERIOD() + 10)
    mockuniv2.setRate(usdt.address, wbtc.address, (800000000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (400000000, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 800000000))
    mockuniv2.setRate(weth.address, usdt.address, (1,  400000000))

    mockuniv2.setRate(dai.address, wbtc.address, (800000000, 1))
    mockuniv2.setRate(dai.address, weth.address, (400000000, 1))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 800000000))
    mockuniv2.setRate(weth.address, dai.address, (1,  400000000))

    #sandbox has 1% of balance > 1000 usdt - can exchange usdt to ether and wbtc
    before_usdt_sandbox = usdt.balanceOf(sandbox1.address)
    tx = sandbox1.topupTreasury({'from':accounts[1]})

    #exchange 1% usdt to 50% ETH and 50% WBTC
    logging.info(treasury.balance())
    logging.info(before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, weth.address)[0]*10**weth.decimals()/10**usdt.decimals())
    assert wbtc.balanceOf(treasury) - (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, wbtc.address)[0])*10**wbtc.decimals()/10**usdt.decimals() <= 2e7
    assert treasury.balance() - (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, weth.address)[0])*10**weth.decimals()/10**usdt.decimals()  < 4e17



    


