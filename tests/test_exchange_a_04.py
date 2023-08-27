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

    with reverts("Ownable: caller is not the owner"):
        exchange_single.setGuardianStatus(accounts[1], True, {"from": accounts[1]})
    exchange_single.setGuardianStatus(accounts[1], True, {"from": accounts[0]})

    with reverts("Only for approved guardians"):
        exchange_single.emergencyPause(usdt.address, {"from": accounts[0]})

    tx = exchange_single.emergencyPause(usdt.address, {"from": accounts[1]})
    assert tx.events['PaymentTokenPaused']['Token'] == usdt.address
    assert tx.events['PaymentTokenPaused']['Until'] >=chain.time() + exchange_single.EMERGENCY_PAYMENT_PAUSE() - 1

    assert exchange_single.paymentTokens(usdt.address)[1] == exchange_single.FEE_EXCHANGE_DEFAULT()
    assert exchange_single.paymentTokens(usdt.address)[0] > chain.time()
    assert exchange_single.paymentTokens(usdt.address)[0] < chain.time() + exchange_single.EMERGENCY_PAYMENT_PAUSE() + 1

    time_unlock = exchange_single.paymentTokens(usdt.address)[0]

    usdt.approve(exchange_single.address, PAY_AMOUNT, {'from':accounts[0]})
    with reverts("Token paused or timelocked"):
        tx = exchange_single.swapExactInput(
                    usdt, 
                    PAY_AMOUNT,
                    0,
                    0,
                    ZERO_ADDRESS, 
                    {'from':accounts[0]}
                )
    
    chain.sleep(10)
    chain.mine()

    #nothing was changed
    tx = exchange_single.emergencyPause(usdt.address, {"from": accounts[1]})
    assert exchange_single.paymentTokens(usdt.address)[0] == time_unlock

    tx = exchange_single.setPaymentTokenStatus(usdt.address, False, 0, {"from": accounts[0]})
    assert exchange_single.paymentTokens(usdt.address)[0] == 0
    tx = exchange_single.emergencyPause(usdt.address, {"from": accounts[1]})
    assert exchange_single.paymentTokens(usdt.address)[0] == 0





