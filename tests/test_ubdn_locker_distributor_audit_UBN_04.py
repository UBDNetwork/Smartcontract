import pytest
import logging
from brownie import Wei, reverts, chain
import math
LOGGER = logging.getLogger(__name__)


inAmount = 100e18

def test_audit(accounts, ubdnlocked, lockerdistributor, dai):
    lockerdistributor.setPaymentTokenStatus(dai, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})

    #prepare data
    dai.transfer(accounts[1], inAmount, {"from": accounts[0]})
    dai.approve(lockerdistributor, inAmount, {'from':accounts[1]})

    chain.sleep(lockerdistributor.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()+1)
    chain.mine()

    with reverts("Slippage occur"):
        tx = lockerdistributor.buyTokensForExactStableWithSlippage(dai, inAmount, 51e18, {'from':accounts[1]})

    before_acc = ubdnlocked.balanceOf(accounts[1])
    tx = lockerdistributor.buyTokensForExactStable(dai, inAmount, {'from':accounts[1]})


    assert lockerdistributor.getUserLocks(accounts[1])[0][0] == 50e18 

    