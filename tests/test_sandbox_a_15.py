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

def test_usdt_to_ubd_100k_1(accounts, ubd, sandbox1, usdt):
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
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    
    init_market_registry(accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury, ubd, markets, wbtc, market_adapter, weth, usdc)
    accounts[9].transfer(mockuniv2, 30e18)

    #sandbox has 1% of balance > 1000 usdt - can exchange usdt to ether and wbtc
    for i in range(70):
        before_usdt_sandbox = usdt.balanceOf(sandbox1.address)
        before_eth_treasury = treasury.balance()
        before_wbtc_treasury = wbtc.balanceOf(treasury)

        tx = sandbox1.topupTreasury({'from':accounts[1]})
        
        chain.sleep(sandbox1.TREASURY_TOPUP_PERIOD()+10)
        chain.mine()

        min_amount = sandbox1.MIN_TREASURY_TOPUP_AMOUNT()
        sandbox1.setMinTopUp(min_amount*0.98)
        
        #exchange 1% usdt to 50% ETH and 50% WBTC
        assert abs(wbtc.balanceOf(treasury) \
            - (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, wbtc.address)[0])*10**wbtc.decimals()/10**usdt.decimals() \
            - before_wbtc_treasury) <1e3
        assert abs(before_eth_treasury \
            + (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, weth.address)[0])*10**weth.decimals()/10**usdt.decimals() \
            - treasury.balance())  <= 3e12
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

    
def test_topup_sandbox2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth):
    logging.info('!!!!!!!!!!!!!!!!!   topup sandbox2 from treasury    !!!!!!!!!!!!!!!')
    assert treasury.isReadyForTopupSandBox2() == False
    

    #bullrun
    mockuniv2.setRate(usdt.address, wbtc.address, (200000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (20000, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 200000))
    mockuniv2.setRate(weth.address, usdt.address, (1, 20000))
    mockuniv2.setRate(dai.address, wbtc.address, (200000, 1))
    mockuniv2.setRate(dai.address, weth.address, (20000, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 20000))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 200000))

    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))
    assert treasury.isReadyForTopupSandBox2() == True

    #let's go to topup sandbox2
    assert dai.balanceOf(sandbox2.address) == 0
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()

    #markets.topupSandBox2()
    tx = sandbox2.topupSandBox2( {'from':accounts[0]})
    #tx = treasury.sendEtherForRedeem(treasury.SANDBOX2_TOPUP_PERCENT())
    [logging.info('\nfrom:{} to:{} value:{}'.format(x['from'],x['to'],x['value'])) for x in tx.events['Transfer']]
    #1/3 of amount
    wbtc_to_dai_amount = before_wbtc_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT() \
        /(100 *treasury.PERCENT_DENOMINATOR())
    eth_to_dai_amount = before_eth_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT() \
        /(100 *treasury.PERCENT_DENOMINATOR())

    dai_amount_calc = wbtc_to_dai_amount*mockuniv2.rates(wbtc.address, dai.address)[1]*10**dai.decimals() \
        /10**wbtc.decimals() \
        + eth_to_dai_amount*mockuniv2.rates(weth.address, dai.address)[1]*10**dai.decimals() \
        /10**weth.decimals()

    assert int(dai.balanceOf(sandbox2) /10**10) ==  int(dai_amount_calc/10**10)
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount - wbtc_to_dai_amount
    assert treasury.balance() == before_eth_treasury_amount - eth_to_dai_amount

    team = markets.getUBDNetworkTeamAddress()
    assert dai.allowance(sandbox2.address, team) == dai.balanceOf(sandbox2.address)*sandbox2.TEAM_PERCENT()/1000000

def test_topup_treasury_from_sandbox2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth):
    
    logging.info('!!!!!!!!!!!!!!!!!   topup treasury from sandbox2    !!!!!!!!!!!!!!!')

    mockuniv2.setRate(dai.address, wbtc.address, (10, 1))
    mockuniv2.setRate(dai.address, weth.address, (5, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 5))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 10))

    mockuniv2.setRate(usdt.address, wbtc.address, (10, 1))
    mockuniv2.setRate(usdt.address, weth.address, (5, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 10))
    mockuniv2.setRate(weth.address, usdt.address, (1, 5))

    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))
    
    #logging.info(markets.getCollateralLevelM10())
    wbtc_treasury_amount_in_usdt = wbtc.balanceOf(treasury.address)*mockuniv2.rates(wbtc, usdt)[1]*10**usdt.decimals()/10**wbtc.decimals()
    eth_treasury_amount_in_usdt = treasury.balance()*mockuniv2.rates(weth, usdt)[1]*10**usdt.decimals()/10**weth.decimals()
    usdt_sandbox1_amount = usdt.balanceOf(sandbox1.address)
    ubd_amount_in_usdt = ubd.totalSupply()*10**usdt.decimals()/10**ubd.decimals()

    security = 10*(wbtc_treasury_amount_in_usdt + eth_treasury_amount_in_usdt + usdt_sandbox1_amount)/ubd_amount_in_usdt
    #check security  - between 0.5 and 1
    #assert round(security) == markets.getCollateralLevelM10()

    #topup treasury from sandbox2 - 1% of dai, at least $1,000 - to wbtc and eth 50x50
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_dai_sandbox2_amount = dai.balanceOf(sandbox2.address)

    assert sandbox2.lastTreasuryTopUp() == 0
    tx = sandbox2.topupTreasury()
    assert tx.return_value == False
    assert sandbox2.lastTreasuryTopUp() == 0

    assert dai.balanceOf(sandbox2) == before_dai_sandbox2_amount
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount
    assert treasury.balance() == before_eth_treasury_amount

   

def test_ubd_to_usdt(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth):

    ubd.approve(sandbox1, 150000*10**ubd.decimals(), {"from": accounts[0]})
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))

    
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_usdt_sandbox1_amount = usdt.balanceOf(sandbox1)

    tx = sandbox1.swapExactInput(ubd.address, 
                            150000*10**ubd.decimals(),
                            0,
                            150000*10**usdt.decimals())


    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount 
    assert treasury.balance() == before_eth_treasury_amount
    assert before_usdt_sandbox1_amount == usdt.balanceOf(sandbox1)

   