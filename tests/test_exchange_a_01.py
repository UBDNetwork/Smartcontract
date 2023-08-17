import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1005e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def test_usdt_to_ubd(accounts, ubd_exch, exchange_single, usdt, dai):
    with reverts("Ownable: caller is not the owner"):
        exchange_single.setUBDToken(ubd_exch, {'from':accounts[1]})
    exchange_single.setUBDToken(ubd_exch, {'from':accounts[0]})
    with reverts("Ownable: caller is not the owner"):
        exchange_single.setBeneficiary(accounts[1], {'from':accounts[1]})
    exchange_single.setBeneficiary(accounts[1], {'from':accounts[0]})
    
    usdt.transfer(accounts[2], PAY_AMOUNT, {'from':accounts[0]})
    usdt.approve(exchange_single, PAY_AMOUNT, {'from':accounts[2]})
    

    #receiver<>msg.sender
    tx = exchange_single.swapExactInput(
        usdt, 
        PAY_AMOUNT,
        0,
        0,
        accounts[2], 
        {'from':accounts[0]}
    )

    #logging.info('tx: {}'.format(tx.infwo()))
    '''assert tx.return_value == MINT_UBD_AMOUNT
    assert ubd_exch.balanceOf(accounts[2]) == MINT_UBD_AMOUNT

    dai.approve(exchange_single, PAY_AMOUNT, {'from':accounts[2]})

    #use not allowed payment token
    with reverts(""):
        tx = exchange_single.swapExactInput(
            dai, 
            PAY_AMOUNT,
            0,
            0,
            ZERO_ADDRESS, 
            {'from':accounts[0]}
        )
    logging.info(tx.revert_msg)'''
    


