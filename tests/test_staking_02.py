import pytest
import logging
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
LOGGER = logging.getLogger(__name__)

STAKE_AMOUNT = 1000e18
ADD_FUNDS_AMOUNT = 3333e18
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
    assert tx.return_value == MINT_UBD_AMOUNT
    assert ubd.balanceOf(accounts[0]) == MINT_UBD_AMOUNT

def test_stake_ubd(accounts, ubd, staking, sandbox1, model_one):
    sandbox1.setStakingContract(staking, True, {"from": accounts[0]});
    #ubd_stake.mint(accounts[0], 1_000e18, {"from": accounts[0]})
    mr_tx = staking.modelRegister((0, 1e18, model_one), {"from": accounts[0]})
    ubd.approve(staking, STAKE_AMOUNT,  {"from": accounts[0]})

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
    d = (0, STAKE_AMOUNT, 
        [0, 
         0, 
         0,
         #500000 # % of interests Available for claim from each accrued period 1%-10000
        ], 
        [], 0
    )
    logging.info('******* Deposit: {}'.format(STAKE_AMOUNT))
    staking.deposit(d,{"from": accounts[0]})
    logging.info('User deposits: {}'.format(
        staking.getUserDeposits(accounts[0])
    ))
    assert ubd.balanceOf(staking) == STAKE_AMOUNT
    
def test_claim_interests(accounts, ubd, staking, sandbox1, model_one):
    logging.info('..... Wait for {} years '.format(1))
    chain.sleep(3600 * 24 * 30 * 12 ) # One years

    logging.info('******* Claim Interests: {}'.format(''))
    cl_tx = staking.claimInterests(0)
    
    logging.info('Events Transfer: {}'.format(
        cl_tx.events['Transfer']
    ))
    deposits = staking.getUserDeposits(accounts[0])

    #[logging.info('\nEvent InterestsAccrued: {}'.format(e)) for e in cl_tx.events['InterestsAccrued']]
    logging.info('User deposits: {}'.format(
        deposits
    ))
    if deposits[0][2][0] > 0:
        assert cl_tx.return_value == cl_tx.events['Transfer'][1]['value']
            
    assert ubd.balanceOf(staking) == deposits[0][1]

def test_add_funds(accounts, ubd, staking, sandbox1, model_one):
    logging.info('******* Wait for 3 month {}'.format(''))
    chain.sleep(3600 * 24 * 30 * 3 ) 
    logging.info('User deposits: {}'.format(
        staking.getUserDeposits(accounts[0])
    ))
    logging.info('UBD Balance of this contract: {}'.format(
        ubd.balanceOf(staking)
    ))
    ####################### Add Funds ######################
    ubd.approve(staking, ADD_FUNDS_AMOUNT,  {"from": accounts[0]})
    logging.info('******* Add funds: {}'.format('3333e18'))
    ad_tx = staking.addFundsToDeposit(0, ADD_FUNDS_AMOUNT, {"from": accounts[0]})
    #[logging.info('\nEvent InterestsAccrued: {}'.format(e)) for e in ad_tx.events['InterestsAccrued']]
    deposits = staking.getUserDeposits(accounts[0])
    logging.info('User deposits: {}'.format(
        deposits
    ))
    logging.info('UBD Balance of this contract: {}'.format(
        ubd.balanceOf(staking)
    ))
    assert ubd.balanceOf(staking) == deposits[0][1] + deposits[0][2][0]

def test_withdraw_funds(accounts, ubd, staking, sandbox1, model_one):
    
    logging.info('******* Wait for 12 month {}'.format(''))
    chain.sleep(3600 * 24 * 30 * 12 )
    logging.info('User deposits: {}'.format(
        staking.getUserDeposits(accounts[0])
    ))
    logging.info('UBD Balance of this contract: {}'.format(
        Wei(ubd.balanceOf(staking)).to('ether')
    )) 

    w_tx = staking.withdraw(0, {"from": accounts[0]})
    #[logging.info('\nEvent InterestsAccrued: {}'.format(e)) for e in w_tx.events['InterestsAccrued']]
    # deposits = staking.getUserDeposits(accounts[0])
    # logging.info('User deposits: {}'.format(
    #     deposits
    # ))
    # assert ubd.balanceOf(staking) == deposits[0][1] + deposits[0][2][0]
    assert ubd.balanceOf(staking) == 0
    
    
    
