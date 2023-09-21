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

def test_topup_treasury1(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    logging.info('UBDNetwork.state:{}'.format(markets.ubdNetwork()))
    init_market_registry(accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury, ubd, markets, wbtc, market_adapter, weth, usdc)
    logging.info('UBDNetwork.state:{}'.format(markets.getUBDNetworkInfo()))
    accounts[9].transfer(mockuniv2, accounts[9].balance()-1e18)

    #sandbox has 1% of balance <1000 usdt - can't exchange usdt to ether and wbtc
    with reverts("Too small topup amount"):
        tx = sandbox1.topupTreasury({'from':accounts[1]})

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
    accounts[9].transfer(mockuniv2, accounts[9].balance()-1e18)

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
    assert wbtc.balanceOf(treasury) - (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, wbtc.address)[0])*10**wbtc.decimals()/10**usdt.decimals() <=100
    assert (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, weth.address)[0])*10**weth.decimals()/10**usdt.decimals() - treasury.balance()  <= 3000000000000

def test_topup_sandbox2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth):
    logging.info('!!!!!!!!!!!!!!!!!   topup sandbox2 from treasury    !!!!!!!!!!!!!!!')
    assert treasury.isReadyForTopupSandBox2() == False
    
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

    #try to topup Treasury second time in day - expect revert 
    usdt.approve(sandbox1, PAY_AMOUNT, {'from':accounts[0]})
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )

    with reverts('Please wait untit TREASURY_TOPUP_PERIOD'):
        sandbox1.topupTreasury()

    #bullrun
    mockuniv2.setRate(usdt.address, wbtc.address, (100000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (10000, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 100000))
    mockuniv2.setRate(weth.address, usdt.address, (1, 10000))
    mockuniv2.setRate(dai.address, wbtc.address, (100000, 1))
    mockuniv2.setRate(dai.address, weth.address, (10000, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 10000))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 100000))

    assert treasury.isReadyForTopupSandBox2() == True

    #let's go to topup sandbox2
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))
    logging.info('treasury_wbtc_usdt = {}'.format(mockuniv2.getAmountsOut(wbtc.balanceOf(treasury), [wbtc.address,usdt.address])))
    logging.info('treasury_eth_usdt = {}'.format(mockuniv2.getAmountsOut(treasury.balance(), [weth.address,usdt.address])))
    logging.info('sandbox1_usdt_amount = {}'.format(usdt.balanceOf(sandbox1.address)))
    logging.info('ubd_amount = {}'.format(ubd.totalSupply()))


    assert dai.balanceOf(sandbox2.address) == 0
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()

    #markets.topupSandBox2()
    tx = sandbox2.topupSandBox2( {'from':accounts[0]})
    #tx = treasury.sendEtherForRedeem(treasury.SANDBOX2_TOPUP_PERCENT())

    #1/3 of amount
    wbtc_to_dai_amount = before_wbtc_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/100
    eth_to_dai_amount = before_eth_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/100

    logging.info('wbtc_to_dai_amount = {}'.format(wbtc_to_dai_amount))
    logging.info('eth_to_dai_amount = {}'.format(eth_to_dai_amount))
    logging.info('eth_balance_market = {}'.format(markets.balance()))

    dai_amount_calc = wbtc_to_dai_amount*mockuniv2.rates(wbtc.address, dai.address)[1]*10**dai.decimals()/10**wbtc.decimals() + eth_to_dai_amount*mockuniv2.rates(weth.address, dai.address)[1]*10**dai.decimals()/10**weth.decimals()
    logging.info('dai_amount_calc = {}'.format(dai_amount_calc))

    logging.info(mockuniv2.getAmountsOut(eth_to_dai_amount, [weth.address,dai.address]))
    logging.info(mockuniv2.getAmountsOut(wbtc_to_dai_amount, [wbtc.address,dai.address]))

    assert dai.balanceOf(sandbox2) ==  dai_amount_calc
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount - wbtc_to_dai_amount
    assert treasury.balance() == before_eth_treasury_amount - eth_to_dai_amount

    logging.info('market eth balance = {}'.format(markets.balance()))
    logging.info('market_adapter wbtc balance = {}'.format(wbtc.balanceOf(market_adapter)))

    logging.info('dai_balance_sandbox = {}'.format(dai.balanceOf(sandbox2.address)))

    assert dai.balanceOf(sandbox2.address) == dai_amount_calc
    team = markets.getUBDNetworkTeamAddress()
    assert dai.allowance(sandbox2.address, team) == dai.balanceOf(sandbox2.address)*sandbox2.TEAM_PERCENT()/100

def test_topup_treasury_from_sandbox2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth):
    
    logging.info('!!!!!!!!!!!!!!!!!   topup treasury from sandbox2    !!!!!!!!!!!!!!!')

    mockuniv2.setRate(dai.address, wbtc.address, (28000, 1))
    mockuniv2.setRate(dai.address, weth.address, (1400, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 28000))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 1400))

    mockuniv2.setRate(usdt.address, wbtc.address, (28000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (1400, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 28000))
    mockuniv2.setRate(weth.address, usdt.address, (1, 1400))
    
    #logging.info(markets.getCollateralLevelM10())
    wbtc_treasury_amount_in_usdt = wbtc.balanceOf(treasury.address)*mockuniv2.rates(wbtc, usdt)[1]*10**usdt.decimals()/10**wbtc.decimals()
    eth_treasury_amount_in_usdt = treasury.balance()*mockuniv2.rates(weth, usdt)[1]*10**usdt.decimals()/10**weth.decimals()
    usdt_sandbox1_amount = usdt.balanceOf(sandbox1.address)
    ubd_amount_in_usdt = ubd.totalSupply()*10**usdt.decimals()/10**ubd.decimals()

    security = 10*(wbtc_treasury_amount_in_usdt + eth_treasury_amount_in_usdt + usdt_sandbox1_amount)/ubd_amount_in_usdt
    #check security  - between 0.5 and 1
    assert round(security) == markets.getCollateralLevelM10()

    #topup treasury from sandbox2 - 1% of dai, at least $1,000 - to wbtc and eth 50x50
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_dai_sandbox2_amount = dai.balanceOf(sandbox2.address)

    # add call constant with percent!!!!
    logging.info('dai to exchange = {}'.format(before_dai_sandbox2_amount/100))
    assert sandbox2.lastTreasuryTopUp() == 0
    tx = sandbox2.topupTreasury()
    assert tx.return_value == True
    assert sandbox2.lastTreasuryTopUp() > 0


    ##need call of constant from contract with topup percent - wait appearing it!!
    wbtc_amount_calc = before_dai_sandbox2_amount*10**wbtc.decimals()/mockuniv2.rates(dai, wbtc)[0]/10**dai.decimals()/2/100
    eth_amount_calc = before_dai_sandbox2_amount*10**weth.decimals()/mockuniv2.rates(dai, weth)[0]/10**dai.decimals()/2/100

    assert dai.balanceOf(sandbox2) == before_dai_sandbox2_amount*99/100
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount + wbtc_amount_calc
    assert treasury.balance() - before_eth_treasury_amount - eth_amount_calc < 100

    #second time in day - revert is expected
    with reverts('Please wait untit TREASURY_TOPUP_PERIOD'):
        sandbox2.topupTreasury()

    #security increased and became higher than 1 - topup treasury from sandbox2 is impossible
    mockuniv2.setRate(dai.address, wbtc.address, (56000, 1))
    mockuniv2.setRate(dai.address, weth.address, (2800, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 56000))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 2800))

    mockuniv2.setRate(usdt.address, wbtc.address, (56000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (2800, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 56000))
    mockuniv2.setRate(weth.address, usdt.address, (1, 2800))

    wbtc_treasury_amount_in_usdt = wbtc.balanceOf(treasury.address)*mockuniv2.rates(wbtc, usdt)[1]*10**usdt.decimals()/10**wbtc.decimals()
    eth_treasury_amount_in_usdt = treasury.balance()*mockuniv2.rates(weth, usdt)[1]*10**usdt.decimals()/10**weth.decimals()

    security = 10*(wbtc_treasury_amount_in_usdt + eth_treasury_amount_in_usdt + usdt_sandbox1_amount)/ubd_amount_in_usdt
    assert markets.getCollateralLevelM10() == math.trunc(security)

    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_dai_sandbox2_amount = dai.balanceOf(sandbox2.address)
    
    tx = sandbox2.topupTreasury()

    assert tx.return_value == False
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
    wbtc_to_swap = before_wbtc_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/100
    eth_to_swap = before_eth_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/100
    #logging.info(eth_to_swap)
    usdt_amount_calc = wbtc_to_swap*mockuniv2.rates(wbtc.address, usdt.address)[1]*10**usdt.decimals()/10**wbtc.decimals() + eth_to_swap*mockuniv2.rates(weth.address, usdt.address)[1]*10**usdt.decimals()/10**weth.decimals()

    #logging.info('before_wbtc_treasury_amount = {}'.format(before_wbtc_treasury_amount))
    #logging.info('before_eth_treasury_amount = {}'.format(before_eth_treasury_amount))

    #logging.info('before_usdt_sandbox1_amount = {}'.format(before_usdt_sandbox1_amount))
    #logging.info('usdt_amount_calc = {}'.format(usdt_amount_calc))
    #only redeem Sandbox1 - without swap
    tx = sandbox1.swapExactInput(ubd.address, 
                            150000*10**ubd.decimals(),
                            0,
                            150000*10**usdt.decimals())
    #logging.info(tx.return_value)
    #logging.info(usdt.balanceOf(sandbox1))
    #logging.info(wbtc.balanceOf(treasury.address))
    #logging.info(treasury.balance())

    assert wbtc.balanceOf(treasury) - before_wbtc_treasury_amount*(100 - treasury.SANDBOX1_REDEEM_PERCENT()) /100 < 10
    assert treasury.balance() - before_eth_treasury_amount*(100 - treasury.SANDBOX1_REDEEM_PERCENT())/100 < 10000000000000
    assert before_usdt_sandbox1_amount + usdt_amount_calc - usdt.balanceOf(sandbox1) < 1000

    #security decreased
    mockuniv2.setRate(dai.address, wbtc.address, (28000, 1))
    mockuniv2.setRate(dai.address, weth.address, (1400, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 28000))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 1400))

    mockuniv2.setRate(usdt.address, wbtc.address, (28000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (1400, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 28000))
    mockuniv2.setRate(weth.address, usdt.address, (1, 1400))
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))
    tx = sandbox1.swapExactInput(ubd.address, 
                            150000*10**ubd.decimals(),
                            0,
                            150000*10**usdt.decimals())
    assert tx.return_value == 0

    #security increased
    mockuniv2.setRate(dai.address, wbtc.address, (56000, 1))
    mockuniv2.setRate(dai.address, weth.address, (2800, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 56000))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 2800))

    mockuniv2.setRate(usdt.address, wbtc.address, (56000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (2800, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 56000))
    mockuniv2.setRate(weth.address, usdt.address, (1, 2800))

    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))
    fee_percent = sandbox1.paymentTokens(ubd)[1]/sandbox1.PERCENT_DENOMINATOR()
    before_usdt_sandbox1 = usdt.balanceOf(sandbox1)
    before_usdt_acc = usdt.balanceOf(accounts[0])
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_ubd_acc = ubd.balanceOf(accounts[0])

    wbtc_to_swap = before_wbtc_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/100
    eth_to_swap = before_eth_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/100
    usdt_amount_calc = wbtc_to_swap*mockuniv2.rates(wbtc.address, usdt.address)[1]*10**usdt.decimals()/10**wbtc.decimals() + eth_to_swap*mockuniv2.rates(weth.address, usdt.address)[1]*10**usdt.decimals()/10**weth.decimals()
    tx = sandbox1.swapExactInput(ubd.address, 
                            103000*10**ubd.decimals(),
                            0,
                            102000*10**usdt.decimals())

    assert tx.return_value == 103000*10**usdt.decimals()*100/(100+fee_percent)
    assert usdt.balanceOf(sandbox1) - before_usdt_sandbox1 - usdt_amount_calc + 103000*10**usdt.decimals()*100/(100+fee_percent) < 30
    assert wbtc.balanceOf(treasury) - before_wbtc_treasury_amount*(100 - treasury.SANDBOX1_REDEEM_PERCENT()) /100 < 10
    assert treasury.balance() - before_eth_treasury_amount*(100 - treasury.SANDBOX1_REDEEM_PERCENT())/100 < 10000000000000 
    assert ubd.balanceOf(accounts[0]) == before_ubd_acc - 103000*10**ubd.decimals()
    assert before_usdt_acc + 103000*10**usdt.decimals()*100/(100+fee_percent) == usdt.balanceOf(accounts[0])





        
        
