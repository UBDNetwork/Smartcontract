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
    
    #check calcOutUBDForExactInBASE
    fee_percent = exchange_single.paymentTokens(usdt.address)[1]/exchange_single.PERCENT_DENOMINATOR()

    exchange_single.setUBDToken(ubd_exch, {'from':accounts[0]})
    exchange_single.setBeneficiary(accounts[1], {'from':accounts[0]})

    outAmount = exchange_single.calcOutUBDForExactInBASE(PAY_AMOUNT)

    fee = round(PAY_AMOUNT*fee_percent/(100+fee_percent))
    calcOutAmount = (PAY_AMOUNT-fee)*10**ubd_exch.decimals()/10**usdt.decimals()

    assert outAmount == calcOutAmount

    #check calcInBASEForExactOutUBD
    calcInAmount = exchange_single.calcInBASEForExactOutUBD(outAmount)
    assert PAY_AMOUNT == calcOutAmount




