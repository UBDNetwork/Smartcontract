import pytest
import logging
import math
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1005e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

# three tokens oif treasury - eth, wbtc, wbnb
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
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc,wbnb):
    logging.info('UBDNetwork.state:{}'.format(markets.ubdNetwork()))
    init_market_registry(accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury, ubd, markets, wbtc, market_adapter, weth, usdc)

    #add third token is treasury - wbnb, 10% 
    markets.setMarketParams(wbnb, (market_adapter, market_adapter, 0), {'from':accounts[0]})
    markets.addERC20AssetToTreasury((wbnb, 10), {'from':accounts[0]})
    logging.info('UBDNetwork.state:{}'.format(markets.getUBDNetworkInfo()))
    accounts[3].transfer(mockuniv2, 40e18)

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
        treasury, ubd, markets, wbtc, market_adapter, weth, wbnb):
    logging.info('!!!!!!!!!!!!!!!!!   topup treasury from sandbox1    !!!!!!!!!!!!!!!')
    logging.info(
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{}'
        '\ntreasury.balance(eth):{}'
        '\ntreasury.balance(wbnb):{}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury),
            treasury.balance(),
            wbnb.balanceOf(treasury),
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
        '\ntreasury.balance(eth):{}'
        '\ntreasury.balance(wbnb):{}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury),
            treasury.balance(),
            wbnb.balanceOf(treasury)
    ))


    #exchange 1% usdt to 40% ETH, 50% WBTC, 10% WBNB
    assert wbnb.balanceOf(treasury) - ((before_usdt_sandbox/100)*10/100/mockuniv2.rates(usdt.address, wbnb.address)[0])*10**wbnb.decimals()/10**usdt.decimals()  == 0 #<=100
    assert ((before_usdt_sandbox/100)*50/100/mockuniv2.rates(usdt.address, wbtc.address)[0])*10**wbtc.decimals()/10**usdt.decimals() - wbtc.balanceOf(treasury) <=100
    assert ((before_usdt_sandbox/100)*40/100/mockuniv2.rates(usdt.address, weth.address)[0])*10**weth.decimals()/10**usdt.decimals() - treasury.balance()  <= 5e12

def test_topup_sandbox2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, wbnb):
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
    mockuniv2.setRate(wbnb.address, dai.address, (1, 1600))
    mockuniv2.setRate(dai.address, wbnb.address, (1600, 1))
    mockuniv2.setRate(usdt.address, wbnb.address, (1600, 1))

    assert treasury.isReadyForTopupSandBox2() == True

    #let's go to topup sandbox2
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))
    logging.info('treasury_wbtc_usdt = {}'.format(mockuniv2.getAmountsOut(wbtc.balanceOf(treasury), [wbtc.address,usdt.address])))
    logging.info('treasury_eth_usdt = {}'.format(mockuniv2.getAmountsOut(treasury.balance(), [weth.address,usdt.address])))
    logging.info('treasury_wbnb_usdt = {}'.format(mockuniv2.getAmountsOut(wbnb.balanceOf(treasury), [wbnb.address,usdt.address])))
    logging.info('sandbox1_usdt_amount = {}'.format(usdt.balanceOf(sandbox1.address)))
    logging.info('ubd_amount = {}'.format(ubd.totalSupply()))


    assert dai.balanceOf(sandbox2.address) == 0
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_wbnb_treasury_amount = wbnb.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()

    tx = sandbox2.topupSandBox2( {'from':accounts[0]})

    #1/3 of amount
    wbtc_to_dai_amount = before_wbtc_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    eth_to_dai_amount = before_eth_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    wbnb_to_dai_amount = before_wbnb_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/(100*markets.PERCENT_DENOMINATOR())

    logging.info('wbtc_to_dai_amount = {}'.format(wbtc_to_dai_amount))
    logging.info('wbnb_to_dai_amount = {}'.format(wbnb_to_dai_amount))
    logging.info('eth_to_dai_amount = {}'.format(eth_to_dai_amount))
    logging.info('eth_balance_market = {}'.format(markets.balance()))

    dai_amount_calc = wbtc_to_dai_amount*mockuniv2.rates(wbtc.address, dai.address)[1]*10**dai.decimals()/10**wbtc.decimals() + eth_to_dai_amount*mockuniv2.rates(weth.address, dai.address)[1]*10**dai.decimals()/10**weth.decimals() + wbnb_to_dai_amount*mockuniv2.rates(wbnb.address, dai.address)[1]*10**dai.decimals()/10**wbnb.decimals() 
    logging.info('dai_amount_calc = {}'.format(dai_amount_calc))

    logging.info(mockuniv2.getAmountsOut(eth_to_dai_amount, [weth.address,dai.address]))
    logging.info(mockuniv2.getAmountsOut(wbtc_to_dai_amount, [wbtc.address,dai.address]))
    logging.info(mockuniv2.getAmountsOut(wbnb_to_dai_amount, [wbnb.address,dai.address]))

    assert dai.balanceOf(sandbox2) ==  dai_amount_calc
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount - wbtc_to_dai_amount
    assert wbnb.balanceOf(treasury) == before_wbnb_treasury_amount - wbnb_to_dai_amount
    assert treasury.balance() == before_eth_treasury_amount - eth_to_dai_amount

    logging.info('market eth balance = {}'.format(markets.balance()))
    logging.info('market_adapter wbtc balance = {}'.format(wbtc.balanceOf(market_adapter)))

    logging.info('dai_balance_sandbox2 = {}'.format(dai.balanceOf(sandbox2.address)))

    team = markets.getUBDNetworkTeamAddress()
    assert team == accounts[8]
    assert dai.allowance(sandbox2.address, team) == dai.balanceOf(sandbox2.address)*sandbox2.TEAM_PERCENT()/(100*markets.PERCENT_DENOMINATOR())

def test_topup_treasury_from_sandbox2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, wbnb):
    
    logging.info('!!!!!!!!!!!!!!!!!   topup treasury from sandbox2    !!!!!!!!!!!!!!!')

    mockuniv2.setRate(dai.address, wbtc.address, (28000, 1))
    mockuniv2.setRate(dai.address, weth.address, (1400, 1))
    mockuniv2.setRate(dai.address, wbnb.address, (200, 1))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 28000))
    mockuniv2.setRate(weth.address, dai.address, (1, 1400))
    mockuniv2.setRate(wbnb.address, dai.address, (1, 200))
    

    mockuniv2.setRate(usdt.address, wbtc.address, (28000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (1400, 1))
    mockuniv2.setRate(usdt.address, wbnb.address, (200, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 28000))
    mockuniv2.setRate(weth.address, usdt.address, (1, 1400))
    mockuniv2.setRate(wbnb.address, usdt.address, (1, 200))
    
    #logging.info(markets.getCollateralLevelM10())
    wbtc_treasury_amount_in_usdt = wbtc.balanceOf(treasury.address)*mockuniv2.rates(wbtc, usdt)[1]*10**usdt.decimals()/10**wbtc.decimals()
    wbnb_treasury_amount_in_usdt = wbnb.balanceOf(treasury.address)*mockuniv2.rates(wbnb, usdt)[1]*10**usdt.decimals()/10**wbnb.decimals()
    eth_treasury_amount_in_usdt = treasury.balance()*mockuniv2.rates(weth, usdt)[1]*10**usdt.decimals()/10**weth.decimals()

    usdt_sandbox1_amount = usdt.balanceOf(sandbox1.address)
    ubd_amount_in_usdt = ubd.totalSupply()*10**usdt.decimals()/10**ubd.decimals()

    security = 10*(wbtc_treasury_amount_in_usdt + wbnb_treasury_amount_in_usdt + eth_treasury_amount_in_usdt + usdt_sandbox1_amount)/ubd_amount_in_usdt
    #check security  - between 0.5 and 1
    assert round(security) == markets.getCollateralLevelM10()

    #topup treasury from sandbox2 - 1% of dai, to wbtc (50/100), eth (40/100), wbnb (10/100)
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_wbnb_treasury_amount = wbnb.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_dai_sandbox2_amount = dai.balanceOf(sandbox2.address)

    # add call constant with percent!!!!
    logging.info('dai to exchange = {}'.format(before_dai_sandbox2_amount/100))
    assert sandbox2.lastTreasuryTopUp() == 0
    logging.info(markets.treasuryERC20Assets())
    logging.info(markets.ubdNetwork())
    tx = sandbox2.topupTreasury()
    assert tx.return_value == True
    assert sandbox2.lastTreasuryTopUp() > 0


    ## 1% to topup (1/100) and personal percent for each treasury token (50/100, 40/100, 10/100)
    wbtc_amount_calc = before_dai_sandbox2_amount*50*10**wbtc.decimals()/mockuniv2.rates(dai, wbtc)[0]/10**dai.decimals()/100/100
    wbnb_amount_calc = before_dai_sandbox2_amount*10*10**wbnb.decimals()/mockuniv2.rates(dai, wbnb)[0]/10**dai.decimals()/100/100
    eth_amount_calc = before_dai_sandbox2_amount*40*10**weth.decimals()/mockuniv2.rates(dai, weth)[0]/10**dai.decimals()/100/100

    assert dai.balanceOf(sandbox2) == before_dai_sandbox2_amount*99/100
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount + wbtc_amount_calc
    assert wbnb.balanceOf(treasury) == before_wbnb_treasury_amount + wbnb_amount_calc
    assert before_eth_treasury_amount + eth_amount_calc - treasury.balance()  < 100

    #second time in day - revert is expected
    with reverts('Please wait untit TREASURY_TOPUP_PERIOD'):
        sandbox2.topupTreasury()

    #security increased and became higher than 1 - topup treasury from sandbox2 is impossible
    mockuniv2.setRate(dai.address, wbtc.address, (56000, 1))
    mockuniv2.setRate(dai.address, weth.address, (2800, 1))
    mockuniv2.setRate(dai.address, wbnb.address, (400, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 56000))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 2800))
    mockuniv2.setRate(wbnb.address, dai.address, (1, 400))

    mockuniv2.setRate(usdt.address, wbtc.address, (56000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (2800, 1))
    mockuniv2.setRate(usdt.address, wbnb.address, (400, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 56000))
    mockuniv2.setRate(weth.address, usdt.address, (1, 2800))
    mockuniv2.setRate(wbnb.address, usdt.address, (1, 400))

    wbtc_treasury_amount_in_usdt = wbtc.balanceOf(treasury.address)*mockuniv2.rates(wbtc, usdt)[1]*10**usdt.decimals()/10**wbtc.decimals()
    wbnb_treasury_amount_in_usdt = wbnb.balanceOf(treasury.address)*mockuniv2.rates(wbnb, usdt)[1]*10**usdt.decimals()/10**wbnb.decimals()
    eth_treasury_amount_in_usdt = treasury.balance()*mockuniv2.rates(weth, usdt)[1]*10**usdt.decimals()/10**weth.decimals()

    security = 10*(wbtc_treasury_amount_in_usdt + wbnb_treasury_amount_in_usdt + eth_treasury_amount_in_usdt + usdt_sandbox1_amount)/ubd_amount_in_usdt
    assert markets.getCollateralLevelM10() == math.trunc(security)

    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_wbnb_treasury_amount = wbnb.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_dai_sandbox2_amount = dai.balanceOf(sandbox2.address)
    
    tx = sandbox2.topupTreasury()

    assert tx.return_value == False
    assert dai.balanceOf(sandbox2) == before_dai_sandbox2_amount
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount
    assert wbnb.balanceOf(treasury) == before_wbnb_treasury_amount
    assert treasury.balance() == before_eth_treasury_amount

def test_ubd_to_usdt(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, wbnb):

    ubd.approve(sandbox1, 150000*10**ubd.decimals(), {"from": accounts[0]})
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))

    
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_wbnb_treasury_amount = wbnb.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_usdt_sandbox1_amount = usdt.balanceOf(sandbox1)
    wbtc_to_swap = before_wbtc_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    wbnb_to_swap = before_wbnb_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    eth_to_swap = before_eth_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    #logging.info(eth_to_swap)
    usdt_amount_calc = wbtc_to_swap*mockuniv2.rates(wbtc.address, usdt.address)[1]*10**usdt.decimals()/10**wbtc.decimals() + eth_to_swap*mockuniv2.rates(weth.address, usdt.address)[1]*10**usdt.decimals()/10**weth.decimals() + wbnb_to_swap*mockuniv2.rates(wbnb.address, usdt.address)[1]*10**usdt.decimals()/10**wbnb.decimals() 

    logging.info('before_wbtc_treasury_amount = {}'.format(before_wbtc_treasury_amount))
    logging.info('before_wbnb_treasury_amount = {}'.format(before_wbnb_treasury_amount))
    logging.info('before_eth_treasury_amount = {}'.format(before_eth_treasury_amount))

    logging.info('before_usdt_sandbox1_amount = {}'.format(before_usdt_sandbox1_amount))
    logging.info('usdt_amount_calc = {}'.format(usdt_amount_calc))
    #only redeem Sandbox1 from treasury - without swap
    ##1% of treasury assets to redeem sandbox1
    tx = sandbox1.swapExactInput(ubd.address, 
                            150000*10**ubd.decimals(),
                            0,
                            150000*10**usdt.decimals())
    #logging.info(tx.return_value)
    #logging.info(usdt.balanceOf(sandbox1))
    #logging.info(wbtc.balanceOf(treasury.address))
    #logging.info(wbnb.balanceOf(treasury.address))
    #logging.info(treasury.balance())

    assert tx.return_value == 0 #only redeem - without swap
    assert wbtc.balanceOf(treasury) - before_wbtc_treasury_amount + wbtc_to_swap == 0 #< 10
    assert wbnb.balanceOf(treasury) - before_wbnb_treasury_amount + wbnb_to_swap == 0 # < 10
    assert before_eth_treasury_amount - eth_to_swap - treasury.balance() < 100
    assert before_usdt_sandbox1_amount + usdt_amount_calc - usdt.balanceOf(sandbox1) < 200

    #security decreased
    mockuniv2.setRate(dai.address, wbtc.address, (28000, 1))
    mockuniv2.setRate(dai.address, weth.address, (1400, 1))
    mockuniv2.setRate(dai.address, wbnb.address, (200, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 28000))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 1400))
    mockuniv2.setRate(wbnb.address, dai.address, (1, 200))

    mockuniv2.setRate(usdt.address, wbtc.address, (28000, 1))
    mockuniv2.setRate(usdt.address, wbnb.address, (200, 1))
    mockuniv2.setRate(usdt.address, weth.address, (1400, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 28000))
    mockuniv2.setRate(weth.address, usdt.address, (1, 1400))
    mockuniv2.setRate(wbnb.address, usdt.address, (1, 200))
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))
    #security decreased - redeem is not possible and not enough usdt to exchange ubd
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_wbnb_treasury_amount = wbnb.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_usdt_sandbox1_amount = usdt.balanceOf(sandbox1)
    tx = sandbox1.swapExactInput(ubd.address, 
                            150000*10**ubd.decimals(),
                            0,
                            150000*10**usdt.decimals())
    assert tx.return_value == 0
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount
    assert wbnb.balanceOf(treasury) == before_wbnb_treasury_amount
    assert treasury.balance() == before_eth_treasury_amount
    assert usdt.balanceOf(sandbox1) == before_usdt_sandbox1_amount 



    #security increased
    mockuniv2.setRate(dai.address, wbtc.address, (56000, 1))
    mockuniv2.setRate(dai.address, wbnb.address, (400, 1))
    mockuniv2.setRate(dai.address, weth.address, (2800, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 2800))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 56000))
    mockuniv2.setRate(wbnb.address, dai.address, (1, 400))

    mockuniv2.setRate(usdt.address, wbtc.address, (56000, 1))
    mockuniv2.setRate(usdt.address, wbnb.address, (400, 1))
    mockuniv2.setRate(usdt.address, weth.address, (2800, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 56000))
    mockuniv2.setRate(wbnb.address, usdt.address, (1, 400))
    mockuniv2.setRate(weth.address, usdt.address, (1, 2800))

    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))
    #make redeem - 1% from treasury to sandbox1 (usdt) and swap ubd to usdt - sandbox1 has enough usdt after redeem
    fee_percent = sandbox1.paymentTokens(ubd)[1]/sandbox1.PERCENT_DENOMINATOR()
    before_usdt_sandbox1 = usdt.balanceOf(sandbox1)
    before_usdt_acc = usdt.balanceOf(accounts[0])
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_wbnb_treasury_amount = wbnb.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_ubd_acc = ubd.balanceOf(accounts[0])

    wbtc_to_swap = before_wbtc_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    wbnb_to_swap = before_wbnb_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    eth_to_swap = before_eth_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    usdt_amount_calc = wbtc_to_swap*mockuniv2.rates(wbtc.address, usdt.address)[1]*10**usdt.decimals()/10**wbtc.decimals() + eth_to_swap*mockuniv2.rates(weth.address, usdt.address)[1]*10**usdt.decimals()/10**weth.decimals() + wbnb_to_swap*mockuniv2.rates(wbnb.address, usdt.address)[1]*10**usdt.decimals()/10**wbnb.decimals()
    #logging.info(usdt.balanceOf(sandbox1))
    #logging.info(wbtc.balanceOf(treasury.address))
    #logging.info(wbnb.balanceOf(treasury.address))
    #logging.info(treasury.balance())
    tx = sandbox1.swapExactInput(ubd.address, 
                            102510*10**ubd.decimals(),
                            0,
                            102000*10**usdt.decimals())

    assert tx.return_value == 102510*10**usdt.decimals()*100/(100+fee_percent)
    assert before_usdt_sandbox1 + usdt_amount_calc - 102510*10**usdt.decimals()*100/(100+fee_percent) - usdt.balanceOf(sandbox1) < 300
    assert wbtc.balanceOf(treasury) - before_wbtc_treasury_amount*(100 - treasury.SANDBOX1_REDEEM_PERCENT()/markets.PERCENT_DENOMINATOR()) /100 < 10
    assert wbnb.balanceOf(treasury) - before_wbnb_treasury_amount*(100 - treasury.SANDBOX1_REDEEM_PERCENT()/markets.PERCENT_DENOMINATOR()) /100 < 3000
    assert before_eth_treasury_amount*(100 - treasury.SANDBOX1_REDEEM_PERCENT()/markets.PERCENT_DENOMINATOR())/100 - treasury.balance() < 1000
    assert ubd.balanceOf(accounts[0]) == before_ubd_acc - 102510*10**ubd.decimals()
    assert before_usdt_acc + 102510*10**usdt.decimals()*100/(100+fee_percent) == usdt.balanceOf(accounts[0])

    #logging.info('!!!!AFTER!!!!!')
    #logging.info(usdt.balanceOf(sandbox1))
    #logging.info(wbtc.balanceOf(treasury.address))
    #logging.info(wbnb.balanceOf(treasury.address))
    #logging.info(treasury.balance())
    #logging.info(usdt.balanceOf(accounts[0]))

def test_check_other_functions(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, wbnb):
    amount_from_contract = treasury.getBalanceInStableUnits(treasury, [wbtc, wbnb])
    eth_calc = treasury.balance() * mockuniv2.rates(weth, usdt)[1] /10**markets.NATIVE_TOKEN_DECIMALS()
    wbtc_calc = wbtc.balanceOf(treasury) * mockuniv2.rates(wbtc, usdt)[1] / 10**wbtc.decimals()
    wbnb_calc = wbnb.balanceOf(treasury) * mockuniv2.rates(wbnb, usdt)[1] / 10**wbnb.decimals()

    calc_amount = eth_calc + wbtc_calc + wbnb_calc

    assert amount_from_contract == calc_amount
    assert markets.getAmountOut(treasury.balance(), [weth, usdt]) == eth_calc*10**usdt.decimals()
    assert markets.getAmountOut(wbtc.balanceOf(treasury), [wbtc, usdt]) == round(wbtc_calc*10**usdt.decimals())
    assert markets.getAmountOut(wbnb.balanceOf(treasury), [wbnb, usdt]) == wbnb_calc*10**usdt.decimals()





        
        
