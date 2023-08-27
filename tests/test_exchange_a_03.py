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
        exchange_single.setPaymentTokenStatus(usdt.address, False, 0, {"from": accounts[1]})
    exchange_single.setPaymentTokenStatus(usdt.address, False, 0, {"from": accounts[0]})
    assert exchange_single.paymentTokens(usdt.address)[0] == 0
    assert exchange_single.paymentTokens(usdt.address)[1] == 0

    usdt.transfer(accounts[2], PAY_AMOUNT, {'from':accounts[0]})
    usdt.approve(exchange_single.address, PAY_AMOUNT, {'from':accounts[2]})
    
    #switch of usdt
    with reverts("Token not enabled"):
        tx = exchange_single.swapExactInput(
                usdt, 
                PAY_AMOUNT,
                0,
                PAY_AMOUNT*10**ubd_exch.decimals()/10**usdt.decimals(),
                accounts[2], 
                {'from':accounts[0]}
            )

    #try to switch ubd token
    with reverts("Cant disable UBD"):
        exchange_single.setPaymentTokenStatus(ubd_exch.address, False, 0, {"from": accounts[0]})

    #change fee for ubd
    exchange_single.setPaymentTokenStatus(ubd_exch.address, True, exchange_single.FEE_EXCHANGE_DEFAULT()-1000, {"from": accounts[0]})
    assert exchange_single.paymentTokens(ubd_exch)[1] == exchange_single.FEE_EXCHANGE_DEFAULT()-1000
    assert exchange_single.paymentTokens(ubd_exch)[0] <= chain.time()
    assert exchange_single.paymentTokens(ubd_exch)[0] > chain.time() - 10

    #swith usdt again
    exchange_single.setPaymentTokenStatus(usdt.address, True, exchange_single.FEE_EXCHANGE_DEFAULT()+4000, {"from": accounts[0]})
    chain.sleep(10)
    chain.mine()

    #check swap with new fee
    fee_percent = exchange_single.paymentTokens(usdt.address)[1]/exchange_single.PERCENT_DENOMINATOR()

    tx = exchange_single.swapExactInput(
                usdt, 
                PAY_AMOUNT,
                0,
                0,
                accounts[2], 
                {'from':accounts[0]}
            )

    assert tx.return_value == round(PAY_AMOUNT*100/(100+fee_percent))*10**ubd_exch.decimals()/10**usdt.decimals()

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

    assert tx.return_value == usdt_out_amount
    assert usdt.balanceOf(accounts[2]) == usdt_out_amount
    assert exchange_single.getFeeFromInAmount(ubd_exch, PAY_AMOUNT) - PAY_AMOUNT*fee_percent/(100+fee_percent) < 1000

    assert before_usdt_sandbox - usdt.balanceOf(exchange_single.SANDBOX_1()) == round(PAY_AMOUNT*100/(100+fee_percent))*10**usdt.decimals()/10**ubd_exch.decimals()
    assert ubd_exch.balanceOf(accounts[1]) - PAY_AMOUNT*fee_percent/(100+fee_percent) < 1000
    assert ubd_exch.balanceOf(accounts[2]) == 0
    #check burning
    assert ubd_exch.totalSupply() == ubd_exch.balanceOf(accounts[1])

    with reverts("Fee is too much"):
        exchange_single.setPaymentTokenStatus(ubd_exch.address, True, exchange_single.FEE_EXCHANGE_DEFAULT()*4, {"from": accounts[0]})

    #add new paymentToken and check pause - change BASE_EXCHANGE_TOKEN
    exchange_single.setPaymentTokenStatus(dai.address, True, exchange_single.FEE_EXCHANGE_DEFAULT()+4000, {"from": accounts[0]})

    assert exchange_single.paymentTokens(dai)[1] == exchange_single.FEE_EXCHANGE_DEFAULT()+4000
    assert exchange_single.paymentTokens(dai)[0] <= chain.time() + exchange_single.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()
    assert exchange_single.paymentTokens(dai)[0] > chain.time() + exchange_single.ADD_NEW_PAYMENT_TOKEN_TIMELOCK() - 10
    assert exchange_single.EXCHANGE_BASE_ASSET() == dai.address


    dai.approve(exchange_single, PAY_AMOUNT, {'from':accounts[0]})

    with reverts("Token paused or timelocked"):
        tx = exchange_single.swapExactInput(
            dai, 
            PAY_AMOUNT,
            0,
            0,
            ZERO_ADDRESS, 
            {'from':accounts[0]}
        )

    usdt.approve(exchange_single, PAY_AMOUNT, {'from':accounts[0]})
    
    with reverts(""):
        tx = exchange_single.swapExactInput(
                usdt, 
                PAY_AMOUNT,
                0,
                0,
                ZERO_ADDRESS, 
                {'from':accounts[0]}
            )

    chain.sleep(exchange_single.ADD_NEW_PAYMENT_TOKEN_TIMELOCK() + 1)
    chain.mine()

    tx = exchange_single.swapExactInput(
            dai, 
            PAY_AMOUNT,
            0,
            0,
            ZERO_ADDRESS, 
            {'from':accounts[0]}
        )


