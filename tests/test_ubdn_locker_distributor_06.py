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


    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, (PAY_AMOUNT/2)*10**ubdnlocked.decimals())
    in_amount_calc_manual = 0  
    last_price  = lockerdistributor.START_PRICE() +1
    in_amount_calc_manual= in_amount_calc_manual + PAY_AMOUNT/2*last_price*10**usdt.decimals()
    assert in_amount_calc == in_amount_calc_manual

    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdt, in_amount_calc)
    assert out_amount_calc == PAY_AMOUNT/2*10**ubdnlocked.decimals()


    assert in_amount_calc == (PAY_AMOUNT/2*lockerdistributor.priceInUnitsAndRemainByRound(1)[0])*10**usdt.decimals()
    usdt.transfer(accounts[1], in_amount_calc, {'from':accounts[0]})
    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[1]})
    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[1]})
    assert lockerdistributor.distributedAmount() == (PAY_AMOUNT/2)*10**ubdnlocked.decimals()
    
    assert lockerdistributor.getCurrentRound() == 1
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == (PAY_AMOUNT/2)*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2 #check price
    assert lockerdistributor.getUserLocks(accounts[1])[0][0] == (PAY_AMOUNT/2)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[1])[0][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[1])) == 1

    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == PAY_AMOUNT/2*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  PAY_AMOUNT/2*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0


def test_buy_1(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    #buy 100 tokens
    chain.sleep(1000)
    chain.mine()
    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, 100*10**ubdnlocked.decimals())

    in_amount_calc_manual = 0  
    last_price  = lockerdistributor.START_PRICE() +1
    in_amount_calc_manual= in_amount_calc_manual + 100*last_price*10**usdt.decimals()
    assert in_amount_calc == in_amount_calc_manual

    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdt, in_amount_calc)
    assert out_amount_calc == 100*10**ubdnlocked.decimals()

    usdt.transfer(accounts[1], in_amount_calc, {'from':accounts[0]})
    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[1]})
    before_amount_distr = lockerdistributor.distributedAmount()
    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[1]})

    assert lockerdistributor.distributedAmount() == before_amount_distr + 100*10**ubdnlocked.decimals()
    
    assert lockerdistributor.getUserLocks(accounts[1])[1][0] == 100*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[1])[1][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[1])) == 2
    assert lockerdistributor.getCurrentRound() == 1

    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == (PAY_AMOUNT/2-100)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  (PAY_AMOUNT/2+100)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0

    chain.sleep(2000)
    chain.mine()

    #buy again - 200 tokens
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
    
    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[1]})

    assert lockerdistributor.distributedAmount() == before_amount_distr + 200*10**ubdnlocked.decimals()
    
    assert lockerdistributor.getUserLocks(accounts[1])[2][0] == 200*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[1])[2][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[1])) == 3
    assert lockerdistributor.getCurrentRound() == 1

    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == (PAY_AMOUNT/2-100-200)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  (PAY_AMOUNT/2+100+200)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0

    chain.sleep(90*24*3600+1)
    chain.mine()

    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  (PAY_AMOUNT/2+100+200)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  (PAY_AMOUNT/2+100+200)*10**ubdnlocked.decimals()

    before_acc1_ub = ubdnlocked.balanceOf(accounts[1])
    tx = lockerdistributor.claimTokens({"from": accounts[1]})    

    assert lockerdistributor.getUserLocks(accounts[1])[0][0] == 0
    assert lockerdistributor.getUserLocks(accounts[1])[1][0] == 0
    assert lockerdistributor.getUserLocks(accounts[1])[2][0] == 0
    assert ubdnlocked.balanceOf(accounts[1]) == (PAY_AMOUNT/2+100+200)*10**ubdnlocked.decimals()
    assert ubdnlocked.balanceOf(lockerdistributor) == 0

    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  0
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0




