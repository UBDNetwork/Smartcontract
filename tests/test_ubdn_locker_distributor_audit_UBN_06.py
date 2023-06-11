import pytest
import logging
from brownie import Wei, reverts, chain
import math
LOGGER = logging.getLogger(__name__)


inAmount = 334e18

#check math
#make 10 rounds. Use payment token with decimals=6
def test_audit(accounts, ubdnlocked, lockerdistributor, dai):
    lockerdistributor.setPaymentTokenStatus(dai, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})

    #prepare data
    dai.approve(lockerdistributor, 2000000*10**dai.decimals(), {'from':accounts[0]})
    tx = lockerdistributor.buyTokensForExactStable(dai, 2000000*10**dai.decimals(), {'from':accounts[0]})

    dai.approve(lockerdistributor, 3000000*10**dai.decimals(), {'from':accounts[0]})
    tx = lockerdistributor.buyTokensForExactStable(dai, 3000000*10**dai.decimals(), {'from':accounts[0]})

    dai.approve(lockerdistributor, 4000000*10**dai.decimals(), {'from':accounts[0]})
    tx = lockerdistributor.buyTokensForExactStable(dai, 4000000*10**dai.decimals(), {'from':accounts[0]})

    dai.approve(lockerdistributor, 604557350015191483654609*lockerdistributor.priceInUnitsAndRemainByRound(4)[0], {'from':accounts[0]})
    tx = lockerdistributor.buyTokensForExactStable(dai, 604557350015191483654609*lockerdistributor.priceInUnitsAndRemainByRound(4)[0], {'from':accounts[0]})

    logging.info("distributedAmount: {}".format(lockerdistributor.distributedAmount()))
    logging.info("curRound: {}".format(math.floor(lockerdistributor.distributedAmount() / lockerdistributor.ROUND_VOLUME()) + 1))
    logging.info("curPrice:  {}".format(lockerdistributor.priceInUnitsAndRemainByRound(4)[0]))
    

    assert lockerdistributor.getCurrentRound() == 4
    assert lockerdistributor.priceInUnitsAndRemainByRound(4)[0] == 5 #check price

    #test
    logging.info('inAmount: {}'.format(inAmount))
    out_amount_manual_calc = inAmount*10**ubdnlocked.decimals()/(lockerdistributor.priceInUnitsAndRemainByRound(4)[0]*10**dai.decimals())
    logging.info('out_amount_manual_calc: {}'.format(out_amount_manual_calc))

    out_amount_contract_calc = lockerdistributor.calcTokensForExactStable(dai.address, inAmount)
    inAmount_contract_calc = lockerdistributor.calcStableForExactTokens(dai.address, out_amount_contract_calc)
    logging.info('out_amount_contract_calc: {}'.format(out_amount_contract_calc))

    logging.info('inAmount_contract_calc: {}'.format(inAmount_contract_calc))

    diff_ = inAmount - inAmount_contract_calc

    logging.info('diff: {}'.format(diff_))
    
    