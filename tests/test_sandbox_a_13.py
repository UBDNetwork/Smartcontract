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

#decrease rate of one asset
def test_rebalance_1(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    
    #change rates
    mockuniv2.setRate(usdt.address, wbtc.address, (20000, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 20000))

    with reverts('Ownable: caller is not the owner'):
        markets.rebalance({"from": accounts[1]})
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

    logging.info('Diff_in_stable_wbtc: {}'.format(diff_in_usdt_wbtc))
    logging.info('Diff_in_stable__eth: {}'.format(diff_in_usdt_weth))

    #prepare difference in natural units of measurement
    diff_wbtc = diff_in_usdt_wbtc/mockuniv2.rates(usdt.address, wbtc.address)[0]*10**wbtc.decimals()/10**usdt.decimals()
    diff_weth = diff_in_usdt_weth/mockuniv2.rates(usdt.address, weth.address)[0]*10**weth.decimals()/10**usdt.decimals()
    logging.info('Diff_in_wbtc: {}'.format(diff_wbtc))
    logging.info('Diff_in__eth: {}'.format(Wei(diff_weth).to('ether')))

    
    logging.info(
        '\n Before rebalancing ...'
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{} ({})'
        '\ntreasury.balance(eth):{} ({})'
        '\ngetBalanceInStableUnits: {}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury) / 1e8, markets.getAmountOut(wbtc.balanceOf(treasury), [wbtc, usdt]),
            Wei(treasury.balance()).to('ether'), markets.getAmountOut(treasury.balance(), [weth, usdt]),
            Wei(markets.getBalanceInStable18(treasury, [wbtc, weth])).to('ether')
    ))
    t = markets.rebalance({"from": accounts[0]})
    logging.info('Actual transfer to sandbox1 {}'.format(
        t.events['Transfer'][1]['value'])
    )
    logging.info(
        '\n After rebalancing ...'
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{} ({})'
        '\ntreasury.balance(eth):{} ({})'
        '\ngetBalanceInStableUnits: {}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury) / 1e8, markets.getAmountOut(wbtc.balanceOf(treasury), [wbtc, usdt]),
            Wei(treasury.balance()).to('ether'), markets.getAmountOut(treasury.balance(), [weth, usdt]),
            Wei(markets.getBalanceInStable18(treasury, [wbtc, weth])).to('ether')
    ))
    logging.info(treasury.balance())
    logging.info(usdt.balanceOf(sandbox1))

    #check rebalance
    assert wbtc.balanceOf(treasury) - before_wbtc_balance == 0 
    assert treasury.balance() - before_eth_balance + diff_weth < 8e11 #2*1e15
    assert before_usdt_balance_sandbox1 + diff_in_usdt_weth + diff_in_usdt_wbtc - usdt.balanceOf(sandbox1) < 2000

#increase rates of all assets in two time 
def test_rebalance_2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    
    #increase rates in two time
    mockuniv2.setRate(usdt.address, wbtc.address, (40000, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 40000))
    mockuniv2.setRate(usdt.address, weth.address, (2800, 1))
    mockuniv2.setRate(weth.address, usdt.address, (1, 2800))

    before_usdt_balance_sandbox1 = usdt.balanceOf(sandbox1)
    before_wbtc_balance = wbtc.balanceOf(treasury)
    before_eth_balance = treasury.balance()

    logging.info(before_wbtc_balance)
    logging.info(before_eth_balance)
    logging.info(before_usdt_balance_sandbox1)

    balances_in_usdt = before_eth_balance*mockuniv2.rates(usdt.address, weth.address)[0]*10**usdt.decimals()/10**weth.decimals() + before_wbtc_balance*mockuniv2.rates(usdt.address, wbtc.address)[0]*10**usdt.decimals()/10**wbtc.decimals()

    #prepare shares in usdt - how it have to be
    #50% eth, 50% wbtc
    htb_wbtc_in_usdt = balances_in_usdt*50/100    
    htb_weth_in_usdt = balances_in_usdt*50/100

    #prepare difference in usdt
    diff_in_usdt_wbtc = before_wbtc_balance*mockuniv2.rates(usdt.address, wbtc.address)[0]*10**usdt.decimals()/10**wbtc.decimals() - htb_wbtc_in_usdt
    diff_in_usdt_weth = before_eth_balance*mockuniv2.rates(usdt.address, weth.address)[0]*10**usdt.decimals()/10**weth.decimals() - htb_weth_in_usdt

    if diff_in_usdt_wbtc < 0:
        diff_in_usdt_wbtc = 0
    if diff_in_usdt_weth < 0:
        diff_in_usdt_weth = 0

    #prepare difference in natural units of measurement
    diff_wbtc = diff_in_usdt_wbtc/mockuniv2.rates(usdt.address, wbtc.address)[0]*10**wbtc.decimals()/10**usdt.decimals()
    diff_weth = diff_in_usdt_weth/mockuniv2.rates(usdt.address, weth.address)[0]*10**weth.decimals()/10**usdt.decimals()
    
    markets.rebalance({"from": accounts[0]})
    #logging.info(before_wbtc_balance)
    #logging.info(before_eth_balance)
    logging.info(usdt.balanceOf(sandbox1))


    #check rebalance
    assert wbtc.balanceOf(treasury) - before_wbtc_balance + diff_wbtc == 0 
    assert treasury.balance() - before_eth_balance + diff_weth < 3e11 #2*1e15
    assert before_usdt_balance_sandbox1 + diff_in_usdt_weth + diff_in_usdt_wbtc - usdt.balanceOf(sandbox1) < 1000
    


