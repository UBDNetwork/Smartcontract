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
    
    accounts[2].transfer(mockuniv2, 30e18)

    #sandbox has 1% of balance > 1000 usdt - can exchange usdt to ether and wbtc
    tx = sandbox1.topupTreasury({'from':accounts[1]})


#decrease rates of all assets
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
    logging.info(before_wbtc_balance)
    logging.info(before_eth_balance)
    logging.info(before_usdt_balance_sandbox1)
    
    balances_in_usdt = before_eth_balance * mockuniv2.rates(usdt.address, weth.address)[0]*10**usdt.decimals()/10**weth.decimals() + before_wbtc_balance*mockuniv2.rates(usdt.address, wbtc.address)[0]*10**usdt.decimals()/10**wbtc.decimals()

    #prepare shares in usdt - how it have to be
    #50% eth, 50% wbtc
    htb_wbtc_in_usdt = balances_in_usdt*50/100    
    htb_weth_in_usdt = balances_in_usdt*50/100

    #prepare difference in usdt
    diff_in_usdt_wbtc = before_wbtc_balance*mockuniv2.rates(usdt.address, wbtc.address)[0]*10**usdt.decimals()/10**wbtc.decimals() - htb_wbtc_in_usdt
    diff_in_usdt_weth = before_eth_balance *mockuniv2.rates(usdt.address, weth.address)[0]*10**usdt.decimals()/10**weth.decimals() - htb_weth_in_usdt
    logging.info(diff_in_usdt_weth)
    if diff_in_usdt_wbtc < 0:
        diff_in_usdt_wbtc = 0
    if diff_in_usdt_weth < 0:
        diff_in_usdt_weth = 0

    #prepare difference in natural units of measurement
    diff_wbtc = diff_in_usdt_wbtc/mockuniv2.rates(usdt.address, wbtc.address)[0]*10**wbtc.decimals()/10**usdt.decimals()
    diff_weth = diff_in_usdt_weth/mockuniv2.rates(usdt.address, weth.address)[0]*10**weth.decimals()/10**usdt.decimals()

    t = markets.rebalance({"from": accounts[0]})

    #check rebalance
    assert wbtc.balanceOf(treasury) - before_wbtc_balance == 0 
    assert treasury.balance() - before_eth_balance + diff_weth < 2e12 #< 2*1e15
    assert before_usdt_balance_sandbox1 + diff_in_usdt_weth + diff_in_usdt_wbtc - usdt.balanceOf(sandbox1) < 200

#add eth to treasury a little
def test_rebalance_2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    
    accounts[0].transfer(treasury, 1000000000000000)

    before_usdt_balance_sandbox1 = usdt.balanceOf(sandbox1)
    before_wbtc_balance = wbtc.balanceOf(treasury)
    before_eth_balance = treasury.balance()
    
    balances_in_usdt = before_eth_balance * mockuniv2.rates(usdt.address, weth.address)[0]*10**usdt.decimals()/10**weth.decimals() + before_wbtc_balance*mockuniv2.rates(usdt.address, wbtc.address)[0]*10**usdt.decimals()/10**wbtc.decimals()

    #prepare shares in usdt - how it have to be
    #50% eth, 50% wbtc
    htb_wbtc_in_usdt = balances_in_usdt*50/100    
    htb_weth_in_usdt = balances_in_usdt*50/100

    #prepare difference in usdt
    diff_in_usdt_wbtc = before_wbtc_balance*mockuniv2.rates(usdt.address, wbtc.address)[0]*10**usdt.decimals()/10**wbtc.decimals() - htb_wbtc_in_usdt
    diff_in_usdt_weth = before_eth_balance *mockuniv2.rates(usdt.address, weth.address)[0]*10**usdt.decimals()/10**weth.decimals() - htb_weth_in_usdt
    logging.info(diff_in_usdt_weth)
    if diff_in_usdt_wbtc < 0:
        diff_in_usdt_wbtc = 0
    if diff_in_usdt_weth < 0:
        diff_in_usdt_weth = 0

    #prepare difference in natural units of measurement
    diff_wbtc = diff_in_usdt_wbtc/mockuniv2.rates(usdt.address, wbtc.address)[0]*10**wbtc.decimals()/10**usdt.decimals()
    diff_weth = diff_in_usdt_weth/mockuniv2.rates(usdt.address, weth.address)[0]*10**weth.decimals()/10**usdt.decimals()

    markets.rebalance({"from": accounts[0]})

    #check rebalance
    assert wbtc.balanceOf(treasury) - before_wbtc_balance == 0 
    assert treasury.balance() - before_eth_balance + diff_weth < 9e11 #< 2*1e15
    assert before_usdt_balance_sandbox1 + diff_in_usdt_weth + diff_in_usdt_wbtc - usdt.balanceOf(sandbox1) < 1000

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
    before_wbtc_balance = wbtc.balanceOf(treasury)
    before_eth_balance = treasury.balance()
    tx = sandbox1.topupTreasury({'from':accounts[1]})

    #exchange 1% usdt to 50% ETH and 50% WBTC
    assert before_wbtc_balance + (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, wbtc.address)[0])*10**wbtc.decimals()/10**usdt.decimals() - wbtc.balanceOf(treasury) < 100 #2e7
    assert before_eth_balance + (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, weth.address)[0])*10**weth.decimals()/10**usdt.decimals() - treasury.balance() < 3e11 #4e17
    assert before_usdt_sandbox *99/100 - usdt.balanceOf(sandbox1.address) < 100

    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))

def test_topup_sandbox2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth):

    #bullrun
    mockuniv2.setRate(usdt.address, wbtc.address, (160000000000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (80000000000, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 160000000000))
    mockuniv2.setRate(weth.address, usdt.address, (1,  80000000000))

    mockuniv2.setRate(dai.address, wbtc.address, (160000000000, 1))
    mockuniv2.setRate(dai.address, weth.address, (80000000000, 1))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 160000000000))
    mockuniv2.setRate(weth.address, dai.address, (1,  80000000000))

    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))

    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()

    #markets.topupSandBox2()
    tx = sandbox2.topupSandBox2( {'from':accounts[0]})

    #1/3 of amount
    wbtc_to_dai_amount = before_wbtc_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    eth_to_dai_amount = before_eth_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/(100*markets.PERCENT_DENOMINATOR())

    logging.info('wbtc_to_dai_amount = {}'.format(wbtc_to_dai_amount))
    logging.info('eth_to_dai_amount = {}'.format(eth_to_dai_amount))
    logging.info('eth_balance_market = {}'.format(markets.balance()))

    dai_amount_calc = wbtc_to_dai_amount*mockuniv2.rates(wbtc.address, dai.address)[1]*10**dai.decimals()/10**wbtc.decimals() + eth_to_dai_amount*mockuniv2.rates(weth.address, dai.address)[1]*10**dai.decimals()/10**weth.decimals()
    logging.info('dai_amount_calc = {}'.format(dai_amount_calc))

    logging.info(mockuniv2.getAmountsOut(eth_to_dai_amount, [weth.address,dai.address]))
    logging.info(mockuniv2.getAmountsOut(wbtc_to_dai_amount, [wbtc.address,dai.address]))

    assert dai_amount_calc - dai.balanceOf(sandbox2) < 1e14
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount - wbtc_to_dai_amount
    assert before_eth_treasury_amount - eth_to_dai_amount - treasury.balance()   < 1000



    


