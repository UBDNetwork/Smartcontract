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
    logging.info('!!!!!!!!!!!!!!!!!   topup treasury from sandbox1 - there is slippage in defi 50%, there is slippage in marketRegistry 1%  !!!!!!!!!!!!!!!')
    
    #set slippage for defi - defi will give less amountOut in swapping time
    mockuniv2.setSlippgae(50)
    init_market_registry(accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury, ubd, markets, wbtc, market_adapter, weth, usdc)
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
    accounts[2].transfer(mockuniv2, 40e18)

    #sandbox has 1% of balance > 1000 usdt - can exchange usdt to ether and wbtc
    before_usdt_sandbox = usdt.balanceOf(sandbox1.address)
    logging.info(markets.markets(usdt))
    with reverts('UniSwapV2: Excuse me, slippage. Try again with other settings'):
        tx = sandbox1.topupTreasury({'from':accounts[1]})

    #change settings
    mockuniv2.setSlippgae(1) # valid slippage persent . MarketRegistry has 1% slippage for assets
    tx = sandbox1.topupTreasury({'from':accounts[1]})


    assert usdt.balanceOf(sandbox1.address) == before_usdt_sandbox - before_usdt_sandbox/100  #-1%

    assert tx.events['TreasuryTopup'][0]['Asset'] == usdt.address
    assert tx.events['TreasuryTopup'][0]['TopupAmount'] == before_usdt_sandbox/100


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

    #exchange 1% usdt of sandbox1 to swap => 50% ETH and 50% WBTC + 1% slippage in defi happened - treasury got assets 1% less due to slippage
    assert (before_usdt_sandbox*99/100/100/2/mockuniv2.rates(usdt.address, wbtc.address)[0])*10**wbtc.decimals()/10**usdt.decimals() - wbtc.balanceOf(treasury) <=100
    assert (before_usdt_sandbox*99/100/100/2/mockuniv2.rates(usdt.address, weth.address)[0])*10**weth.decimals()/10**usdt.decimals() - treasury.balance() <= 3e12

def test_topup_sandbox2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth):
    logging.info('!!!!!!!!!!!!!!!!!   topup sandbox2 from treasury    !!!!!!!!!!!!!!!')

    #topup manually treasury
    wbtc.transfer(treasury, 7*10**wbtc.decimals(), {"from": accounts[0]})
    accounts[0].transfer(treasury,30e18)

    logging.info(markets.getCollateralLevelM10())
    logging.info(ubd.totalSupply()/10**ubd.decimals())
    logging.info(usdt.balanceOf(sandbox1)/10**usdt.decimals())
    logging.info(wbtc.balanceOf(treasury)/10**wbtc.decimals())
    logging.info(treasury.balance()/10**18)

    #logging.info(markets.getCollateralLevelM10())
    assert treasury.isReadyForTopupSandBox2() == True

    #set slippage for defi - defi will give less amountOut in swapping time
    mockuniv2.setSlippgae(50)

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
    with reverts('UniSwapV2: Excuse me, slippage. Try again with other settings'):
        tx = sandbox2.topupSandBox2( {'from':accounts[0]})

    #change settings
    mockuniv2.setSlippgae(1) # valid slippage persent 1%. MarketRegistry has 1% slippage for assets
    tx = sandbox2.topupSandBox2( {'from':accounts[0]})

    #1/3 of amount
    wbtc_to_dai_amount = before_wbtc_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    eth_to_dai_amount = before_eth_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/(100*markets.PERCENT_DENOMINATOR())

    logging.info('wbtc_to_dai_amount = {}'.format(wbtc_to_dai_amount))
    logging.info('eth_to_dai_amount = {}'.format(eth_to_dai_amount))
    logging.info('eth_balance_market = {}'.format(markets.balance()))

    #with -1% of slippage
    dai_amount_calc = wbtc_to_dai_amount*mockuniv2.rates(wbtc.address, dai.address)[1]*10**dai.decimals()/10**wbtc.decimals()*99/100 + eth_to_dai_amount*mockuniv2.rates(weth.address, dai.address)[1]*10**dai.decimals()/10**weth.decimals()*99/100
    logging.info('dai_amount_calc = {}'.format(dai_amount_calc))
    
    #logging.info(mockuniv2.getAmountsOut(eth_to_dai_amount, [weth.address,dai.address]))
    #logging.info(mockuniv2.getAmountsOut(wbtc_to_dai_amount, [wbtc.address,dai.address]))

    assert dai_amount_calc - dai.balanceOf(sandbox2)  < 1e15  #mathematical error of Solidity and python 
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount - wbtc_to_dai_amount
    assert treasury.balance() == before_eth_treasury_amount - eth_to_dai_amount

    assert tx.events['TeamShareIncreased']['Income'] - dai.balanceOf(sandbox2)*sandbox2.TEAM_PERCENT()/100 <= 1e6
    assert tx.events['TeamShareIncreased']['TeamLimit'] - dai.balanceOf(sandbox2)*sandbox2.TEAM_PERCENT()/100 <= 1e6
    assert tx.events['Sandbox2Topup']['Asset'] == dai.address
    assert tx.events['Sandbox2Topup']['TopupAmount'] == dai.balanceOf(sandbox2)

    logging.info('market eth balance = {}'.format(markets.balance()))
    logging.info('market_adapter wbtc balance = {}'.format(wbtc.balanceOf(market_adapter)))
    logging.info('dai_balance_sandbox = {}'.format(dai.balanceOf(sandbox2.address)))

    team = markets.getUBDNetworkTeamAddress()
    assert dai.allowance(sandbox2.address, team) - dai.balanceOf(sandbox2.address)*sandbox2.TEAM_PERCENT()/(100*markets.PERCENT_DENOMINATOR()) <= 1e6

    #team withdraw dai from sandbox2
    before_allowance = dai.allowance(sandbox2, team)
    dai.transferFrom(sandbox2, accounts[8], before_allowance/2, {"from": accounts[8]})
    assert dai.allowance(sandbox2, team) == before_allowance/2
    assert dai.balanceOf(accounts[8]) == before_allowance/2


    #################################################################################################
    #again topup sandbox2
    #################################################################################################
    
    logging.info('!!!!!!!!!!!!!!!!!   topup sandbox2 from treasury  - SECOND TIME   !!!!!!!!!!!!!!!')
    #add assets in treasury to increase security
    wbtc.transfer(treasury, 3*10**wbtc.decimals(), {"from": accounts[0]})

    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_dai_sandbox2 = dai.balanceOf(sandbox2)
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))
    logging.info(before_wbtc_treasury_amount)
    logging.info(before_eth_treasury_amount)
    logging.info(before_eth_treasury_amount)

    tx = sandbox2.topupSandBox2( {'from':accounts[0]})

    #1/3 of amount
    wbtc_to_dai_amount = before_wbtc_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    eth_to_dai_amount = before_eth_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/(100*markets.PERCENT_DENOMINATOR())

    logging.info('wbtc_to_dai_amount = {}'.format(wbtc_to_dai_amount))
    logging.info('eth_to_dai_amount = {}'.format(eth_to_dai_amount))
    logging.info('eth_balance_market = {}'.format(markets.balance()))


    #with -1% of slippage
    dai_amount_calc = wbtc_to_dai_amount*mockuniv2.rates(wbtc.address, dai.address)[1]*10**dai.decimals()/10**wbtc.decimals()*99/100 + eth_to_dai_amount*mockuniv2.rates(weth.address, dai.address)[1]*10**dai.decimals()/10**weth.decimals()*99/100
    logging.info('dai_amount_calc = {}'.format(dai_amount_calc))
    logging.info('dai_balance_sandbox = {}'.format(dai.balanceOf(sandbox2.address)))

    assert before_dai_sandbox2 + dai_amount_calc - dai.balanceOf(sandbox2) < 1e15  #mathematical error of Solidity and python 
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount - wbtc_to_dai_amount
    assert treasury.balance() == before_eth_treasury_amount - eth_to_dai_amount

    assert tx.events['TeamShareIncreased']['Income'] - (dai.balanceOf(sandbox2) - before_dai_sandbox2)*sandbox2.TEAM_PERCENT()/(100*markets.PERCENT_DENOMINATOR()) <= 1e6
    assert tx.events['TeamShareIncreased']['TeamLimit'] == dai.allowance(sandbox2.address, team)

    logging.info('market eth balance = {}'.format(markets.balance()))
    logging.info('market_adapter wbtc balance = {}'.format(wbtc.balanceOf(market_adapter)))
    logging.info('dai_balance_sandbox = {}'.format(dai.balanceOf(sandbox2.address)))
    logging.info(dai.allowance(sandbox2.address, team) )

    diff = dai.balanceOf(sandbox2) - before_dai_sandbox2

    assert dai.allowance(sandbox2.address, team) - before_allowance/2 - diff*sandbox2.TEAM_PERCENT()/100 < 1e6

def test_topup_treasury_from_sandbox2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth):
    
    logging.info('!!!!!!!!!!!!!!!!!   topup treasury from sandbox2    !!!!!!!!!!!!!!!')
    #desrease MinTopUp of sandbox1
    with reverts('Ownable: caller is not the owner'):
        sandbox1.setMinTopUp(990, {"from": accounts[1]})
    sandbox1.setMinTopUp(990, {"from": accounts[0]})
    chain.sleep(sandbox1.TREASURY_TOPUP_PERIOD() + 10)
    tx = sandbox1.topupTreasury({'from':accounts[1]})
    mockuniv2.setRate(dai.address, wbtc.address, (50000, 1))
    mockuniv2.setRate(dai.address, weth.address, (5000, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 5000))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 50000))

    mockuniv2.setRate(usdt.address, wbtc.address, (50000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (5000, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 50000))
    mockuniv2.setRate(weth.address, usdt.address, (1, 5000))

    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))
    tx = sandbox2.topupSandBox2( {'from':accounts[0]})

    mockuniv2.setRate(dai.address, wbtc.address, (10, 1))
    mockuniv2.setRate(dai.address, weth.address, (200, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 200))
    mockuniv2.setRate(wbtc.address, dai.address, (1, 10))

    mockuniv2.setRate(usdt.address, wbtc.address, (10, 1))
    mockuniv2.setRate(usdt.address, weth.address, (200, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 10))
    mockuniv2.setRate(weth.address, usdt.address, (1, 200))

    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))

    #set slippage for defi - defi will give less amountOut in swapping time
    mockuniv2.setSlippgae(50)
    with reverts('UniSwapV2: Excuse me, slippage. Try again with other settings'):
        tx = sandbox2.topupTreasury()

    mockuniv2.setSlippgae(1) # valid slippage persent 1%. MarketRegistry has 1% slippage for assets

    #topup treasury from sandbox2 - 1% of dai - to wbtc and eth 50x50
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_dai_sandbox2_amount = dai.balanceOf(sandbox2.address)

    # add call constant with percent!!!!
    logging.info('dai to exchange = {}'.format(before_dai_sandbox2_amount/100))
    logging.info('sandbox2 dai balance  = {}'.format(dai.balanceOf(sandbox2)))
    assert sandbox2.lastTreasuryTopUp() == 0
    tx = sandbox2.topupTreasury()
    assert tx.return_value == True
    assert sandbox2.lastTreasuryTopUp() > 0


    ##need call of constant from contract with topup percent - wait appearing it!! and 1% of slippage in defi
    wbtc_amount_calc = (before_dai_sandbox2_amount*10**wbtc.decimals()/mockuniv2.rates(dai, wbtc)[0]/10**dai.decimals()/2/100)*99/100
    eth_amount_calc = (before_dai_sandbox2_amount*10**weth.decimals()/mockuniv2.rates(dai, weth)[0]/10**dai.decimals()/2/100)*99/100

    assert dai.balanceOf(sandbox2) - before_dai_sandbox2_amount*99/100  <2e8
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount + wbtc_amount_calc
    assert  before_eth_treasury_amount + eth_amount_calc - treasury.balance()  < 1e4


def test_redeem_for_sandbox1(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth):

    ubd.approve(sandbox1, 100000*10**ubd.decimals(), {"from": accounts[0]})
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))

    #set slippage for defi - defi will give less amountOut in swapping time
    mockuniv2.setSlippgae(50)

    #only redeem Sandbox1 - without swap
    with reverts('UniSwapV2: Excuse me, slippage. Try again with other settings'):
        tx = sandbox1.swapExactInput(ubd.address, 
                                100000*10**ubd.decimals(),
                                0,
                                100000*10**usdt.decimals())

    mockuniv2.setSlippgae(1) # valid slippage persent 1%. MarketRegistry has 1% slippage for assets

    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_usdt_sandbox1_amount = usdt.balanceOf(sandbox1)
    wbtc_to_swap = before_wbtc_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    eth_to_swap = before_eth_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/(100*markets.PERCENT_DENOMINATOR())
    
    #and 1% of defi slippage of usdt
    usdt_amount_calc = (wbtc_to_swap*mockuniv2.rates(wbtc.address, usdt.address)[1]*10**usdt.decimals()/10**wbtc.decimals() + eth_to_swap*mockuniv2.rates(weth.address, usdt.address)[1]*10**usdt.decimals()/10**weth.decimals())*99/100

    #redeem only - topup sandbox1 from treasury
    tx = sandbox1.swapExactInput(ubd.address, 
                                100000*10**ubd.decimals(),
                                0,
                                100000*10**usdt.decimals())

    assert tx.events['Sandbox1Redeem']['Asset'] == usdt.address
    assert tx.events['Sandbox1Redeem']['TopupAmount'] ==  usdt.balanceOf(sandbox1) - before_usdt_sandbox1_amount

    assert wbtc.balanceOf(treasury) - before_wbtc_treasury_amount + wbtc_to_swap == 0 #< 10
    assert treasury.balance() + eth_to_swap - before_eth_treasury_amount < 10
    assert before_usdt_sandbox1_amount + usdt_amount_calc == usdt.balanceOf(sandbox1) 



    
    
    



