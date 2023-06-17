import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

usdt_amount = 23

#check math
def test_first_round(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})

    chain.sleep(lockerdistributor.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()+1)
    chain.mine()
    
    out_amount_calc = usdt_amount*10**ubdnlocked.decimals()/lockerdistributor.priceInUnitsAndRemainByRound(1)[0]
    #logging.info(out_amount_calc)
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

