import pytest
import logging
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
LOGGER = logging.getLogger(__name__)

STAKE_AMOUNT = 1005e6
MINT_UBD_AMOUNT = 995029850746269000000000000
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

PAY_AMOUNT = 100_0005_000e6
def test_prepare_ubd(accounts, ubd, sandbox1, usdt):
    sandbox1.setUBDToken(ubd, {'from':accounts[0]})
    sandbox1.setBeneficiary(accounts[2], {'from':accounts[0]})
    chain.sleep(10)
    
    usdt.approve(sandbox1, PAY_AMOUNT, {'from':accounts[0]})
    logging.info('Calculated UBD amount: {}'.format(
        sandbox1.calcOutUBDForExactInBASE(PAY_AMOUNT))
    )

    chain.sleep(10)
    logging.info('paymentTokens(usdt): {}, chain.time {}'.format(
        sandbox1.paymentTokens(usdt), chain.time() 
    ))
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    #logging.info('tx: {}'.format(tx.infwo()))
    assert tx.return_value == MINT_UBD_AMOUNT
    assert ubd.balanceOf(accounts[0]) == MINT_UBD_AMOUNT

def test_stake_ubd(accounts, ubd, staking, sandbox1, model_one):
    sandbox1.setStakingContract(staking, True, {"from": accounts[0]});
    #ubd_stake.mint(accounts[0], 1_000e18, {"from": accounts[0]})
    mr_tx = staking.modelRegister((0, 1e18, model_one), {"from": accounts[0]})
    ubd.approve(staking, 1_000e18,  {"from": accounts[0]})

    logging.info('Events in reg model: {}'.format(
        mr_tx.events
    ))
    # struct Deposit {
    #         uint256 startDate;
    #         uint256 body;
    #         uint256[] amountParams;
    #         address[] addressParams;
    #         uint8 depositModelIndex;

    #     }
    d = (0, 111, [0, 5000, 50000], [], 18)
    staking.deposit(0, d,{"from": accounts[0]})

    d2 = (0, 22222222222, [12,45, 333], [ZERO_ADDRESS], 18)
    staking.deposit(0, d2,{"from": accounts[0]})
    logging.info('User deposits: {}'.format(
        staking.getUserDeposits(accounts[0])
    ))

    staking.addFundsToDeposit(1, 33333333333, {"from": accounts[0]})
    logging.info('User deposits: {}'.format(
        staking.getUserDeposits(accounts[0])
    ))

    ci= staking.claimInterests(1, {"from": accounts[0]})
    logging.info('Events Transfer: {}'.format(
        ci.events['Transfer']
    ))
    logging.info('User deposits: {}'.format(
        staking.getUserDeposits(accounts[0])
    ))

    staking.withdraw(1, {"from": accounts[0]})

    
    
    
    
