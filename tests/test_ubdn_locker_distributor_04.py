import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1000000


def test_buy(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})
    usdt.approve(lockerdistributor, PAY_AMOUNT-1, {'from':accounts[0]})


    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, 20*PAY_AMOUNT*10**ubdnlocked.decimals())
    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[0]})
    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[0]})
    assert lockerdistributor.distributedAmount() == 20*PAY_AMOUNT*10**ubdnlocked.decimals()

    assert lockerdistributor.getCurrentRound() == 21
    assert lockerdistributor.priceInUnitsAndRemainByRound(21)[0] == 22
    assert lockerdistributor.priceInUnitsAndRemainByRound(21)[1] == PAY_AMOUNT*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2 #check price
    #assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == 0 #check rest


    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, PAY_AMOUNT*10**ubdnlocked.decimals()/2)
    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[0]})
    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[0]})
    assert lockerdistributor.priceInUnitsAndRemainByRound(21)[1] == PAY_AMOUNT/2*10**ubdnlocked.decimals()

