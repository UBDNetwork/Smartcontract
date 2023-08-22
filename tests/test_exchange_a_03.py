import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1000e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def test_usdt_to_ubd(accounts, ubd_exch, exchange_single, usdt):
    global PAY_AMOUNT
    #prepare data
    
    exchange_single.setUBDToken(ubd_exch, {'from':accounts[0]})
    exchange_single.setBeneficiary(accounts[1], {'from':accounts[0]})

    with reverts("Ownable: caller is not the owner"):
        exchange_single.setPaymentTokenStatus(usdt.address, False, 0, {"from": accounts[1]})
    exchange_single.setPaymentTokenStatus(usdt.address, False, 0, {"from": accounts[0]})
    assert exchange_single.paymentTokens(usdt.address)[0] == 0
    assert exchange_single.paymentTokens(usdt.address)[1] == 0

    usdt.transfer(accounts[2], PAY_AMOUNT, {'from':accounts[0]})
    usdt.approve(exchange_single.address, PAY_AMOUNT, {'from':accounts[2]})
    usdt.approve(exchange_single.address, PAY_AMOUNT, {'from':accounts[2]})
    
    #switch of usdt
    tx = exchange_single.swapExactInput(
            usdt, 
            PAY_AMOUNT,
            0,
            PAY_AMOUNT*10**ubd_exch.decimals()/10**usdt.decimals(),
            accounts[2], 
            {'from':accounts[0]}
        )
    logging.info(tx.return_value)

    #try to switch ubd token
    with reverts("Cant disable UBD"):
        exchange_single.setPaymentTokenStatus(ubd_exch.address, False, 0, {"from": accounts[0]})


    exchange_single.setPaymentTokenStatus(ubd_exch.address, True, exchange_single.FEE_EXCHANGE_DEFAULT()-1000, {"from": accounts[0]})
    assert exchange_single.paymentTokens(ubd_exch)[1] == exchange_single.FEE_EXCHANGE_DEFAULT()-1000
    assert exchange_single.paymentTokens(ubd_exch)[0] <= chain.time() + exchange_single.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()
    assert exchange_single.paymentTokens(ubd_exch)[0] > chain.time() + exchange_single.ADD_NEW_PAYMENT_TOKEN_TIMELOCK() - 10

    logging.info(exchange_single.ADD_NEW_PAYMENT_TOKEN_TIMELOCK())

    with reverts("Fee is too much"):
        exchange_single.setPaymentTokenStatus(ubd_exch.address, True, exchange_single.FEE_EXCHANGE_DEFAULT()*4, {"from": accounts[0]})