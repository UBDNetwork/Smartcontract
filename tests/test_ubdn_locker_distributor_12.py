import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

usdt_amount = 11000211

#check math
#make 10 rounds. Use payment token with decimals=6
def test_odd_number(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})

    chain.sleep(lockerdistributor.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()+1)
    chain.mine()

    for i in range(9):
        in_amount_calc = lockerdistributor.ROUND_VOLUME()*lockerdistributor.priceInUnitsAndRemainByRound(i+1)[0]*10**usdt.decimals()/10**ubdnlocked.decimals()
        usdt.transfer(accounts[1], in_amount_calc, {'from':accounts[0]})
        usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[1]})
        tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[1]})

    assert lockerdistributor.getCurrentRound() == 10
    assert lockerdistributor.priceInUnitsAndRemainByRound(10)[0] == 11 #check price
    out_amount_calc = (usdt_amount-211)*10**ubdnlocked.decimals()/lockerdistributor.priceInUnitsAndRemainByRound(10)[0]+211*10**ubdnlocked.decimals()/lockerdistributor.priceInUnitsAndRemainByRound(11)[0]
    logging.info(out_amount_calc)
    logging.info('current price: {} and {}'.format(lockerdistributor.priceInUnitsAndRemainByRound(10)[0], lockerdistributor.priceInUnitsAndRemainByRound(11)[0]))
    #assert lockerdistributor.calcTokensForExactStable(usdt.address, usdt_amount*10**usdt.decimals()) ==  out_amount_calc
    out_amount_from_contract = lockerdistributor.calcTokensForExactStable(usdt.address, usdt_amount*10**usdt.decimals())
    #assert lockerdistributor.calcStableForExactTokens(usdt.address, out_amount_calc) ==  usdt_amount*10**usdt.decimals()
    in_amount_from_contract = lockerdistributor.calcStableForExactTokens(usdt.address, out_amount_calc)
    logging.info('calcTokensForExactStable returns ubdnlocked tokens for {} usdt: {}'.format(out_amount_from_contract, usdt_amount*10**usdt.decimals() ))
    logging.info('calcStableForExactTokens returns usdt {} for ubdnlocked tokens: {}'.format(in_amount_from_contract, out_amount_from_contract))

    usdt.transfer(accounts[1], usdt_amount*10**usdt.decimals(), {'from':accounts[0]})
    usdt.approve(lockerdistributor, usdt_amount*10**usdt.decimals(), {'from':accounts[1]})
    tx = lockerdistributor.buyTokensForExactStable(usdt, usdt_amount*10**usdt.decimals(), {'from':accounts[1]})
    
    assert lockerdistributor.distributedAmount() == 9*lockerdistributor.ROUND_VOLUME()+out_amount_from_contract
    #assert lockerdistributor.priceInUnitsAndRemainByRound(11)[1] == lockerdistributor.ROUND_VOLUME() - 211*10**ubdnlocked.decimals()/lockerdistributor.priceInUnitsAndRemainByRound(11)[0]
    
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[0] ==  9*lockerdistributor.ROUND_VOLUME()+out_amount_from_contract
    assert lockerdistributor.getUserAvailableAmount(accounts[1])[1] ==  0

    out_amount = 1000000000000000000000000
    in_amount_from_contract = lockerdistributor.calcStableForExactTokens(usdt.address, out_amount)
    logging.info('calcStableForExactTokens returns usdt {} for ubdnlocked tokens: {}'.format(in_amount_from_contract, out_amount))
    out_amount_from_contract =  lockerdistributor.calcTokensForExactStable(usdt.address, in_amount_from_contract)
    logging.info('calcTokensForExactStable returns ubdnlocked tokens for {} usdt: {}'.format(out_amount_from_contract,  in_amount_from_contract))

    part1 = lockerdistributor.ROUND_VOLUME()-lockerdistributor.distributedAmount()%lockerdistributor.ROUND_VOLUME()
    part2 = out_amount - part1

    in_amount_calc11 = part1*lockerdistributor.priceInUnitsAndRemainByRound(11)[0]*10**usdt.decimals()/10**ubdnlocked.decimals()
    in_amount_calc12 = part2*lockerdistributor.priceInUnitsAndRemainByRound(12)[0]*10**usdt.decimals()/10**ubdnlocked.decimals()
    assert round(in_amount_calc11+in_amount_calc12) == in_amount_from_contract

