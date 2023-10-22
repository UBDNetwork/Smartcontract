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
    accounts[0].transfer(mockuniv2, 40e18)


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

def test_topup_treasury_from_sandbox1(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, wbnb):
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

    for i in range(100):
        usdt.approve(sandbox1, PAY_AMOUNT, {'from':accounts[0]})
        tx = sandbox1.swapExactInput(
            usdt, 
            PAY_AMOUNT,
            0,
            0,
            ZERO_ADDRESS, 
            {'from':accounts[0]}
        )
        chain.sleep(sandbox1.TREASURY_TOPUP_PERIOD()+1)
        sandbox1.topupTreasury()

    #logging.info('Ether transfer:{}'.format(tx.events['ReceivedEther']))
    logging.info(
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{}'
        '\ntreasury.balance(eth):{}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury),
            treasury.balance()
    ))

def test_topup_sandbox2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, wbnb):
    #add new treasury assets
    markets.addERC20AssetToTreasury((wbnb, 40), {'from':accounts[0]})
    markets.setMarketParams(wbnb, (market_adapter, market_adapter, 0), {'from':accounts[0]})
    mockuniv2.setRate(usdt.address, wbnb.address, (1400, 1))
    mockuniv2.setRate(wbnb.address, usdt.address, (1, 1400))

    mockuniv2.setRate(usdt.address, wbtc.address, (100000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (10000, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 100000))
    mockuniv2.setRate(weth.address, usdt.address, (1,  10000))
    
    mockuniv2.setRate(wbtc.address, dai.address, (1, 100000))
    mockuniv2.setRate(weth.address, dai.address, (1,  10000))
    mockuniv2.setRate(dai.address, wbtc.address, (100000, 1))
    mockuniv2.setRate(dai.address, weth.address, (10000, 1))

    mockuniv2.setRate(wbnb.address, dai.address, (1, 5000))
    mockuniv2.setRate(dai.address, wbnb.address, (5000, 1))

    #assert treasury.isReadyForTopupSandBox2() == True
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))

    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_wbnb_treasury_amount = wbnb.balanceOf(treasury.address)

    #markets.topupSandBox2()
    tx = sandbox2.topupSandBox2( {'from':accounts[0]})

    #1/3 of amount
    wbtc_to_dai_amount = before_wbtc_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/100
    eth_to_dai_amount = before_eth_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/100
    wbnb_to_dai_amount = before_wbnb_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/100


    logging.info('wbtc_to_dai_amount = {}'.format(wbtc_to_dai_amount))
    logging.info('wbnb_to_dai_amount = {}'.format(wbnb_to_dai_amount))
    logging.info('eth_to_dai_amount = {}'.format(eth_to_dai_amount))
    logging.info('eth_balance_market = {}'.format(markets.balance()))

    dai_amount_calc = wbtc_to_dai_amount*mockuniv2.rates(wbtc.address, dai.address)[1]*10**dai.decimals()/10**wbtc.decimals() + eth_to_dai_amount*mockuniv2.rates(weth.address, dai.address)[1]*10**dai.decimals()/10**weth.decimals() + wbnb_to_dai_amount*mockuniv2.rates(wbnb.address, dai.address)[1]*10**dai.decimals()/10**wbnb.decimals()
    logging.info('dai_amount_calc = {}'.format(dai_amount_calc))

    assert dai.balanceOf(sandbox2) ==  dai_amount_calc
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount - wbtc_to_dai_amount
    assert treasury.balance() == before_eth_treasury_amount - eth_to_dai_amount
    assert before_wbnb_treasury_amount == wbnb.balanceOf(treasury.address)

def test_redeem_sandbox1(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, wbnb):
    
    #security decreased
    mockuniv2.setRate(dai.address, wbtc.address, (40000, 1))
    mockuniv2.setRate(dai.address, wbnb.address, (200, 1))
    mockuniv2.setRate(dai.address, weth.address, (3000, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 3000))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 40000))
    mockuniv2.setRate(wbnb.address, dai.address, (1, 200))

    mockuniv2.setRate(usdt.address, wbtc.address, (40000, 1))
    mockuniv2.setRate(usdt.address, wbnb.address, (200, 1))
    mockuniv2.setRate(usdt.address, weth.address, (3000, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 40000))
    mockuniv2.setRate(wbnb.address, usdt.address, (1, 200))
    mockuniv2.setRate(weth.address, usdt.address, (1, 3000))
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))

    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_wbnb_treasury_amount = wbnb.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_usdt_sandbox1_amount = usdt.balanceOf(sandbox1)
    wbtc_to_swap = before_wbtc_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/100
    wbnb_to_swap = before_wbnb_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/100
    eth_to_swap = before_eth_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/100
    usdt_amount_calc = wbtc_to_swap*mockuniv2.rates(wbtc.address, usdt.address)[1]*10**usdt.decimals()/10**wbtc.decimals() + eth_to_swap*mockuniv2.rates(weth.address, usdt.address)[1]*10**usdt.decimals()/10**weth.decimals() + wbnb_to_swap*mockuniv2.rates(wbnb.address, usdt.address)[1]*10**usdt.decimals()/10**wbnb.decimals()

    ubd.approve(sandbox1, 150000*10**ubd.decimals(), {"from": accounts[0]})
    tx = sandbox1.swapExactInput(ubd.address, 
                            150000*10**ubd.decimals(),
                            0,
                            150000*10**usdt.decimals())
    assert tx.return_value == 0

    assert wbtc.balanceOf(treasury) - before_wbtc_treasury_amount*(100 - treasury.SANDBOX1_REDEEM_PERCENT()) /100 < 10
    assert treasury.balance() - before_eth_treasury_amount*(100 - treasury.SANDBOX1_REDEEM_PERCENT())/100 == 0 #< 10000000000000
    assert before_usdt_sandbox1_amount + usdt_amount_calc - usdt.balanceOf(sandbox1) < 1000
    assert before_wbnb_treasury_amount == wbnb.balanceOf(treasury.address)



    
    






