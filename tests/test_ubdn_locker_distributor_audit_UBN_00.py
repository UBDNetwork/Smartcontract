import pytest
import logging
from brownie import Wei, reverts, chain
import math
LOGGER = logging.getLogger(__name__)


inAmount = 100e18

def test_audit(accounts, ubdnlocked, lockerdistributor, dai, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(dai, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})

    assert lockerdistributor.paymentTokens(dai) > 0

    with reverts("Ownable: caller is not the owner"):
        lockerdistributor.setGuardianStatus(accounts[1], True, {"from": accounts[1]})

    chain.sleep(lockerdistributor.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()+1)
    chain.mine()

    #add gardian
    lockerdistributor.setGuardianStatus(accounts[1], True, {"from": accounts[0]})

    with reverts("Only for approved guardians"):
        lockerdistributor.emergencyPause(dai, {"from": accounts[2]})

    #set pause
    tx = lockerdistributor.emergencyPause(dai, {"from": accounts[1]})
    assert tx.events['PaymentTokenPaused']['Token'] == dai.address
    assert tx.events['PaymentTokenPaused']['Until'] == lockerdistributor.paymentTokens(dai)

    #prepare data
    dai.transfer(accounts[1], inAmount, {"from": accounts[0]})
    dai.approve(lockerdistributor, inAmount, {'from':accounts[1]})


    before_acc = ubdnlocked.balanceOf(accounts[1])
    with reverts("Token paused or timelocked"):
        tx = lockerdistributor.buyTokensForExactStable(dai, inAmount, {'from':accounts[1]})

    chain.sleep(lockerdistributor.EMERGENCY_PAYMENT_PAUSE()+1)
    chain.mine()

    tx = lockerdistributor.buyTokensForExactStable(dai, inAmount, {'from':accounts[1]})


    assert lockerdistributor.getUserLocks(accounts[1])[0][0] == 50e18 

    #set pause for not payment token
    tx = lockerdistributor.emergencyPause(usdt.address, {"from": accounts[1]})
    assert lockerdistributor.paymentTokens(usdt.address) == 0

    t = chain.time()
    logging.info(t)
    lockerdistributor.setPaymentTokenStatus(usdc, True, {'from':accounts[0]})
    tx = lockerdistributor.emergencyPause(usdc, {"from": accounts[1]})
    assert lockerdistributor.paymentTokens(usdc.address) > t + lockerdistributor.EMERGENCY_PAYMENT_PAUSE() + 2
    assert lockerdistributor.paymentTokens(usdc.address) < t + lockerdistributor.ADD_NEW_PAYMENT_TOKEN_TIMELOCK() + 2




    