import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1000e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def test_usdt_to_ubd(accounts, ubd_exch, exchange_single, usdt, dai):
    #prepare data
    fee_percent = exchange_single.paymentTokens(usdt.address)[1]/exchange_single.PERCENT_DENOMINATOR()

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
    assert tx.return_value == round(PAY_AMOUNT*100/(100+fee_percent))*10**ubd_exch.decimals()/10**usdt.decimals()
    assert ubd_exch.balanceOf(accounts[2]) == round(PAY_AMOUNT*100/(100+fee_percent))*10**ubd_exch.decimals()/10**usdt.decimals()
    assert exchange_single.getFeeFromInAmount(usdt, PAY_AMOUNT) == PAY_AMOUNT*fee_percent/(100+fee_percent)

    assert usdt.balanceOf(exchange_single.SANDBOX_1())== round(PAY_AMOUNT*100/(100+fee_percent))
    assert usdt.balanceOf(accounts[1])== PAY_AMOUNT*fee_percent/(100+fee_percent)
    assert ubd_exch.totalSupply() == round(PAY_AMOUNT*100/(100+fee_percent))*10**ubd_exch.decimals()/10**usdt.decimals()

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

def test_ubd_to_usdt(accounts, ubd_exch, exchange_single, usdt):
    #prepare data
    fee_percent = exchange_single.paymentTokens(ubd_exch.address)[1]/exchange_single.PERCENT_DENOMINATOR()
    PAY_AMOUNT = ubd_exch.balanceOf(accounts[2])
    usdt_out_amount = round(PAY_AMOUNT*100/(100+fee_percent))*10**usdt.decimals()/10**ubd_exch.decimals()

    ubd_exch.approve(exchange_single, PAY_AMOUNT, {'from':accounts[2]})
    usdt.approve(exchange_single, PAY_AMOUNT, {'from':accounts[9]})
    before_usdt_sandbox = usdt.balanceOf(exchange_single.SANDBOX_1())
    before_total_supply = ubd_exch.totalSupply()
    
    #receiver<>msg.sender
    tx = exchange_single.swapExactInput(
        ubd_exch, 
        PAY_AMOUNT,
        0,
        0,
        accounts[2], 
        {'from':accounts[0]}
    )

    #logging.info('tx: {}'.format(tx.infwo()))
    assert tx.return_value == usdt_out_amount
    assert usdt.balanceOf(accounts[2]) == usdt_out_amount
    assert exchange_single.getFeeFromInAmount(ubd_exch, PAY_AMOUNT) - PAY_AMOUNT*fee_percent/(100+fee_percent) < 1000

    assert before_usdt_sandbox - usdt.balanceOf(exchange_single.SANDBOX_1()) == round(PAY_AMOUNT*100/(100+fee_percent))*10**usdt.decimals()/10**ubd_exch.decimals()
    assert ubd_exch.balanceOf(accounts[1]) - PAY_AMOUNT*fee_percent/(100+fee_percent) < 1000
    assert ubd_exch.balanceOf(accounts[2]) == 0
    #check burning
    assert ubd_exch.totalSupply() == ubd_exch.balanceOf(accounts[1])

    