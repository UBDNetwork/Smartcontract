import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1_000_000e6
def pretty_print_locks(locks):
    for l in locks:
        logging.info('\nLocked:{:24n} tokens untill {}'.format(
            Wei(l[0]).to('ether'), 
            l[1]
        ));

def test_simple_buy(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})
    usdt.approve(lockerdistributor, PAY_AMOUNT, {'from':accounts[0]})
    logging.info('Price and rest in round  1:{}'.format(
        lockerdistributor.priceInUnitsAndRemainByRound(1))
    )
    logging.info('Price and rest in round 10:{}'.format(
        lockerdistributor.priceInUnitsAndRemainByRound(10))
    )
    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdt, PAY_AMOUNT)
    logging.info('Amount of distributed is:{:n}'.format(
        Wei(out_amount_calc).to('ether')
    ))
    assert lockerdistributor.getCurrentRound() == 1
    tx = lockerdistributor.buyTokensForExactStable(usdt, PAY_AMOUNT, {'from':accounts[0]})
    distributed = lockerdistributor.distributedAmount()
    logging.info('Total distributed:{:n}'.format(
        Wei(distributed).to('ether')
    ))
    assert lockerdistributor.getCurrentRound() == 1
    for e in tx.events.keys():
        logging.info('Events:{}:{}'.format(e, tx.events[e]))
    assert ubdnlocked.balanceOf(lockerdistributor.address) ==  out_amount_calc
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[0] == 3
    assert lockerdistributor.priceInUnitsAndRemainByRound(5)[0] == 6

def test_locks(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    chain.sleep(3600)
    chain.mine()
    usdt.approve(lockerdistributor, PAY_AMOUNT, {'from':accounts[0]})
    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdt, PAY_AMOUNT)
    lockerdistributor.buyTokensForExactStable(usdt, PAY_AMOUNT, {'from':accounts[0]})
    locks = lockerdistributor.getUserLocks(accounts[0])
    pretty_print_locks(locks);
    assert len(locks) == 2
    assert lockerdistributor.getUserAvailableAmount(accounts[0])[0] == ubdnlocked.balanceOf(lockerdistributor.address)
    assert lockerdistributor.getUserAvailableAmount(accounts[0])[1] == 0

def test_claim(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    chain.sleep(lockerdistributor.LOCK_PERIOD() - 3600)
    chain.mine()
    locks = lockerdistributor.getUserLocks(accounts[0])
    assert lockerdistributor.getUserAvailableAmount(accounts[0])[1] == locks[0][0]
    bbefore = ubdnlocked.balanceOf(accounts[0])
    tx = lockerdistributor.claimTokens({'from':accounts[0]})
    for e in tx.events.keys():
        logging.info('Events:{}:{}'.format(e, tx.events[e]))
    assert ubdnlocked.balanceOf(accounts[0]) - bbefore == tx.events['Claimed']['Amount']
    assert lockerdistributor.getUserAvailableAmount(accounts[0])[1] == 0
    assert lockerdistributor.getUserAvailableAmount(accounts[0])[0] == locks[1][0]
    assert tx.events['Claimed']['Amount'] == tx.events['Transfer']['value']
    locks = lockerdistributor.getUserLocks(accounts[0])
    pretty_print_locks(locks);

def test_second_claim(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    with reverts('Nothing to claim'):
        tx = lockerdistributor.claimTokens({'from':accounts[0]})
    chain.sleep(3600)
    chain.mine()
    locks = lockerdistributor.getUserLocks(accounts[0])
    assert lockerdistributor.getUserAvailableAmount(accounts[0])[1] == locks[1][0]
    bbefore = ubdnlocked.balanceOf(accounts[0])
    tx = lockerdistributor.claimTokens({'from':accounts[0]})
    for e in tx.events.keys():
        logging.info('Events:{}:{}'.format(e, tx.events[e]))
    assert ubdnlocked.balanceOf(accounts[0]) - bbefore == tx.events['Claimed']['Amount']
    assert lockerdistributor.getUserAvailableAmount(accounts[0])[1] == 0
    assert lockerdistributor.getUserAvailableAmount(accounts[0])[0] == 0
    assert tx.events['Claimed']['Amount'] ==tx.events['Transfer']['value']
    locks = lockerdistributor.getUserLocks(accounts[0])
    pretty_print_locks(locks);    




    



