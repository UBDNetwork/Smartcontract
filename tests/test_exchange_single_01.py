import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1005e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
def test_usdt_to_ubd(accounts, ubd_exch, exchange_single, usdt):
    exchange_single.setUBDToken(ubd_exch, {'from':accounts[0]})
    exchange_single.setBeneficiary(accounts[1], {'from':accounts[0]})
    
    usdt.approve(exchange_single, PAY_AMOUNT, {'from':accounts[0]})
    logging.info('Calculated UBD amount: {}'.format(
        exchange_single.calcOutUBDForExactInBASE(PAY_AMOUNT))
    )
    logging.info('paymentTokens(usdt): {}, chain.time {}'.format(
        exchange_single.paymentTokens(usdt), chain.time() 
    ))
    
    tx = exchange_single.swapExactInput(
        usdt, 
        PAY_AMOUNT,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    #logging.info('tx: {}'.format(tx.infwo()))
    assert tx.return_value == MINT_UBD_AMOUNT
    assert ubd_exch.balanceOf(accounts[0]) == MINT_UBD_AMOUNT
    
def test_ubd_to_usdt(accounts, ubd_exch, exchange_single, usdt):
    # In this test SANDBOX_1 - just EOA (accounts[9]). Hense we need approve
    usdt.approve(exchange_single, usdt.balanceOf(accounts[9]), {'from':accounts[9]})
    logging.info('Calculated USDT amount: {}'.format(
        exchange_single.calcOutBASEForExactInUBD(MINT_UBD_AMOUNT))
    )
    ubd_balance = ubd_exch.balanceOf(accounts[0])
    logging.info('UBD.balanceOf: {}'.format(
        ubd_balance
    ))

    usdt_balance = usdt.balanceOf(exchange_single)
    logging.info('USDT.balanceOf(exchange_single): {}'.format(
        usdt_balance
    ))

    fee_ubd_calc = exchange_single.getFeeFromInAmount(ubd_exch, MINT_UBD_AMOUNT)
    logging.info(
        '\nCalculated Fee UBD: {}'
        '\nCalculated UBD Balance - Fee: {}'.format(
        fee_ubd_calc,
        ubd_balance - fee_ubd_calc 
    ))

    ubd_exch.approve(exchange_single, MINT_UBD_AMOUNT, {'from':accounts[0]})
    tx = exchange_single.swapExactInput(
        ubd_exch, 
        MINT_UBD_AMOUNT,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    logging.info('tx.return_value: {}'.format(tx.return_value))
    usdt_balance = usdt.balanceOf(accounts[9])
    logging.info('USDT.balanceOf(SANDBOX1): {}'.format(
        usdt_balance
    ))
    



