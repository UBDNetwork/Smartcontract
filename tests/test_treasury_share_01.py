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
    sandbox1.setBeneficiary(accounts[2], {'from':accounts[0]})
    chain.sleep(10)
    
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
    


def test_usdt_to_ubd_100k(accounts, ubd, sandbox1, usdt):
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
    #assert ubd.balanceOf(accounts[0]) == MINT_UBD_AMOUNT * 100

#def test_init_market(accounts, ubd, sandbox1, sandbox2, treasury, usdt):

def test_topup_treasury(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    logging.info(
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{}'
        '\ntreasury.balance(eth):{}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury) / 1e8,
            Wei(treasury.balance()).to('ether')
    ))
    logging.info('UBDNetwork.state:{}'.format(markets.ubdNetwork()))
    init_market_registry(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury, 
        ubd, markets, wbtc, market_adapter, weth, usdc
    )

    logging.info('UBDNetwork.state:{}'.format(markets.getUBDNetworkInfo()))
    logging.info('Treasury assets:{}'.format(markets.treasuryERC20Assets()))
    accounts[7].transfer(mockuniv2, 40e18)

    tx = sandbox1.topupTreasury({'from':accounts[1]})
    logging.info('Ether transfer:{}'.format(tx.events['ReceivedEther']))
    [logging.info('\nfrom:{} to:{} value:{}'.format(x['from'],x['to'],x['value'])) for x in tx.events['Transfer']]
    logging.info(
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{} ({})'
        '\ntreasury.balance(eth):{} ({})'
        '\ngetBalanceInStableUnits: {}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury) / 1e8, markets.getAmountOut(wbtc.balanceOf(treasury), [wbtc, usdt]),
            Wei(treasury.balance()).to('ether'), markets.getAmountOut(treasury.balance(), [weth, usdt]),
            Wei(markets.getBalanceInStable18(treasury, [wbtc, weth])).to('ether')
    ))
    t2 = markets.getActualAssetsSharesM100()
    logging.info('Actual shares: {}'.format(t2))
    
    accounts[0].transfer(treasury, 2e18)
    t = markets.getActualAssetsSharesM100()
    logging.info('Plus Ether Actual shares: {}'.format(t))
    
    logging.info(
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{} ({})'
        '\ntreasury.balance(eth):{} ({})'
        '\ngetBalanceInStableUnits: {}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury) / 1e8, markets.getAmountOut(wbtc.balanceOf(treasury), [wbtc, usdt]),
            Wei(treasury.balance()).to('ether'), markets.getAmountOut(treasury.balance(), [weth, usdt]),
            Wei(markets.getBalanceInStable18(treasury, [wbtc, weth])).to('ether')
    ))

    tx = markets.rebalance({'from':accounts[0]})
    t = markets.getActualAssetsSharesM100()
    logging.info(
        '\n rebalancing 1...'
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{} ({})'
        '\ntreasury.balance(eth):{} ({})'
        '\ngetBalanceInStableUnits: {}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury) / 1e8, markets.getAmountOut(wbtc.balanceOf(treasury), [wbtc, usdt]),
            Wei(treasury.balance()).to('ether'), markets.getAmountOut(treasury.balance(), [weth, usdt]),
            Wei(markets.getBalanceInStable18(treasury, [wbtc, weth])).to('ether')
    ))
    logging.info('After rebalancing 1 Actual shares: {}'.format(t))

    tx = markets.rebalance({'from':accounts[0]})
    t = markets.getActualAssetsSharesM100()
    
    logging.info(
        '\n rebalancing 2...'
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{} ({})'
        '\ntreasury.balance(eth):{} ({})'
        '\ngetBalanceInStableUnits: {}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury) / 1e8, markets.getAmountOut(wbtc.balanceOf(treasury), [wbtc, usdt]),
            Wei(treasury.balance()).to('ether'), markets.getAmountOut(treasury.balance(), [weth, usdt]),
            Wei(markets.getBalanceInStable18(treasury, [wbtc, weth])).to('ether')
    ))
    logging.info('After rebalancing 2 Actual shares: {}'.format(t))
    wwww