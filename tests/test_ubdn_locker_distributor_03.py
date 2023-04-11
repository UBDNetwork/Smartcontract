import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1000000


def test_buy(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})
    usdt.approve(lockerdistributor, PAY_AMOUNT-1, {'from':accounts[0]})
    



    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdt, PAY_AMOUNT)
    assert lockerdistributor.getCurrentRound() == 1
    
    with reverts("ERC20: insufficient allowance"):
        tx = lockerdistributor.buyTokensForExactStable(usdt, PAY_AMOUNT, {'from':accounts[0]})

    usdt.approve(lockerdistributor, PAY_AMOUNT, {'from':accounts[1]})
    with reverts("ERC20: transfer amount exceeds balance"):
        tx = lockerdistributor.buyTokensForExactStable(usdt, PAY_AMOUNT, {'from':accounts[1]})

    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, 10*1e6*1e18)   #10*1e6*10**ubdnlocked.decimals()
    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[0]})
    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[0]})
    

    assert lockerdistributor.getCurrentRound() == 11
    assert lockerdistributor.priceInUnitsAndRemainByRound(11)[0] == 12
    assert lockerdistributor.priceInUnitsAndRemainByRound(11)[1] == PAY_AMOUNT*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2 #check price
    #assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == 0 #check rest