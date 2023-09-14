import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1000e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def test_usdt_to_ubd(accounts, ubd_exch, exchange_single, usdt, sandbox1, ubd):
    global PAY_AMOUNT
    #prepare data
    fee_percent = sandbox1.paymentTokens(usdt.address)[1]/sandbox1.PERCENT_DENOMINATOR()

    exchange_single.setUBDToken(ubd_exch, {'from':accounts[0]})
    exchange_single.setBeneficiary(accounts[1], {'from':accounts[0]})

    usdt.transfer(accounts[2], PAY_AMOUNT, {'from':accounts[0]})
    usdt.approve(sandbox1.address, PAY_AMOUNT, {'from':accounts[2]})
    usdt.approve(exchange_single.address, PAY_AMOUNT, {'from':accounts[2]})
    
    #too big amountOutMin
    with reverts("Unexpected Out Amount"):
        tx = exchange_single.swapExactInput(
            usdt, 
            PAY_AMOUNT,
            0,
            PAY_AMOUNT*10**ubd_exch.decimals()/10**usdt.decimals(),
            accounts[2], 
            {'from':accounts[0]}
        )

    with reverts("Unexpected Transaction time"):
        tx = exchange_single.swapExactInput(
            usdt, 
            PAY_AMOUNT,
            1,
            0,
            accounts[2], 
            {'from':accounts[0]}
        )

    sandbox1.setUBDToken(ubd, {'from':accounts[0]})
    sandbox1.setBeneficiary(accounts[1], {'from':accounts[0]})

    tx = sandbox1.swapExactInput(
            usdt, 
            PAY_AMOUNT,
            0,
            0,
            accounts[2], 
            {'from':accounts[0]}
        )

    PAY_AMOUNT = ubd.balanceOf(accounts[2])
    ubd.approve(sandbox1.address, PAY_AMOUNT, {'from':accounts[2]})
    usdt_out_amount = round(PAY_AMOUNT*100/(100+fee_percent))*10**usdt.decimals()/10**ubd_exch.decimals()

    tx = sandbox1.swapExactInput(
        ubd, 
        PAY_AMOUNT,
        0,
        0,
        accounts[2], 
        {'from':accounts[0]}
    )

    assert usdt.balanceOf(accounts[2]) == usdt_out_amount




    