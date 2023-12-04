import pytest
import logging
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
import os
LOGGER = logging.getLogger(__name__)
STAKE_AMOUNT = 100_000e18
ADD_FUNDS_AMOUNT = 3333e18
MINT_UBD_AMOUNT = 995029850746269000000000000
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
#WITH_DEBUG_EVENT = True
MONTH_WAIT = 120
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


#with amount bonus, without claim percent
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
    tx = staking.deposit(d,{"from": accounts[0]})
    logging.info('User deposits: {}'.format(
        staking.getUserDeposits(accounts[0])
    ))
    assert ubd.balanceOf(staking) == STAKE_AMOUNT
    assert tx.events['DepositNew']['User'] == accounts[0]
    assert tx.events['DepositNew']['DepositIndex'] == 0
    assert tx.events['DepositNew']['DepositValue'] == STAKE_AMOUNT


#10 monthes - nothing claim, only accrue
def test_claim_interests(accounts, ubd, staking, sandbox1, model_two):
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

    cal_int = staking.calcInterests(d, 120)

    chain.sleep(3600 * 24 * 30 * MONTH_WAIT ) # ten Months

    
    logging.info('******* Claim Interests: {}'.format(''))
    deposits = staking.getUserDeposits(accounts[0])
    body_before = deposits[0][1]
    logging.info(ubd.balanceOf(accounts[0]))
    cl_tx = staking.claimInterests(0)
    logging.info(ubd.balanceOf(accounts[0]))
    
    logging.info('Events Transfer: {}'.format(
        cl_tx.events['Transfer']
    ))
    
    logging.info(os.environ.get("WITH_DEBUG_EVENT") )

    if os.environ.get("WITH_DEBUG_EVENT") == 'True': 
        [logging.info('\nEvent InterestsAccrued: {}'.format(e)) for e in cl_tx.events['InterestsAccrued']]
    logging.info('User deposits: {}'.format(
        deposits
    ))
    #assert cl_tx.return_value == cl_tx.events['Transfer'][1]['value']
    #assert ubd.balanceOf(staking) == deposits[0][1]

    #accrue interest
    body = body_before
    for i in range(120):
        if i < 95:
            rate = model_two.BASE_START() + model_two.BASE_STEP()*((i+1) // 4)
            rate = rate + model_two.AMOUNT_BONUS() * ((deposits[0][1] / 10**ubd.decimals()) // model_two.AMOUNT_STEP()) #add bonus for amount 
        body = body * (1 + rate / model_two.PERCENT_DENOMINATOR() / 100 / 12)  
        #body = body_before * (1 + rate / model_two.PERCENT_DENOMINATOR() / 100 / 12)  
        logging.info('month: {}, rate: {}, body_after: {}'.format(i+1, rate/model_two.PERCENT_DENOMINATOR(), body ))

    deposits = staking.getUserDeposits(accounts[0])

    assert body - deposits[0][1] < 1e9
    assert deposits[0][2][1] == 120
    assert deposits[0][2][0] == 0
    assert deposits[0][2][2] == 0
    assert ubd.balanceOf(staking) == deposits[0][1]
    assert deposits[0][1] - STAKE_AMOUNT == cal_int[1] #check calculated interests - staking.calcInterests

def test_prepare_ubd_1(accounts, ubd, sandbox1, usdt):
    usdt.approve(sandbox1, 25e6*10**6, {'from':accounts[0]})
    
    tx = sandbox1.swapExactInput(
        usdt, 
        25e6*10**6,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    logging.info(ubd.balanceOf(accounts[0]))

#stake huge amount to check amount bonus
def test_stake_ubd_1(accounts, ubd, staking, sandbox1, model_one, model_two):
    ubd.approve(staking, 24e24)
    d = (0,  
        24e24, 
        [0, 
         0,
         0, 
         #500000 # % of interests Available for claim from each accrued period 1%-10000
        ], 
        [], 
        0  #model index
    )
    tx = staking.deposit(d,{"from": accounts[0]})
    logging.info('User deposits: {}'.format(
        staking.getUserDeposits(accounts[0])
    ))

#5 monthes - nothing claim, only accrue
def test_claim_interests(accounts, ubd, staking, sandbox1, model_two):
    
    chain.sleep(3600 * 24 * 30 * 5 ) # five Months

    logging.info('******* Claim Interests: {}'.format(''))
    deposits = staking.getUserDeposits(accounts[0])
    body_before = deposits[1][1]
    cl_tx = staking.claimInterests(1)

    deposits = staking.getUserDeposits(accounts[0])
    
    if os.environ.get("WITH_DEBUG_EVENT") == 'True': 
        [logging.info('\nEvent InterestsAccrued: {}'.format(e)) for e in cl_tx.events['InterestsAccrued']]
    logging.info('User deposits: {}'.format(
        deposits
    ))

    #accrue interest
    body = body_before

    #logging.info(body)
    for i in range(5):
        rate = model_two.BASE_MAX()
        body = body * (1 + rate / model_two.PERCENT_DENOMINATOR() / 100 / 12)  
        #body = body_before * (1 + rate / model_two.PERCENT_DENOMINATOR() / 100 / 12)  
        logging.info('month: {}, rate: {}, body_after: {}'.format(i+1, rate/model_two.PERCENT_DENOMINATOR(), body ))

    deposits = staking.getUserDeposits(accounts[0])

    assert body - deposits[1][1] < 5e10
    assert deposits[1][2][1] == 5
    assert deposits[1][2][0] == 0
    assert deposits[1][2][2] == 0

def test_model(accounts, ubd, staking, sandbox1, model_two, DepositModel_02):
    staking.editModelEndDate(0, 0)
    ubd.approve(staking, 1)
    d = (0,  
        1, 
        [0, 
         0,
         0, 
         #500000 # % of interests Available for claim from each accrued period 1%-10000
        ], 
        [], 
        0  #model index
    )
    with reverts('Model not valid already'):
        tx = staking.deposit(d,{"from": accounts[0]})

    model_three = DepositModel_02.deploy(18, {"from": accounts[0]})
    staking.modelRegister((1e15, 1e18, model_three), {"from": accounts[0]})
    d = (0,  
        1, 
        [0, 
         0,
         0, 
         #500000 # % of interests Available for claim from each accrued period 1%-10000
        ], 
        [], 
        1  #model index
    )
    with reverts('Model not valid yet'):
        tx = staking.deposit(d,{"from": accounts[0]})


    




















        





    
    
    
