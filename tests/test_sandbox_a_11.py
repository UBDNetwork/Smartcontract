import pytest
import logging
import math
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1005e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
def test_usdt_to_ubd(accounts, ubd, sandbox1, usdt):
    logging.info('!!!!!!!!!!!!!!!!!   exchange from usdt to ubd    !!!!!!!!!!!!!!!')
    sandbox1.setUBDToken(ubd, {'from':accounts[0]})
    sandbox1.setBeneficiary(accounts[1], {'from':accounts[0]})
    
    usdt.approve(sandbox1, PAY_AMOUNT, {'from':accounts[0]})
    
    chain.sleep(10)
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    assert tx.return_value == MINT_UBD_AMOUNT
    assert ubd.balanceOf(accounts[0]) == MINT_UBD_AMOUNT

def test_usdt_to_ubd_100k_1(accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    logging.info('UBDNetwork.state:{}'.format(markets.ubdNetwork()))
    init_market_registry(accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury, ubd, markets, wbtc, market_adapter, weth, usdc)
    logging.info('UBDNetwork.state:{}'.format(markets.getUBDNetworkInfo()))
    accounts[0].transfer(mockuniv2, 5e18)


    usdt.approve(sandbox1, PAY_AMOUNT * 100, {'from':accounts[0]})

    before_ubd_acc0 = ubd.balanceOf(accounts[0])
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT * 100,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    
    assert tx.return_value == MINT_UBD_AMOUNT * 100
    assert ubd.balanceOf(accounts[0]) == before_ubd_acc0 + MINT_UBD_AMOUNT * 100

def test_topup_treasury_from_sandbox_defi_1(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth):
    logging.info('!!!!!!!!!!!!!!!!!   topup treasury from sandbox1    !!!!!!!!!!!!!!!')
    logging.info(
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{}'
        '\ntreasury.balance(eth):{}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury),
            treasury.balance()
    ))
    logging.info('UBDNetwork.state:{}'.format(markets.ubdNetwork()))
    logging.info('UBDNetwork.state:{}'.format(markets.getUBDNetworkInfo()))

    #sandbox has 1% of balance > 1000 usdt - can exchange usdt to ether and wbtc
    before_usdt_sandbox = usdt.balanceOf(sandbox1.address)
    tx = sandbox1.topupTreasury({'from':accounts[1]})

    assert usdt.balanceOf(sandbox1.address) == before_usdt_sandbox - before_usdt_sandbox/100  #-1%


    logging.info('Ether transfer:{}'.format(tx.events['ReceivedEther']))
    [logging.info('\nfrom:{} to:{} value:{}'.format(x['from'],x['to'],x['value'])) for x in tx.events['Transfer']]
    logging.info(
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{}'
        '\ntreasury.balance(eth):{}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury),
            treasury.balance()
    ))

    #exchange 1% usdt to 50% ETH and 50% WBTC
    assert (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, wbtc.address)[0])*10**wbtc.decimals()/10**usdt.decimals() - wbtc.balanceOf(treasury) <=100
    assert (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, weth.address)[0])*10**weth.decimals()/10**usdt.decimals() - treasury.balance()  < 3e11

    #check market adapte settings for assets
    assert markets.markets(usdt)[0] == market_adapter
    assert markets.markets(usdt)[1] == market_adapter


def test_topup_treasury_from_sandbox_defi_2(
        accounts, MockSwapRouter, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, MarketAdapterCustomMarket, weth, usdc):
    
    mockuniv2_2 = accounts[0].deploy(MockSwapRouter, weth, weth)
    mockuniv2_2.setRate(usdt.address, wbtc.address, (10000, 1))
    mockuniv2_2.setRate(usdt.address, weth.address, (500, 1))
    mockuniv2_2.setRate(wbtc.address, usdt.address, (1, 10000))
    mockuniv2_2.setRate(weth.address, usdt.address, (1,  500))
    market_adapter2 = accounts[0].deploy(MarketAdapterCustomMarket, 'Mock UniSwapV2 adapter ', mockuniv2_2)

    markets.setMarketParams(usdt, (market_adapter2, market_adapter2, 0), {'from':accounts[0]})
    markets.setMarketParams(usdc, (market_adapter2, market_adapter2, 0), {'from':accounts[0]})
    markets.setMarketParams(wbtc, (market_adapter2, market_adapter2, 0), {'from':accounts[0]})
    markets.setMarketParams(dai, (market_adapter2, market_adapter2, 0), {'from':accounts[0]})

    markets.setMarketParams(weth, (market_adapter2, market_adapter2, 0), {'from':accounts[0]})
    markets.setMarketParams(ZERO_ADDRESS, (market_adapter2, market_adapter2, 0), {'from':accounts[0]})

    accounts[0].transfer(mockuniv2_2, 5e18)

    sandbox1.setMinTopUp(900, {"from": accounts[0]})

    chain.sleep(sandbox1.TREASURY_TOPUP_PERIOD()+10)

    before_usdt_sandbox = usdt.balanceOf(sandbox1.address)
    before_wbtc_treasury = wbtc.balanceOf(treasury)
    before_eth_treasury = treasury.balance()
    tx = sandbox1.topupTreasury({'from':accounts[1]})

    assert usdt.balanceOf(sandbox1.address) == before_usdt_sandbox - before_usdt_sandbox/100

    wbtc_calc = (before_usdt_sandbox/100/2/mockuniv2_2.rates(usdt.address, wbtc.address)[0])*10**wbtc.decimals()/10**usdt.decimals()
    eth_calc = (before_usdt_sandbox/100/2/mockuniv2_2.rates(usdt.address, weth.address)[0])*10**weth.decimals()/10**usdt.decimals()

    assert wbtc.balanceOf(treasury) == before_wbtc_treasury + wbtc_calc
    assert treasury.balance() == before_eth_treasury + eth_calc

    #check market adapte settings for assets
    assert markets.markets(usdt)[0] == market_adapter2
    assert markets.markets(usdt)[1] == market_adapter2

