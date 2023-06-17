import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 100_000e6
def test_distrib_simple(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})

    chain.sleep(lockerdistributor.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()+1)
    chain.mine()

    usdt.approve(lockerdistributor, PAY_AMOUNT, {'from':accounts[0]})
    logging.info('Price and rest in round  1:{}'.format(lockerdistributor.priceInUnitsAndRemainByRound(1)))
    logging.info('Price and rest in round 10:{}'.format(
        lockerdistributor.priceInUnitsAndRemainByRound(10))
    )

    ubdn_calc = lockerdistributor.calcTokensForExactStable(usdt, PAY_AMOUNT) 
    logging.info('Amount of distributed is:{} for stable amount {}'.format(
        ubdn_calc , PAY_AMOUNT)
    )
    tx = lockerdistributor.buyTokensForExactStable(usdt, PAY_AMOUNT, {'from':accounts[0]})
    for e in tx.events.keys():
        logging.info('Events:{}:{}'.format(e, tx.events[e]))
    #assert ubdnlocked.balanceOf(accounts[0]) == ubdn_calc
    ubdn_calc = lockerdistributor.calcTokensForExactStable(usdt, 5e5) 
    logging.info('Amount of distributed is:{} for stable amount {}'.format(
        Wei(ubdn_calc).to('ether') , 5e5)
    )

    ubdn_calc = lockerdistributor.calcTokensForExactStable(usdt, 5e6 ) 
    logging.info('Amount of distributed is:{} for stable amount {}'.format(
        Wei(ubdn_calc).to('ether') , 5e6)
    )

    stable_calc = lockerdistributor.calcStableForExactTokens(ubdnlocked, 1e18 ) 
    logging.info('Amount of stable is:{} for distr amount {}'.format(
        stable_calc , 1e18)
    )


