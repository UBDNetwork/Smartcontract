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

    usdt.approve(lockerdistributor, PAY_AMOUNT-1, {'from':accounts[0]})


    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, 20*PAY_AMOUNT*10**ubdnlocked.decimals())

    in_amount_calc_manual = 0  
    last_price  = lockerdistributor.START_PRICE() +1
    for i in range(20):
        in_amount_calc_manual= in_amount_calc_manual + PAY_AMOUNT*last_price*10**usdt.decimals()
        last_price = last_price + lockerdistributor.PRICE_INCREASE_STEP()

    assert in_amount_calc == in_amount_calc_manual
    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdt, in_amount_calc)
    assert out_amount_calc == 20*PAY_AMOUNT*10**ubdnlocked.decimals()

    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[0]})
    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[0]})
    assert lockerdistributor.distributedAmount() == 20*PAY_AMOUNT*10**ubdnlocked.decimals()

    assert lockerdistributor.getCurrentRound() == 21
    assert lockerdistributor.priceInUnitsAndRemainByRound(21)[0] == 22
    assert lockerdistributor.priceInUnitsAndRemainByRound(21)[1] == PAY_AMOUNT*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2 #check price
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == 0 #check rest


    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, PAY_AMOUNT*10**ubdnlocked.decimals()/2)
    in_amount_calc_manual= PAY_AMOUNT/2*10**usdt.decimals()*(lockerdistributor.getCurrentRound()*lockerdistributor.PRICE_INCREASE_STEP()+lockerdistributor.START_PRICE())

    assert in_amount_calc == in_amount_calc_manual

    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdt, in_amount_calc)
    assert out_amount_calc == PAY_AMOUNT/2*10**ubdnlocked.decimals()
    
    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[0]})
    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[0]})
    assert lockerdistributor.priceInUnitsAndRemainByRound(21)[1] == PAY_AMOUNT/2*10**ubdnlocked.decimals()


