import pytest
import logging
from brownie import Wei, reverts
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 100_000e6
def test_distrib_simple(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})
    usdt.approve(lockerdistributor, PAY_AMOUNT, {'from':accounts[0]})
    logging.info('Price and rest in round  1:{}'.format(
        lockerdistributor.priceInUnitsAndRemainByRound(1))
    )
    logging.info('Price and rest in round 10:{}'.format(
        lockerdistributor.priceInUnitsAndRemainByRound(10))
    )
    logging.info('Amount of distributed is:{}'.format(
        lockerdistributor.calcTokensForExactStable(usdt, PAY_AMOUNT))
    )
    tx = lockerdistributor.buyTokensForExactStable(usdt, PAY_AMOUNT, {'from':accounts[0]})
    for e in tx.events.keys():
        logging.info('Events:{}:{}'.format(e, tx.events[e]))
    assert ubdnlocked.balanceOf(lockerdistributor.address) ==  PAY_AMOUNT



