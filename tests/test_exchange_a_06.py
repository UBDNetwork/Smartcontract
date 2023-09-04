import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1000e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def test_usdt_to_ubd(accounts, ubd_exch, exchange_single, usdt, dai):
    global PAY_AMOUNT
    #prepare data
    
    exchange_single.setUBDToken(ubd_exch, {'from':accounts[0]})
    exchange_single.setBeneficiary(accounts[1], {'from':accounts[0]})

    logging.info(exchange_single.paymentTokens(ubd_exch))
    logging.info(exchange_single.paymentTokens(usdt))\

    chain.sleep(10)
    chain.mine()

    tx = exchange_single.swapExactInput(
            usdt, 
            0,
            0,
            0,
            accounts[2], 
            {'from':accounts[0]}
        )

    tx = exchange_single.swapExactInput(
            ubd_exch, 
            0,
            0,
            0,
            accounts[2], 
            {'from':accounts[0]}
        )
    
    logging.info(exchange_single.paymentTokens(ubd_exch))