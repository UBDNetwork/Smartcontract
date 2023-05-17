import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

usdt_amount = 23

#check math
def test_first_round(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})
    
    out_amount_calc = usdt_amount*10**ubdnlocked.decimals()/lockerdistributor.priceInUnitsAndRemainByRound(1)[0]
    logging.info(out_amount_calc)
    usdt.transfer(accounts[1], usdt_amount*10**usdt.decimals(), {'from':accounts[0]})
    usdt.approve(lockerdistributor, usdt_amount*10**usdt.decimals(), {'from':accounts[1]})
    assert lockerdistributor.calcTokensForExactStable(usdt.address, usdt_amount*10**usdt.decimals()) ==  out_amount_calc
    out_amount_from_contract = lockerdistributor.calcTokensForExactStable(usdt.address, usdt_amount*10**usdt.decimals())
    assert lockerdistributor.calcStableForExactTokens(usdt.address, out_amount_calc) ==  usdt_amount*10**usdt.decimals()
    in_amount_from_contract = lockerdistributor.calcStableForExactTokens(usdt.address, out_amount_calc)
    logging.info('calcTokensForExactStable returns ubdnlocked tokens for 23 usdt: {}'.format(out_amount_from_contract ))
    logging.info('calcStableForExactTokens returns ubdnlocked tokens for {} usdt: {}'.format(out_amount_from_contract,  in_amount_from_contract))


    tx = lockerdistributor.buyTokensForExactStable(usdt, usdt_amount*10**usdt.decimals(), {'from':accounts[1]})
    assert lockerdistributor.distributedAmount() == out_amount_calc
    
    assert lockerdistributor.getCurrentRound() == 1
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == lockerdistributor.ROUND_VOLUME() - out_amount_calc
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2 #check price
    assert lockerdistributor.getUserLocks(accounts[1])[0][0] == out_amount_calc
    assert lockerdistributor.getUserLocks(accounts[1])[0][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[1])) == 1

    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  out_amount_calc
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0

#part of tokens from round 1 and part of tokens from round 2
'''def test_buy_1(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    #buy 300 tokens
    chain.sleep(1000)
    chain.mine()
    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, 300*10**ubdnlocked.decimals())

    in_amount_calc_manual = 0  
    last_price  = lockerdistributor.START_PRICE() +1
    in_amount_calc_manual= in_amount_calc_manual + 100*last_price*10**usdt.decimals()
    last_price = last_price + lockerdistributor.PRICE_INCREASE_STEP()
    in_amount_calc_manual= in_amount_calc_manual + 200*last_price*10**usdt.decimals()

    assert in_amount_calc == in_amount_calc_manual

    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdt, in_amount_calc)
    assert out_amount_calc == 300*10**ubdnlocked.decimals()

    usdt.transfer(accounts[1], in_amount_calc, {'from':accounts[0]})
    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[1]})
    before_amount_distr = lockerdistributor.distributedAmount()
    
    assert in_amount_calc == 100*lockerdistributor.priceInUnitsAndRemainByRound(1)[0]*10**usdt.decimals() + 200*lockerdistributor.priceInUnitsAndRemainByRound(2)[0]*10**usdt.decimals() 
    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[1]})
    assert lockerdistributor.distributedAmount() == before_amount_distr + 300*10**ubdnlocked.decimals()
    
    assert lockerdistributor.getUserLocks(accounts[1])[1][0] == 300*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[1])[1][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[1])) == 2
    assert lockerdistributor.getCurrentRound() == 2

    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[1] == 0
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[1] == (PAY_AMOUNT-200)*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(3)[1] == PAY_AMOUNT*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2 #check price
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[0] == 3 #check price
    assert lockerdistributor.priceInUnitsAndRemainByRound(3)[0] == 4 #check price

    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  (PAY_AMOUNT+200)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0'''







