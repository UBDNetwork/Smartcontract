import pytest
import logging
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
LOGGER = logging.getLogger(__name__)
STAKE_AMOUNT = 100_000e18
ADD_FUNDS_AMOUNT = 3333e18
MINT_UBD_AMOUNT = 995029850746269000000000000
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
WITH_DEBUG_EVENT = True
MONTH_WAIT = 10
PAY_AMOUNT = 100_0005_000e6
def test_prepare_ubd(accounts, ubd, sandbox1, usdt):
    sandbox1.setUBDToken(ubd, {'from':accounts[0]})
    sandbox1.setBeneficiary(accounts[2], {'from':accounts[0]})
    chain.sleep(10)
    
    usdt.approve(sandbox1, PAY_AMOUNT, {'from':accounts[0]})
    
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

#with amount bonus
def test_stake_ubd(accounts, ubd, staking, sandbox1, model_one, model_two):
    sandbox1.setStakingContract(staking, True, {"from": accounts[0]});
    
    with reverts('Ownable: caller is not the owner'):
        mr_tx = staking.modelRegister((0, 1e18, model_two), {"from": accounts[1]})
    mr_tx = staking.modelRegister((0, 1e18, model_two), {"from": accounts[0]})
    ubd.approve(staking, STAKE_AMOUNT,  {"from": accounts[0]})

    
    # struct Deposit {
    #         uint256 startDate;
    #         uint256 body;
    #         uint256[] amountParams;
    #         address[] addressParams;
    #         uint8 depositModelIndex;

    #     }
    d = (0,  
        STAKE_AMOUNT, 
        [0, 
         0,
         0, 
         #500000 # % of interests Available for claim from each accrued period 1%-10000
        ], 
        [], 
        1  #model index
    )
    logging.info('******* Deposit: {}'.format(STAKE_AMOUNT))

    #nonexists model
    with reverts("Model with this index not exist yet"):
        staking.deposit(d,{"from": accounts[0]})
    d = (0,  
        STAKE_AMOUNT, 
        [0, 
         0,
         0, 
         #500000 # % of interests Available for claim from each accrued period 1%-10000
        ], 
        [], 
        0  #model index
    )
    staking.deposit(d,{"from": accounts[0]})
    logging.info('User deposits: {}'.format(
        staking.getUserDeposits(accounts[0])
    ))
    assert ubd.balanceOf(staking) == STAKE_AMOUNT

    logging.info(model_two.calcInterests(d,3))

#10 monthes
def test_claim_interests(accounts, ubd, staking, sandbox1, model_two):
    logging.info('..... Wait for {} months '.format(MONTH_WAIT))
    chain.sleep(3600 * 24 * 30 * MONTH_WAIT ) # One Month

    
    logging.info('******* Claim Interests: {}'.format(''))
    deposits = staking.getUserDeposits(accounts[0])
    body_before = deposits[0][1]
    cl_tx = staking.claimInterests(0)
    
    logging.info('Events Transfer: {}'.format(
        cl_tx.events['Transfer']
    ))
    
    if WITH_DEBUG_EVENT : 
        [logging.info('\nEvent InterestsAccrued: {}'.format(e)) for e in cl_tx.events['InterestsAccrued']]
    logging.info('User deposits: {}'.format(
        deposits
    ))
    #assert cl_tx.return_value == cl_tx.events['Transfer'][1]['value']
    #assert ubd.balanceOf(staking) == deposits[0][1]

    #accrue interest
    body = body_before
    for i in range(10):
        rate = model_two.BASE_START() + model_two.BASE_STEP()*((i+1) // 4)
        rate = rate + model_two.AMOUNT_BONUS() * ((deposits[0][1] / 10**ubd.decimals()) // model_two.AMOUNT_STEP()) 
        body = body * (1 + rate / model_two.PERCENT_DENOMINATOR() / 100 / 12)  
        #body = body_before * (1 + rate / model_two.PERCENT_DENOMINATOR() / 100 / 12)  
        logging.info('month: {}, rate: {}, body_after: {}'.format(i+1, rate/model_two.PERCENT_DENOMINATOR(), body ))

    deposits = staking.getUserDeposits(accounts[0])

    assert body - deposits[0][1] < 4e17
    assert deposits[0][2][1] == 10
    assert deposits[0][2][0] == 0
    assert deposits[0][2][2] == 0
    assert ubd.balanceOf(staking) == deposits[0][1]
        





    
    
    
