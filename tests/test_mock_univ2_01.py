import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

AMOUNT_IN_USDT = 28_000e6
AMOUNT_OUT_WBTC = 1e8
AMOUNT_OUT_ETH = 20e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
def test_mock_univ2_swapExactTokensForTokens(accounts, mockuniv2, dai, usdt, wbtc, weth, ubd):
    
    usdt.approve(mockuniv2, AMOUNT_IN_USDT, {'from':accounts[0]})
    
    acc0_usdt_before = usdt.balanceOf(accounts[0])
    acc1_wbtc_befroe = wbtc.balanceOf(accounts[1])
    tx = mockuniv2.swapExactTokensForTokens(
        AMOUNT_IN_USDT, 
        0,
        [usdt, wbtc],
        accounts[1],
        chain.time()*100, 
        {'from':accounts[0]}
    )
    [logging.info('\nfrom:{} to:{} value:{}'.format(x['from'],x['to'],x['value'])) for x in tx.events['Transfer']]
    
    assert usdt.balanceOf(accounts[0]) == acc0_usdt_before - AMOUNT_IN_USDT
    assert wbtc.balanceOf(accounts[1]) == acc1_wbtc_befroe + AMOUNT_OUT_WBTC

def test_mock_univ2_swapExactTokensForETH(accounts, mockuniv2, dai, usdt, wbtc, weth, ubd):
    
    usdt.approve(mockuniv2, AMOUNT_IN_USDT, {'from':accounts[0]})
    accounts[9].transfer(mockuniv2, accounts[9].balance()-1e18)
    
    acc0_usdt_before = usdt.balanceOf(accounts[0])
    acc1_eth_befroe = accounts[1].balance()
    tx = mockuniv2.swapExactTokensForETH(
        AMOUNT_IN_USDT, 
        0,
        [usdt, weth],
        accounts[1],
        chain.time()*100, 
        {'from':accounts[0]}
    )
    [logging.info('\nfrom:{} to:{} value:{}'.format(x['from'],x['to'],x['value'])) for x in tx.events['Transfer']]
    
    assert usdt.balanceOf(accounts[0]) == acc0_usdt_before - AMOUNT_IN_USDT
    assert accounts[1].balance() == acc1_eth_befroe + AMOUNT_OUT_ETH    
