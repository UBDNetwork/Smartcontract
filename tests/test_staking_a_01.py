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
    staking.deposit(d,{"from": accounts[0]})
    #logging.info('User deposits: {}'.format(
    #    staking.getUserDeposits(accounts[0])
    #))
    assert ubd.balanceOf(staking) == STAKE_AMOUNT

    #logging.info(model_two.calcInterests(d,3))

#10 monthes - nothing claim, only accrue interests
def test_claim_interests(accounts, ubd, staking, sandbox1, model_two):
    logging.info('..... Wait for {} months '.format(MONTH_WAIT))
    chain.sleep(3600 * 24 * 30 * MONTH_WAIT ) # ten Months

    
    logging.info('******* Claim Interests: {}'.format(''))
    deposits = staking.getUserDeposits(accounts[0])
    body_before = deposits[0][1]
    logging.info(ubd.balanceOf(accounts[0]))
    cl_tx = staking.claimInterests(0)
    logging.info(ubd.balanceOf(accounts[0]))
    
    #logging.info('Events Transfer: {}'.format(
    #    cl_tx.events['Transfer']
    #))

    if os.environ.get("WITH_DEBUG_EVENT") == 'True': 
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
        rate = rate + model_two.AMOUNT_BONUS() * ((deposits[0][1] / 10**ubd.decimals()) // model_two.AMOUNT_STEP()) #add bonus for amount 
        body = body * (1 + rate / model_two.PERCENT_DENOMINATOR() / 100 / 12)  
        #body = body_before * (1 + rate / model_two.PERCENT_DENOMINATOR() / 100 / 12)  
        logging.info('month: {}, rate: {}, body_after: {}'.format(i+1, rate/model_two.PERCENT_DENOMINATOR(), body ))

    deposits = staking.getUserDeposits(accounts[0])

    assert body - deposits[0][1] < 4e17
    assert deposits[0][2][1] == 10
    assert deposits[0][2][0] == 0
    assert deposits[0][2][2] == 0
    assert ubd.balanceOf(staking) == deposits[0][1]

#without amount bonus, with claim percent
def test_stake_ubd_1(accounts, usdt, ubd, staking, sandbox1, model_one, model_two):

    usdt.approve(sandbox1, PAY_AMOUNT/10, {'from':accounts[0]})
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT/10,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )

    ubd.approve(staking, STAKE_AMOUNT/10,  {"from": accounts[0]})


    # struct Deposit {
    #         uint256 startDate;
    #         uint256 body;
    #         uint256[] amountParams;
    #         address[] addressParams;
    #         uint8 depositModelIndex;

    #     }
    t = chain.time()
    d = (0,  
        STAKE_AMOUNT/10, 
        [0, 
         0,
         300000 # % of interests Available for claim from each accrued period 1%-10000
        ], 
        [], 
        0  #model index
    )
    logging.info('******* Deposit: {}'.format(STAKE_AMOUNT))

    staking.deposit(d,{"from": accounts[0]})
    #logging.info('User deposits: {}'.format(
    #    staking.getUserDeposits(accounts[0])
    #))
    deposits = staking.getUserDeposits(accounts[0])
    assert ubd.balanceOf(staking) == deposits[0][1] + deposits[1][1]

    assert staking.getUserDepositByIndex(accounts[0], 1)[0] == t
    assert staking.getUserDepositByIndex(accounts[0], 1)[1] == d[1]
    assert staking.getUserDepositByIndex(accounts[0], 1)[2] == d[2]
    assert staking.getUserDepositByIndex(accounts[0], 1)[3] == d[3]
    assert staking.getUserDepositByIndex(accounts[0], 1)[4] == d[4]

#10 monthes, 30% claim 
def test_claim_interests_1(accounts, ubd, staking, sandbox1, model_two):
    logging.info('..... Wait for {} months '.format(MONTH_WAIT))
    chain.sleep(3600 * 24 * 30 * MONTH_WAIT ) # ten Months

    balance_acc_before = ubd.balanceOf(accounts[0]) 
    
    logging.info('******* Claim Interests: {}'.format(''))
    deposits = staking.getUserDeposits(accounts[0])
    body_before = deposits[1][1]

    #claim interests of claimable deposit
    cl_tx = staking.claimInterests(1)
    
    if os.environ.get("WITH_DEBUG_EVENT") == 'True': 
        [logging.info('\nEvent InterestsAccrued: {}'.format(e)) for e in cl_tx.events['InterestsAccrued']]
    logging.info('User deposits: {}'.format(
        deposits
    ))
    
    #accrue interest
    body = body_before
    claimable_interests = 0
    claimable_interests_all = 0
    for i in range(10):
        rate = model_two.BASE_START() + model_two.BASE_STEP()*((i+1) // 4)
        interests = body * rate / model_two.PERCENT_DENOMINATOR() / 100 / 12
        body = body + interests * (1 - deposits[1][2][2] / model_two.PERCENT_DENOMINATOR() / 100)
        claimable_interests = interests * deposits[1][2][2] / model_two.PERCENT_DENOMINATOR() / 100
        claimable_interests_all = claimable_interests_all + claimable_interests

        #body = body_before * (1 + rate / model_two.PERCENT_DENOMINATOR() / 100 / 12)  
        logging.info('month: {}, rate: {}, body_after: {}, claimable_interests_added_per_month: {}'.format(i+1, rate/model_two.PERCENT_DENOMINATOR(), body, claimable_interests ))

    deposits = staking.getUserDeposits(accounts[0])

    #check getters
    assert staking.getUserDeposits2(accounts[0]) == deposits
    assert staking.getUserDepositsCount(accounts[0]) == 2
    assert staking.getUserDepositByIndex2(accounts[0], 1)[0][0] == deposits[1][0]
    assert staking.getUserDepositByIndex2(accounts[0], 1)[0][1] == deposits[1][1]
    assert staking.getUserDepositByIndex2(accounts[0], 1)[0][2] == deposits[1][4]
    assert staking.getUserDepositByIndex2(accounts[0], 1)[1] == deposits[1][2]
    assert staking.getUserDepositByIndex2(accounts[0], 1)[2] == deposits[1][3]

    #check deposit after claim
    assert body - deposits[1][1] < 3e16
    assert deposits[1][2][1] == 10
    assert deposits[1][2][0] == 0
    assert deposits[1][2][2] == 300000
    assert ubd.balanceOf(staking) == deposits[1][1] + deposits[0][1]
    assert balance_acc_before + claimable_interests_all - ubd.balanceOf(accounts[0]) < 2e16

#with  the accruing of interests
def test_withdraw(accounts, ubd, staking, sandbox1, model_two):
    with reverts('Index out of range'):
        staking.withdraw(2)
    balance_acc_before = ubd.balanceOf(accounts[0]) 
    deposits = staking.getUserDeposits(accounts[0])
    wt_tx = staking.withdraw(0)

    if os.environ.get("WITH_DEBUG_EVENT") == 'True': 
        [logging.info('\nEvent InterestsAccrued: {}'.format(e)) for e in wt_tx.events['InterestsAccrued']]

    #accrue interest
    body = deposits[0][1]
    for i in range(10,20):
        rate = model_two.BASE_START() + model_two.BASE_STEP()*((i+1) // 4)
        rate = rate + model_two.AMOUNT_BONUS() * ((deposits[0][1] / 10**ubd.decimals()) // model_two.AMOUNT_STEP()) 
        body = body * (1 + rate / model_two.PERCENT_DENOMINATOR() / 100 / 12)  
        #body = body_before * (1 + rate / model_two.PERCENT_DENOMINATOR() / 100 / 12)  
        logging.info('month: {}, rate: {}, body_after: {}'.format(i+1, rate/model_two.PERCENT_DENOMINATOR(), body ))


    deposits_new = staking.getUserDeposits(accounts[0])

    assert balance_acc_before + body - ubd.balanceOf(accounts[0]) < 5e17
    assert len(deposits_new) == 1
    assert deposits_new[0] == deposits[1]

#10 monthes, 30% claim, add funds 
def test_addFunds(accounts, ubd, staking, sandbox1, model_two):
    ubd.approve(staking, 1,  {"from": accounts[0]})
    deposits = staking.getUserDeposits(accounts[0])
    body_before = deposits[0][1]
    balance_acc_before = ubd.balanceOf(accounts[0]) 
    with reverts("Index out of range"):
        staking.addFundsToDeposit(2,1)

    #move time
    chain.sleep(3600 * 24 * 30 * MONTH_WAIT ) # ten Months
    ubd.approve(staking, STAKE_AMOUNT,  {"from": accounts[0]})
    ad_tx = staking.addFundsToDeposit(0,STAKE_AMOUNT)
    if os.environ.get("WITH_DEBUG_EVENT") == 'True': 
        [logging.info('\nEvent InterestsAccrued: {}'.format(e)) for e in ad_tx.events['InterestsAccrued']]
    

    #accrue interest
    body = body_before
    claimable_interests = 0
    claimable_interests_all = 0
    for i in range(10,20):
        rate = model_two.BASE_START() + model_two.BASE_STEP()*((i+1) // 4)
        rate = rate + model_two.AMOUNT_BONUS() * ((deposits[0][1] / 10**ubd.decimals()) // model_two.AMOUNT_STEP())  #add bonus for amount 
        interests = body * rate / model_two.PERCENT_DENOMINATOR() / 100 / 12
        body = body + interests * (1 - deposits[0][2][2] / model_two.PERCENT_DENOMINATOR() / 100)
        claimable_interests = interests * deposits[0][2][2] / model_two.PERCENT_DENOMINATOR() / 100
        claimable_interests_all = claimable_interests_all + claimable_interests

        #body = body_before * (1 + rate / model_two.PERCENT_DENOMINATOR() / 100 / 12)  
        logging.info('month: {}, rate: {}, body_after: {}, claimable_interests_added_per_month: {}'.format(i+1, rate/model_two.PERCENT_DENOMINATOR(), body, claimable_interests ))

    deposits = staking.getUserDeposits(accounts[0])

    
    assert body + STAKE_AMOUNT - deposits[0][1] < 2e16
    assert deposits[0][2][1] == 20
    assert deposits[0][2][0] - claimable_interests_all < 9e15
    assert deposits[0][2][2] == 300000
    assert ubd.balanceOf(staking) == deposits[0][1] + deposits[0][2][0]
    assert balance_acc_before - STAKE_AMOUNT - ubd.balanceOf(accounts[0]) == 0

def test_withdrawEmergency(accounts, ubd, staking, sandbox1, model_two):
    chain.sleep(3600 * 24 * 30 * MONTH_WAIT ) # ten Months
    deposits = staking.getUserDeposits(accounts[0])
    balance_acc_before = ubd.balanceOf(accounts[0])
    staking.withdrawEmergency(0)
    assert ubd.balanceOf(staking) == 0
    assert balance_acc_before + deposits[0][1] + deposits[0][2][0] == ubd.balanceOf(accounts[0])
















        





    
    
    
