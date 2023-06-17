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

def test_calc_out(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})

    chain.sleep(lockerdistributor.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()+1)
    chain.mine()
    
    logging.info('Price and rest in round  1:{}'.format(
        lockerdistributor.priceInUnitsAndRemainByRound(1))
    )
    logging.info('Price and rest in round 2:{}'.format(
        lockerdistributor.priceInUnitsAndRemainByRound(2))
    )
    logging.info('Price and rest in round 10:{}'.format(
        lockerdistributor.priceInUnitsAndRemainByRound(10))
    )
    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdt, PAY_AMOUNT * 2)
    assert out_amount_calc == 1_000_000e18
    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdt, PAY_AMOUNT * 10)
    logging.info('outAmount from in {}:{:n}'.format(
        PAY_AMOUNT * 10,
        Wei(out_amount_calc).to('ether')
    ))

def test_calc_in(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt,1_500_000e18)
    assert in_amount_calc == 3_500_000e6
    logging.info('inAmount for out {}:{:n}'.format(
        1_500_000e18,
        Wei(in_amount_calc).to('ether')
    ))
   