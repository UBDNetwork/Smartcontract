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
        treasury, ubd, markets, wbtc, market_adapter, weth):
    logging.info('UBDNetwork.state:{}'.format(markets.ubdNetwork()))
    init_market_registry(accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury, ubd, markets, wbtc, market_adapter, weth)
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
    
    

    #mockuniv2.setRate(wbtc.address, usdt.address, (1, 200000000))
    #mockuniv2.setRate(weth.address, usdt.address, (1,  2000000))

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

    #bullrun
    mockuniv2.setRate(usdt.address, wbtc.address, (100000, 1))
    mockuniv2.setRate(usdt.address, weth.address, (10000, 1))

    #assert treasury.isReadyForTopupSandBox2() == True
    logging.info(mockuniv2.getAmountsOut(wbtc.balanceOf(treasury), [wbtc.address,usdt.address]))
    logging.info(mockuniv2.getAmountsOut(treasury.balance(), [weth.address,usdt.address]))
    logging.info(usdt.balanceOf(sandbox1.address))
    logging.info(ubd.totalSupply())




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





