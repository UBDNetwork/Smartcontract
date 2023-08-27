import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

AMOUNT_IN_USDT = 1000e6
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
def test_mock_univ2_swapExactTokensForTokens(accounts, mockuniv2, dai, usdt, wbtc, weth, ubd):
    
    usdt.approve(mockuniv2, AMOUNT_IN_USDT, {'from':accounts[0]})
    

    tx = mockuniv2.swapExactTokensForTokens(
        AMOUNT_IN_USDT, 
        0,
        [usdt, wbtc],
        accounts[1],
        chain.time()*100, 
        {'from':accounts[0]}
    )
    #[x for x in tx.events]
    logging.info('tx.events: {}'.format(
        tx.events
    ))
    #logging.info('tx: {}'.format(tx.infwo()))
    #assert tx.return_value == MINT_UBD_AMOUNT
    #assert ubd_exch.balanceOf(accounts[0]) == MINT_UBD_AMOUNT
    
