import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

USDT_AMOUNT = 1000e6
UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def test_usdt_to_ubd(accounts, ubd_exch, exchange_single, usdt, dai):
    global USDT_AMOUNT
    #prepare data
    
    #check calcOutUBDForExactInBASE
    fee_percent = exchange_single.paymentTokens(usdt.address)[1]/exchange_single.PERCENT_DENOMINATOR()

    exchange_single.setUBDToken(ubd_exch, {'from':accounts[0]})
    exchange_single.setBeneficiary(accounts[1], {'from':accounts[0]})

    outAmount_ubd = exchange_single.calcOutUBDForExactInBASE(USDT_AMOUNT)

    fee = round(USDT_AMOUNT*fee_percent/(100+fee_percent))
    calcOutAmount_ubd = (USDT_AMOUNT-fee)*10**ubd_exch.decimals()/10**usdt.decimals()

    assert outAmount_ubd == calcOutAmount_ubd


    chain.sleep(10)
    
    logging.info('paymentTokens(usdt): {}, chain.time {}'.format(
        exchange_single.paymentTokens(usdt), chain.time() 
    ))
    logging.info('paymentTokens(ubd): {}, chain.time {}'.format(
        exchange_single.paymentTokens(ubd_exch), chain.time() 
    ))
    
    #check calcInBASEForExactOutUBD
    #!!!!REVERT
    calcInAmount_usdt = exchange_single.calcInBASEForExactOutUBD(outAmount_ubd)
    assert USDT_AMOUNT == calcInAmount_usdt

    #check calcOutBASEForExactInUBD
    fee_percent = exchange_single.paymentTokens(ubd_exch.address)[1]/exchange_single.PERCENT_DENOMINATOR()
    outAmount_usdt = exchange_single.calcOutBASEForExactInUBD(UBD_AMOUNT)

    fee = round(UBD_AMOUNT*fee_percent/(100+fee_percent))
    calcOutAmount_usdt = (UBD_AMOUNT-fee)*10**usdt.decimals()/10**ubd_exch.decimals()

    assert outAmount_usdt == calcOutAmount_usdt

    #check calcInUBDForExactOutBASE
    calcInAmount_ubd = exchange_single.calcInUBDForExactOutBASE(outAmount_usdt)

    assert UBD_AMOUNT - calcInAmount_ubd <= 10**13






