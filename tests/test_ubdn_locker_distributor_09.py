import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1000000

#buy by accounts[1]
def test_buy(accounts, ubdnlocked, lockerdistributor, usdt, usdc, dai):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setPaymentTokenStatus(usdc, True, {'from':accounts[0]})
    lockerdistributor.setPaymentTokenStatus(dai, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})

    chain.sleep(lockerdistributor.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()+1)
    chain.mine()


    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, (PAY_AMOUNT/2)*10**ubdnlocked.decimals())
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

#buy by accounts[2] and accounts[3]
def test_buy_1(accounts, ubdnlocked, lockerdistributor, usdt, usdc, dai):
    #buy 100 tokens 
    chain.sleep(1000)
    chain.mine()
    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdc.address, 100*10**ubdnlocked.decimals())
    usdc.transfer(accounts[2], in_amount_calc, {'from':accounts[0]})
    usdc.approve(lockerdistributor, in_amount_calc, {'from':accounts[2]})
    before_amount_distr = lockerdistributor.distributedAmount()
    
    tx = lockerdistributor.buyTokensForExactStable(usdc, in_amount_calc, {'from':accounts[2]})

    assert lockerdistributor.distributedAmount() == before_amount_distr + 100*10**ubdnlocked.decimals()
    
    assert lockerdistributor.getUserLocks(accounts[2])[0][0] == 100*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[2])[0][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[2])) == 1
    assert lockerdistributor.getCurrentRound() == 1

    chain.sleep(2000)
    chain.mine()

    #buy again - 200 tokens
    in_amount_calc = lockerdistributor.calcStableForExactTokens(dai.address, 200*10**ubdnlocked.decimals())
    dai.transfer(accounts[3], in_amount_calc, {'from':accounts[0]})
    dai.approve(lockerdistributor, in_amount_calc, {'from':accounts[3]})
    before_amount_distr = lockerdistributor.distributedAmount()
    
    tx = lockerdistributor.buyTokensForExactStable(dai, in_amount_calc, {'from':accounts[3]})

    assert lockerdistributor.distributedAmount() == before_amount_distr + 200*10**ubdnlocked.decimals()
    
    assert lockerdistributor.getUserLocks(accounts[3])[0][0] == 200*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[3])[0][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[3])) == 1
    assert lockerdistributor.getCurrentRound() == 1

    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  (PAY_AMOUNT/2)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0

    assert lockerdistributor.getUserAvailableAmount(accounts[2])[0] ==  100*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[2])[1] ==  0

    assert lockerdistributor.getUserAvailableAmount(accounts[3])[0] ==  200*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[3])[1] ==  0

    chain.sleep(90*24*3600+1)
    chain.mine()

    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  (PAY_AMOUNT/2)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  (PAY_AMOUNT/2)*10**ubdnlocked.decimals()

    assert lockerdistributor.getUserAvailableAmount(accounts[2])[0] ==  100*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[2])[1] ==  100*10**ubdnlocked.decimals()

    assert lockerdistributor.getUserAvailableAmount(accounts[3])[0] ==  200*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[3])[1] ==  200*10**ubdnlocked.decimals()


    before_acc1_ub = ubdnlocked.balanceOf(accounts[1])
    tx = lockerdistributor.claimTokens({"from": accounts[1]})    

    assert lockerdistributor.getUserLocks(accounts[1])[0][0] == 0
    assert ubdnlocked.balanceOf(accounts[1]) == (PAY_AMOUNT/2)*10**ubdnlocked.decimals()
    assert ubdnlocked.balanceOf(lockerdistributor) == 300*10**ubdnlocked.decimals()

    before_acc2_ub = ubdnlocked.balanceOf(accounts[2])
    tx = lockerdistributor.claimTokens({"from": accounts[2]})    

    assert lockerdistributor.getUserLocks(accounts[2])[0][0] == 0
    assert ubdnlocked.balanceOf(accounts[2]) == 100*10**ubdnlocked.decimals()
    assert ubdnlocked.balanceOf(lockerdistributor) == 200*10**ubdnlocked.decimals()


    before_acc3_ub = ubdnlocked.balanceOf(accounts[3])
    tx = lockerdistributor.claimTokens({"from": accounts[3]})    

    assert lockerdistributor.getUserLocks(accounts[3])[0][0] == 0
    assert ubdnlocked.balanceOf(accounts[3]) == 200*10**ubdnlocked.decimals()
    assert ubdnlocked.balanceOf(lockerdistributor) == 0


    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  0
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0

    assert lockerdistributor.getUserAvailableAmount(accounts[2])[0] ==  0
    assert lockerdistributor.getUserAvailableAmount(accounts[2])[1] ==  0

    assert lockerdistributor.getUserAvailableAmount(accounts[3])[0] ==  0
    assert lockerdistributor.getUserAvailableAmount(accounts[3])[1] ==  0

    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == (PAY_AMOUNT/2 - 100 - 200)*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[1] == PAY_AMOUNT*10**ubdnlocked.decimals()