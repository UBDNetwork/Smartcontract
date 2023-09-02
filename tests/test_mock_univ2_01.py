import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

AMOUNT_IN_USDT = 28_000e6
AMOUNT_IN_DAI = 28_000e18
AMOUNT_OUT_WBTC = 1e8
AMOUNT_IB_WBTC = 1e8
AMOUNT_OUT_ETH = 20e18
AMOUNT_IN_ETH = 2e18
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

def test_mock_univ2_swapExactTokensForTokens_back(accounts, mockuniv2, dai, usdt, wbtc, weth, ubd):
    
    wbtc.approve(mockuniv2, AMOUNT_IN_USDT, {'from':accounts[1]})
    
    acc1_usdt_before = usdt.balanceOf(accounts[1])
    acc1_wbtc_befroe = wbtc.balanceOf(accounts[1])
    tx = mockuniv2.swapExactTokensForTokens(
        AMOUNT_OUT_WBTC, 
        0,
        [wbtc, usdt],
        accounts[1],
        chain.time()*100, 
        {'from':accounts[1]}
    )
    [logging.info('\nfrom:{} to:{} value:{}'.format(x['from'],x['to'],x['value'])) for x in tx.events['Transfer']]
    
    assert usdt.balanceOf(accounts[1]) == acc1_usdt_before + AMOUNT_IN_USDT
    assert wbtc.balanceOf(accounts[1]) == acc1_wbtc_befroe - AMOUNT_OUT_WBTC

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

def test_mock_univ2_swapExactTokensForETH_2(accounts, mockuniv2, dai, usdt, wbtc, weth, ubd):
    
    dai.approve(mockuniv2, AMOUNT_IN_DAI, {'from':accounts[0]})
    accounts[9].transfer(mockuniv2, accounts[9].balance()-1e18)
    
    acc0_dai_before = dai.balanceOf(accounts[0])
    acc1_eth_befroe = accounts[1].balance()
    tx = mockuniv2.swapExactTokensForETH(
        AMOUNT_IN_DAI, 
        0,
        [dai, weth],
        accounts[1],
        chain.time()*100, 
        {'from':accounts[0]}
    )
    [logging.info('\nfrom:{} to:{} value:{}'.format(x['from'],x['to'],x['value'])) for x in tx.events['Transfer']]
    
    assert dai.balanceOf(accounts[0]) == acc0_dai_before - AMOUNT_IN_DAI
    assert accounts[1].balance() == acc1_eth_befroe + AMOUNT_OUT_ETH    


def test_mock_univ2_swapExactETHForTokens(accounts, mockuniv2, dai, usdt, wbtc, weth, ubd):
    dai.transfer(mockuniv2, AMOUNT_IN_ETH / 1800e18)
    accounts[9].transfer(mockuniv2, accounts[9].balance()-1e18)
    acc1_dai_before = dai.balanceOf(accounts[1])
    acc0_eth_befroe = accounts[0].balance()

    tx = mockuniv2.swapExactETHForTokens(
        0,
        [weth, dai],
        accounts[1],
        chain.time()*100, 
        {'from':accounts[0], 'value': AMOUNT_IN_ETH}
    )
    [logging.info('\nfrom:{} to:{} value:{}'.format(x['from'],x['to'],x['value'])) for x in tx.events['Transfer']]

    assert accounts[0].balance() == acc0_eth_befroe - AMOUNT_IN_ETH
    assert dai.balanceOf(accounts[1]) == acc1_dai_before + AMOUNT_IN_DAI/10

def test_mock_univ2_getAmountsOut(accounts, mockuniv2, dai, usdt, wbtc, weth, ubd):
    # swap ETH for other
    assert mockuniv2.getAmountsOut(AMOUNT_IN_ETH /2, [weth, dai]) == (AMOUNT_IN_ETH /2, 1400e18)
    assert mockuniv2.getAmountsOut(AMOUNT_IN_DAI , [dai, weth]) == (AMOUNT_IN_DAI, 20e18)

    assert mockuniv2.getAmountsOut(AMOUNT_IN_ETH /2, [weth, usdt]) == (AMOUNT_IN_ETH /2, 1400e6)
    assert mockuniv2.getAmountsOut(AMOUNT_IN_USDT , [usdt, weth]) == (AMOUNT_IN_USDT, 20e18)

    # swap WBTC
    assert mockuniv2.getAmountsOut(AMOUNT_IB_WBTC, [wbtc, usdt]) == (AMOUNT_IB_WBTC, 28_000e6)
    assert mockuniv2.getAmountsOut(AMOUNT_IN_USDT , [usdt, wbtc]) == (AMOUNT_IN_USDT, 1e8)

    assert mockuniv2.getAmountsOut(AMOUNT_IB_WBTC, [wbtc, dai]) == (AMOUNT_IB_WBTC, 28_000e18)
    assert mockuniv2.getAmountsOut(AMOUNT_IN_DAI , [dai, wbtc]) == (AMOUNT_IN_DAI, 1e8)
