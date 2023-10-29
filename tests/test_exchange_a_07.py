import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

USDT_AMOUNT = 0
UBD_AMOUNT = 0
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def test_usdt_to_ubd(accounts, ubd_exch, exchange_single, usdt, dai):
    global USDT_AMOUNT
    #prepare data
    
    #check calcOutUBDForExactInBASE
    fee_percent = exchange_single.paymentTokens(usdt.address)[1]/exchange_single.PERCENT_DENOMINATOR()

    exchange_single.setUBDToken(ubd_exch, {'from':accounts[0]})
    exchange_single.setBeneficiary(accounts[1], {'from':accounts[0]})

    outAmount_ubd = exchange_single.calcOutUBDForExactInBASE(USDT_AMOUNT)

    fee = USDT_AMOUNT*fee_percent/(100+fee_percent)
    calcOutAmount_ubd = (USDT_AMOUNT-fee)*10**ubd_exch.decimals()/10**usdt.decimals()

    assert outAmount_ubd - calcOutAmount_ubd < 10**13


    chain.sleep(10)
    
    logging.info('paymentTokens(usdt): {}, chain.time {}'.format(
        exchange_single.paymentTokens(usdt), chain.time() 
    ))
    logging.info('paymentTokens(ubd): {}, chain.time {}'.format(
        exchange_single.paymentTokens(ubd_exch), chain.time() 
    ))
    
    
    #check calcInBASEForExactOutUBD
    inAmount_usdt = exchange_single.calcInBASEForExactOutUBD(outAmount_ubd)
    #logging.info(inAmount_usdt)
    assert USDT_AMOUNT == inAmount_usdt

    #check calcOutBASEForExactInUBD
    fee_percent = exchange_single.paymentTokens(ubd_exch.address)[1]/exchange_single.PERCENT_DENOMINATOR()
    outAmount_usdt = exchange_single.calcOutBASEForExactInUBD(UBD_AMOUNT)
    #logging.info(outAmount_usdt)

    fee = UBD_AMOUNT*fee_percent/(100+fee_percent)
    calcOutAmount_usdt = (UBD_AMOUNT-fee)*10**usdt.decimals()/10**ubd_exch.decimals()

    assert outAmount_usdt == calcOutAmount_usdt

    #check calcInUBDForExactOutBASE
    #logging.info(outAmount_usdt)
    inAmount_ubd = exchange_single.calcInUBDForExactOutBASE(outAmount_usdt)
    #logging.info(inAmount_ubd)

    assert UBD_AMOUNT - inAmount_ubd < 10**13

def test_usdt_to_ubd(accounts, ubd_exch, exchange_single):
    
    exchange_single.setUBDToken(ubd_exch, {'from':accounts[0]})

    with reverts("Ownable: caller is not the owner"):
        exchange_single.setStakingContract(accounts[1], True, {"from": accounts[1]})
    exchange_single.setStakingContract(accounts[1], True, {"from": accounts[0]})

    with reverts("Only for staking reward"):
        exchange_single.mintReward(accounts[0], 1, {"from": accounts[0]})

    exchange_single.mintReward(accounts[2], 1, {"from": accounts[1]})
    assert ubd_exch.balanceOf(accounts[2]) == 1






