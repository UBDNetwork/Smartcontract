import pytest
import logging
from brownie import Wei, reverts
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 100_000e6
def test_distrib_simple(accounts, ubdn, distributor, usdt, usdc):
    distributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    distributor.setDistributionToken(ubdn, {'from':accounts[0]})
    usdt.approve(distributor, PAY_AMOUNT, {'from':accounts[0]})
    logging.info('Price and rest in round  1:{}'.format(distributor.priceInUnitsAndRemainByRound(1)))
    logging.info('Price and rest in round 10:{}'.format(
        distributor.priceInUnitsAndRemainByRound(10))
    )
    logging.info('Amount of distributed is:{} for stable amount {}'.format(
        distributor.calcTokensForExactStable(usdt, PAY_AMOUNT), PAY_AMOUNT)
    )
    tx = distributor.buyTokensForExactStable(usdt, PAY_AMOUNT, {'from':accounts[0]})
    for e in tx.events.keys():
        logging.info('Events:{}:{}'.format(e, tx.events[e]))
    assert ubdn.balanceOf(accounts[0]) == PAY_AMOUNT



