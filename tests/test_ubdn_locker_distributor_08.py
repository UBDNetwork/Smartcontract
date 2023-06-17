import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1000000


def test_buy(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})

    chain.sleep(lockerdistributor.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()+1)
    chain.mine()


    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdc.address, 100*10**ubdnlocked.decimals())

    in_amount_calc_manual = 0  
    last_price  = lockerdistributor.START_PRICE() +1
    in_amount_calc_manual= in_amount_calc_manual + 100*last_price*10**usdc.decimals()
    assert in_amount_calc == in_amount_calc_manual

    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdc, in_amount_calc)
    assert out_amount_calc == 100*10**ubdnlocked.decimals()

    assert in_amount_calc == 100*lockerdistributor.priceInUnitsAndRemainByRound(1)[0]*10**usdc.decimals()
    usdc.transfer(accounts[1], in_amount_calc, {'from':accounts[0]})
    usdc.approve(lockerdistributor, in_amount_calc, {'from':accounts[1]})
    with reverts("This payment token not supported"):
        tx = lockerdistributor.buyTokensForExactStable(usdc, in_amount_calc, {'from':accounts[1]})
    lockerdistributor.setPaymentTokenStatus(usdc, True, {'from':accounts[0]})

    chain.sleep(lockerdistributor.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()+1)
    chain.mine()

    tx = lockerdistributor.buyTokensForExactStable(usdc, in_amount_calc, {'from':accounts[1]})

    assert lockerdistributor.distributedAmount() == 100*10**ubdnlocked.decimals()
    
    assert lockerdistributor.getCurrentRound() == 1
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == (PAY_AMOUNT - 100)*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[1] == PAY_AMOUNT*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2 #check price
    assert lockerdistributor.getUserLocks(accounts[1])[0][0] == 100*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[1])[0][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[1])) == 1

    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  100*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0



#use usdt
def test_buy_1(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    #buy 200 tokens
    chain.sleep(1000)
    chain.mine()
    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, 200*10**ubdnlocked.decimals())

    in_amount_calc_manual = 0  
    last_price  = lockerdistributor.START_PRICE() +1
    in_amount_calc_manual= in_amount_calc_manual + 200*last_price*10**usdt.decimals()
    assert in_amount_calc == in_amount_calc_manual

    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdt, in_amount_calc)
    assert out_amount_calc == 200*10**ubdnlocked.decimals()


    usdt.transfer(accounts[1], in_amount_calc, {'from':accounts[0]})
    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[1]})
    before_amount_distr = lockerdistributor.distributedAmount()
    assert in_amount_calc == 200*lockerdistributor.priceInUnitsAndRemainByRound(1)[0]*10**usdt.decimals() 
    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[1]})

    assert lockerdistributor.distributedAmount() == before_amount_distr + 200*10**ubdnlocked.decimals()
    
    assert lockerdistributor.getUserLocks(accounts[1])[1][0] == 200*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[1])[1][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[1])) == 2
    assert lockerdistributor.getCurrentRound() == 1

    
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == (PAY_AMOUNT - 100 - 200)*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[1] == PAY_AMOUNT*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2 #check price
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[0] == 3 #check price
    
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  (100+200)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0

#use dai
def test_buy_2(accounts, ubdnlocked, lockerdistributor, usdt, usdc, dai):
    #buy 300 tokens
    lockerdistributor.setPaymentTokenStatus(dai.address, True, {'from':accounts[0]})

    chain.sleep(lockerdistributor.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()+1)
    chain.mine()

    chain.sleep(1000)
    chain.mine()
    in_amount_calc = lockerdistributor.calcStableForExactTokens(dai.address, 300*10**ubdnlocked.decimals())


    in_amount_calc_manual = 0  
    last_price  = lockerdistributor.START_PRICE() +1
    in_amount_calc_manual= in_amount_calc_manual + 300*last_price*10**dai.decimals()
    assert in_amount_calc == in_amount_calc_manual

    out_amount_calc = lockerdistributor.calcTokensForExactStable(dai, in_amount_calc)
    assert out_amount_calc == 300*10**ubdnlocked.decimals()


    dai.transfer(accounts[1], in_amount_calc, {'from':accounts[0]})
    dai.approve(lockerdistributor, in_amount_calc, {'from':accounts[1]})
    before_amount_distr = lockerdistributor.distributedAmount()
    assert in_amount_calc == 300*lockerdistributor.priceInUnitsAndRemainByRound(1)[0]*10**dai.decimals() 
    tx = lockerdistributor.buyTokensForExactStable(dai, in_amount_calc, {'from':accounts[1]})

    assert lockerdistributor.distributedAmount() == before_amount_distr + 300*10**ubdnlocked.decimals()
    
    assert lockerdistributor.getUserLocks(accounts[1])[2][0] == 300*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[1])[2][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[1])) == 3
    assert lockerdistributor.getCurrentRound() == 1

    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == (PAY_AMOUNT - 100 - 200 - 300)*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[1] == PAY_AMOUNT*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2 #check price
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[0] == 3 #check price
    
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  (100+200+300)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0

   