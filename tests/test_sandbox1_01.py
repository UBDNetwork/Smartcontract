import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1005e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
def test_usdt_to_ubd(accounts, ubd, sandbox1, usdt):
    sandbox1.setUBDToken(ubd, {'from':accounts[0]})
    sandbox1.setBeneficiary(accounts[1], {'from':accounts[0]})
    
    usdt.approve(sandbox1, PAY_AMOUNT, {'from':accounts[0]})
    logging.info('Calculated UBD amount: {}'.format(
        sandbox1.calcOutUBDForExactInBASE(PAY_AMOUNT))
    )

    chain.sleep(10)
    logging.info('paymentTokens(usdt): {}, chain.time {}'.format(
        sandbox1.paymentTokens(usdt), chain.time() 
    ))
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    #logging.info('tx: {}'.format(tx.infwo()))
    assert tx.return_value == MINT_UBD_AMOUNT
    assert ubd.balanceOf(accounts[0]) == MINT_UBD_AMOUNT
    
def test_ubd_to_usdt(accounts, ubd, sandbox1, usdt):
    # In this test SANDBOX_1 - just EOA (accounts[9]). Hense we need approve
    #usdt.approve(sandbox1, usdt.balanceOf(accounts[9]), {'from':accounts[9]})
    logging.info('Calculated USDT amount: {}'.format(
        sandbox1.calcOutBASEForExactInUBD(MINT_UBD_AMOUNT))
    )
    ubd_balance = ubd.balanceOf(accounts[0])
    logging.info('UBD.balanceOf(acc0): {}'.format(
        ubd_balance
    ))

    usdt_balance = usdt.balanceOf(sandbox1)
    logging.info('USDT.balanceOf(sandbox1): {}'.format(
        usdt_balance
    ))

    fee_ubd_calc = sandbox1.getFeeFromInAmount(ubd, MINT_UBD_AMOUNT)
    logging.info(
        '\nCalculated Fee UBD: {}'
        '\nCalculated UBD Balance(acc0)  - Fee: {}'.format(
        fee_ubd_calc,
        ubd_balance - fee_ubd_calc 
    ))

    ubd.approve(sandbox1, MINT_UBD_AMOUNT, {'from':accounts[0]})
    tx = sandbox1.swapExactInput(
        ubd, 
        MINT_UBD_AMOUNT,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    logging.info('tx.return_value: {}'.format(tx.return_value))
    usdt_balance = usdt.balanceOf(sandbox1)
    logging.info('USDT.balanceOf(SANDBOX1): {}'.format(
        usdt_balance
    ))
    assert ubd.balanceOf(accounts[0]) == 0

def test_usdt_to_ubd_100k(accounts, ubd, sandbox1, usdt):
    usdt.approve(sandbox1, PAY_AMOUNT * 100, {'from':accounts[0]})
    logging.info('Calculated UBD amount: {}'.format(
        sandbox1.calcOutUBDForExactInBASE(PAY_AMOUNT * 100))
    )
    
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT * 100,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    #logging.info('tx: {}'.format(tx.infwo()))
    assert tx.return_value == MINT_UBD_AMOUNT * 100
    assert ubd.balanceOf(accounts[0]) == MINT_UBD_AMOUNT * 100

def test_topup_treasury(accounts, ubd, sandbox1, usdt):
    tx = sandbox1.topupTreasury({'from':accounts[1]})
