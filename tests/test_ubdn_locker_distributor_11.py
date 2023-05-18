import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

usdt_amount = 23

#check math
#make 10 rounds
def test_odd_number(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})
    for i in range(9):
        in_amount_calc = lockerdistributor.ROUND_VOLUME()*lockerdistributor.priceInUnitsAndRemainByRound(i+1)[0]*10**usdt.decimals()/10**ubdnlocked.decimals()
        usdt.transfer(accounts[1], in_amount_calc, {'from':accounts[0]})
        usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[1]})
        tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[1]})

    assert lockerdistributor.getCurrentRound() == 10
    assert lockerdistributor.priceInUnitsAndRemainByRound(10)[0] == 11 #check price
    out_amount_calc = usdt_amount*10**ubdnlocked.decimals()/lockerdistributor.priceInUnitsAndRemainByRound(10)[0]
    logging.info(out_amount_calc)
    logging.info('current price: {}'.format(lockerdistributor.priceInUnitsAndRemainByRound(10)[0]))
    #assert lockerdistributor.calcTokensForExactStable(usdt.address, usdt_amount*10**usdt.decimals()) ==  out_amount_calc
    out_amount_from_contract = lockerdistributor.calcTokensForExactStable(usdt.address, usdt_amount*10**usdt.decimals())
    #assert lockerdistributor.calcStableForExactTokens(usdt.address, out_amount_calc) ==  usdt_amount*10**usdt.decimals()
    in_amount_from_contract = lockerdistributor.calcStableForExactTokens(usdt.address, out_amount_calc)
    logging.info('calcTokensForExactStable returns ubdnlocked tokens for 23 usdt: {}'.format(out_amount_from_contract ))
    logging.info('calcStableForExactTokens returns ubdnlocked tokens for {} usdt: {}'.format(out_amount_from_contract,  in_amount_from_contract))

    usdt.transfer(accounts[1], usdt_amount*10**usdt.decimals(), {'from':accounts[0]})
    usdt.approve(lockerdistributor, usdt_amount*10**usdt.decimals(), {'from':accounts[1]})
    tx = lockerdistributor.buyTokensForExactStable(usdt, usdt_amount*10**usdt.decimals(), {'from':accounts[1]})
    
    assert lockerdistributor.distributedAmount() == 9*lockerdistributor.ROUND_VOLUME()+out_amount_from_contract
    assert lockerdistributor.priceInUnitsAndRemainByRound(10)[1] == lockerdistributor.ROUND_VOLUME() - out_amount_from_contract
    
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  9*lockerdistributor.ROUND_VOLUME()+out_amount_from_contract
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0

    out_amount = 1313131313131313131313
    in_amount_from_contract = lockerdistributor.calcStableForExactTokens(usdt.address, out_amount)
    logging.info('calcStableForExactTokens returns ubdnlocked tokens for {} usdt: {}'.format(out_amount,  in_amount_from_contract))

    in_amount_calc = out_amount*lockerdistributor.priceInUnitsAndRemainByRound(10)[0]*10**usdt.decimals()/10**ubdnlocked.decimals()
    assert round(in_amount_calc) == in_amount_from_contract


