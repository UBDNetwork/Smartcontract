import pytest
import logging
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1005e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
WBTC_TREASURY_BALANCE = 3e8
ETH_TREASURY_BALANCE = 10e18
CALC_TREASURY_BALANCE_IN_STABLE = WBTC_TREASURY_BALANCE / 1e8 * 28000 + ETH_TREASURY_BALANCE / 1e18 * 1400
def test_usdt_to_ubd(accounts, ubd, sandbox1, usdt):
    sandbox1.setUBDToken(ubd, {'from':accounts[0]})
    sandbox1.setBeneficiary(accounts[2], {'from':accounts[0]})
    
    usdt.approve(sandbox1, PAY_AMOUNT, {'from':accounts[0]})
    logging.info('Calculated UBD amount: {}'.format(
        sandbox1.calcOutUBDForExactInBASE(PAY_AMOUNT))
    )

    chain.sleep(10)
    logging.info('paymentTokens(usdt): {}, chain.time {}'.format(
        sandbox1.paymentTokens(usdt), chain.time() 
    ))
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    #logging.info('tx: {}'.format(tx.infwo()))
    assert tx.return_value == MINT_UBD_AMOUNT
    assert ubd.balanceOf(accounts[0]) == MINT_UBD_AMOUNT
    


def test_usdt_to_ubd_100k(accounts, ubd, sandbox1, usdt, wbtc, treasury):
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
    assert ubd.balanceOf(accounts[0]) == MINT_UBD_AMOUNT * 100 + MINT_UBD_AMOUNT
    logging.info(
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{}'
        '\ntreasury.balance(eth):{}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury),
            Wei(treasury.balance()).to('ether')
    ))

#def test_init_market(accounts, ubd, sandbox1, sandbox2, treasury, usdt):
def test_treasuryERC20Assets(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    
    
    #logging.info('UBDNetwork.state:{}'.format(markets.ubdNetwork()))
    init_market_registry(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury, 
        ubd, markets, wbtc, market_adapter, weth, usdc
    )
    wtx = wbtc.transfer(treasury, WBTC_TREASURY_BALANCE, {'from': accounts[0]})
    tx = accounts[0].transfer(treasury, ETH_TREASURY_BALANCE)
    logging.info('Ether transfer:{}'.format(tx.events['ReceivedEther']))
    logging.info('WBTC transfer:{}'.format(wtx.events['Transfer']))
    
    assert markets.treasuryERC20Assets() == [wbtc.address]
    logging.info(
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{}'
        '\ntreasury.balance(eth):{}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury),
            treasury.balance()
    ))

def test_getBalanceInStableUnits(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):

    logging.info('UBDNetwork.state:{}'.format(markets.getUBDNetworkInfo()))
    logging.info('getBalanceInStableUnits(accounts[0]):{}'.format(markets.getBalanceInStableUnits(
        accounts[0], [wbtc.address]
    )))
    logging.info('getBalanceInStableUnits(treasury):{}'.format(markets.getBalanceInStableUnits(
        treasury, [wbtc.address]
    )))

    logging.info('getBalanceInStableUnits(accounts[6]):{}'.format(markets.getBalanceInStableUnits(
        accounts[6], [wbtc.address]
    )))
    assert CALC_TREASURY_BALANCE_IN_STABLE == markets.getBalanceInStableUnits(treasury, [wbtc.address])

def test_getCollateralLevelM10(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    col_level = markets.getCollateralLevelM10()
    logging.info('getCollateralLevelM10:{}'.format(col_level))
    coll_calculated = int(
        (usdt.balanceOf(sandbox1) / 1e6  +  CALC_TREASURY_BALANCE_IN_STABLE) * 10 / (ubd.totalSupply()/ 1e18)
    )
    assert col_level == coll_calculated

# Sandbox1.balance(usdt):101000_000000
# treasury.balance(wbtc):3_00000000
# treasury.balance(eth):10_000000000000000000