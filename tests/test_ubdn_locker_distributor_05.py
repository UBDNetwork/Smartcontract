import pytest
import logging
from brownie import Wei, reverts, chain
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1000000


def test_buy(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    lockerdistributor.setPaymentTokenStatus(usdt, True, {'from':accounts[0]})
    lockerdistributor.setDistributionToken(ubdnlocked, {'from':accounts[0]})


    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, (PAY_AMOUNT+1)*10**ubdnlocked.decimals())


    in_amount_calc_manual = 0  
    last_price  = lockerdistributor.START_PRICE() +1
    in_amount_calc_manual= in_amount_calc_manual + PAY_AMOUNT*last_price*10**usdt.decimals()
    last_price = last_price + lockerdistributor.PRICE_INCREASE_STEP()
    in_amount_calc_manual= in_amount_calc_manual + 1*last_price*10**usdt.decimals()

    assert in_amount_calc == in_amount_calc_manual
    logging.info(in_amount_calc)

    out_amount_calc = lockerdistributor.calcTokensForExactStable(usdt, in_amount_calc)
    assert out_amount_calc == (PAY_AMOUNT+1)*10**ubdnlocked.decimals()
    
    assert in_amount_calc == (PAY_AMOUNT*lockerdistributor.priceInUnitsAndRemainByRound(1)[0] + 1*lockerdistributor.priceInUnitsAndRemainByRound(2)[0])*10**usdt.decimals()
    usdt.transfer(accounts[1], in_amount_calc, {'from':accounts[0]})
    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[1]})
    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[1]})
    assert lockerdistributor.distributedAmount() == (PAY_AMOUNT+1)*10**ubdnlocked.decimals()
    assert ubdnlocked.balanceOf(lockerdistributor.address) == lockerdistributor.distributedAmount()

    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[1] == PAY_AMOUNT-1

    assert lockerdistributor.getCurrentRound() == 2
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[0] == 3
    assert lockerdistributor.priceInUnitsAndRemainByRound(2)[1] == (PAY_AMOUNT-1)*10**ubdnlocked.decimals()
    assert lockerdistributor.priceInUnitsAndRemainByRound(1)[0] == 2 #check price

    assert lockerdistributor.getUserLocks(accounts[1])[0][0] == (PAY_AMOUNT+1)*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[1])[0][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[1])) == 1


    #try to claim - lock has not finished yet
    with reverts("Nothing to claim"):
        lockerdistributor.claimTokens({"from": accounts[1]})
    with reverts("Nothing to claim"):
        tx = lockerdistributor.claimTokens({"from": accounts[0]})

def test_buy_zero_amount(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    tx = lockerdistributor.buyTokensForExactStable(usdt, 0, {'from':accounts[1]})
    logging.info(tx.events['Transfer'])
    #we got zero record in user locks array here!!!!

def test_claim(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    chain.sleep(90*24*3600)
    chain.mine()
    balance_before =  ubdnlocked.balanceOf(accounts[1])
    tx = lockerdistributor.claimTokens({"from": accounts[1]})
    #try to claim again   
    with reverts("Nothing to claim"):
        tx = lockerdistributor.claimTokens({"from": accounts[1]})    
    assert ubdnlocked.balanceOf(lockerdistributor.address) == 0
    assert ubdnlocked.balanceOf(accounts[1]) == balance_before + lockerdistributor.distributedAmount()
    assert lockerdistributor.getUserLocks(accounts[1])[1][0] == 0 #check amount of lock

def test_buy_1(accounts, ubdnlocked, lockerdistributor, usdt, usdc):
    #buy 100 tokens
    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, 100*10**ubdnlocked.decimals())


    usdt.transfer(accounts[1], in_amount_calc, {'from':accounts[0]})
    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[1]})
    before_amount_distr = lockerdistributor.distributedAmount()
    before_acc1_ub = ubdnlocked.balanceOf(accounts[1])
    before_acc0_ub = ubdnlocked.balanceOf(accounts[0])
    before_l_ub = ubdnlocked.balanceOf(lockerdistributor.address)
    before_acc1_us = usdt.balanceOf(accounts[1])
    before_acc0_us = usdt.balanceOf(accounts[0])
    before_l_us = usdt.balanceOf(lockerdistributor.address)

    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[1]})

    assert lockerdistributor.distributedAmount() == before_amount_distr + 100*10**ubdnlocked.decimals()
    assert usdt.balanceOf(accounts[1]) == 0
    assert usdt.balanceOf(accounts[0]) == in_amount_calc + before_acc0_us
    assert usdt.balanceOf(lockerdistributor.address) == before_l_us

    assert ubdnlocked.balanceOf(accounts[1]) == before_acc1_ub
    assert ubdnlocked.balanceOf(accounts[0]) == before_acc0_ub
    assert ubdnlocked.balanceOf(lockerdistributor.address) == before_l_ub + 100*10**ubdnlocked.decimals()

    assert lockerdistributor.getUserLocks(accounts[1])[2][0] == 100*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[1])[2][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[1])) == 3
    assert lockerdistributor.getCurrentRound() == 2

    chain.sleep(90*24*3600+1)
    chain.mine()

    balance_before =  ubdnlocked.balanceOf(accounts[1])
    tx = lockerdistributor.claimTokens({"from": accounts[1]})    
    assert ubdnlocked.balanceOf(lockerdistributor.address) == 0
    assert ubdnlocked.balanceOf(accounts[1]) == balance_before + 100*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[1])[2][0] == 0

    #buy again - 200 tokens
    in_amount_calc = lockerdistributor.calcStableForExactTokens(usdt.address, 200*10**ubdnlocked.decimals())
    usdt.transfer(accounts[1], in_amount_calc, {'from':accounts[0]})
    usdt.approve(lockerdistributor, in_amount_calc, {'from':accounts[1]})
    before_amount_distr = lockerdistributor.distributedAmount()
    before_acc1_ub = ubdnlocked.balanceOf(accounts[1])
    before_acc0_ub = ubdnlocked.balanceOf(accounts[0])
    before_l_ub = ubdnlocked.balanceOf(lockerdistributor.address)
    before_acc1_us = usdt.balanceOf(accounts[1])
    before_acc0_us = usdt.balanceOf(accounts[0])
    before_l_us = usdt.balanceOf(lockerdistributor.address)

    tx = lockerdistributor.buyTokensForExactStable(usdt, in_amount_calc, {'from':accounts[1]})

    assert lockerdistributor.distributedAmount() == before_amount_distr + 200*10**ubdnlocked.decimals()
    assert usdt.balanceOf(accounts[1]) == 0
    assert usdt.balanceOf(accounts[0]) == in_amount_calc + before_acc0_us
    assert usdt.balanceOf(lockerdistributor.address) == before_l_us

    assert ubdnlocked.balanceOf(accounts[1]) == before_acc1_ub
    assert ubdnlocked.balanceOf(accounts[0]) == before_acc0_ub
    assert ubdnlocked.balanceOf(lockerdistributor.address) == before_l_ub + 200*10**ubdnlocked.decimals()

    assert lockerdistributor.getUserLocks(accounts[1])[3][0] == 200*10**ubdnlocked.decimals()
    assert lockerdistributor.getUserLocks(accounts[1])[3][1] >= chain.time() + 90*24*3600-1
    assert len(lockerdistributor.getUserLocks(accounts[1])) == 4
    assert lockerdistributor.getCurrentRound() == 2




        
#   +попробовать заклаймить, когда блокировка не закончилась
#   +попробовать 0 отправить при покупке                                  !!!!! отправляется. И куча событий переводов создается. Я бы реверт тут воткнул brownie test ./tests/test_ubdn_locker_distributor_05.py
#   +попробовать заклаймить, когда все заклаймил
#   +купил потом заклаймил, потом снова купил, потом снова заклаймил, потом снова пытаемся клаймить
#   +сделать несколько покупок в разное время пользователем. Попытаться заклаймить все разом, когда последняя блокировка наступила
#   сделать разными адресами покупки в  разное время. Каждым адрес пытается сделать клаймы разом в первую возможность разблокировки 
#   +купить за токены с разным количеством знаков после запятой - покупать в одном раунде за dai, usdt, usdc
#   +осталось в раунде 5 токенов и покупает кто-то 100 токенов - цена из двух раундов       !!! brownie test ./tests/test_ubdn_locker_distributor_07.py
   


    