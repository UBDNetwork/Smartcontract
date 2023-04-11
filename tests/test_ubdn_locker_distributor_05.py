import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1000000


def test_buy(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})
    usdt.approve(lockerdistributor, PAY_AMOUNT-1, {'from':accounts[0]})


    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, (PAY_AMOUNT+1)*10**ubdnlocked.decimals())
    assert in_amount_calc == (PAY_AMOUNT*lockerdistributor.priceInUnitsAndRemainByRound(1)[0] + 1*lockerdistributor.priceInUnitsAndRemainByRound(2)[0])*10**usdt.decimals()
    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[0]})
    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[0]})
    assert lockerdistributor.distributedAmount() == (PAY_AMOUNT+1)*10**ubdnlocked.decimals()
    assert ubdnlocked.balanceOf(lockerdistributor.address) == lockerdistributor.distributedAmount()

    assert lockerdistributor.getCurrentRound() == 2
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[0] == 3
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[1] == (PAY_AMOUNT-1)*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2 #check price

    assert lockerdistributor.getUserLocks(accounts[0])[0][0] == (PAY_AMOUNT+1)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[0])[0][1] >= chain.time() + 7776000-1
    assert len(lockerdistributor.getUserLocks(accounts[0])) == 1


    #try to claim - lock has not finished yet
    lockerdistributor.claimTokens({"from": accounts[1]})
    tx = lockerdistributor.claimTokens({"from": accounts[0]})
    logging.info(tx.events['Transfer'])


    