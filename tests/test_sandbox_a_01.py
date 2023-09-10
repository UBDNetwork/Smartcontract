import pytest
import logging
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1005e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
def test_usdt_to_ubd(accounts, ubd, sandbox1, usdt):
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

def test_topup_treasury2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth):
    
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

    markets.topupSandBox2()
    #tx = treasury.sendEtherForRedeem(treasury.SANDBOX2_TOPUP_PERCENT())

    #1/3 of amount
    wbtc_to_dai_amount = before_wbtc_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/100
    eth_to_dai_amount = before_eth_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/100

    logging.info('wbtc_to_dai_amount = {}'.format(wbtc_to_dai_amount))
    logging.info('eth_to_dai_amount = {}'.format(eth_to_dai_amount))
    logging.info('eth_balance_market = {}'.format(markets.balance()))

    dai_amount_calc = wbtc_to_dai_amount*mockuniv2.rates(dai.address, wbtc.address)[0]*10**dai.decimals()/10**wbtc.decimals() + eth_to_dai_amount*mockuniv2.rates(weth.address, dai.address)[1]*10**dai.decimals()/10**weth.decimals()
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
    assert dai.allowance(sandbox2.address, team) == dai.balanceOf(sandbox2.address)*markets.TEAM_PERCENT()/100


    


    '''logging.info(
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
    assert (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, weth.address)[0])*10**weth.decimals()/10**usdt.decimals() - treasury.balance()  <= 3000000000000'''

    
'''def test_ubd_to_usdt(accounts, ubd, sandbox1, usdt):
    fee_percent = sandbox1.paymentTokens(ubd.address)[1]/sandbox1.PERCENT_DENOMINATOR()

    logging.info(usdt.balanceOf(sandbox1))
    ubd.approve(sandbox1, MINT_UBD_AMOUNT, {'from':accounts[0]})
    tx = sandbox1.swapExactInput(
        ubd, 
        MINT_UBD_AMOUNT,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    logging.info('tx.return_value: {}'.format(tx.return_value))
    usdt_balance = usdt.balanceOf(sandbox1)
    logging.info('USDT.balanceOf(SANDBOX1): {}'.format(
        usdt_balance
    ))
    assert ubd.balanceOf(accounts[0]) == 0
    assert usdt.balanceOf(sandbox1) - (MINT_UBD_AMOUNT*fee_percent/(100+fee_percent))*10**usdt.decimals()/10**ubd.decimals() <= 1'''

'''def test_usdt_to_ubd_100k(accounts, ubd, sandbox1, usdt):
    usdt.approve(sandbox1, PAY_AMOUNT * 100, {'from':accounts[0]})
    logging.info('Calculated UBD amount: {}'.format(
        sandbox1.calcOutUBDForExactInBASE(PAY_AMOUNT * 100))
    )
    
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT * 100,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    #logging.info('tx: {}'.format(tx.infwo()))
    assert tx.return_value == MINT_UBD_AMOUNT * 100
    assert ubd.balanceOf(accounts[0]) == MINT_UBD_AMOUNT * 100'''





