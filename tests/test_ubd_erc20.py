import pytest
import logging
from brownie import Wei, reverts
LOGGER = logging.getLogger(__name__)

ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def test_approve_fail(accounts, erc20_ubd):
    with reverts("erc20_ubd: approve to the zero address"):
        erc20_ubd.approve(ZERO_ADDRESS, 1, {"from": accounts[0]})

def test_transfer_fail(accounts, erc20_ubd):
    with reverts("erc20_ubd: transfer to the zero address"):
        erc20_ubd.transfer(ZERO_ADDRESS, 1, {"from": accounts[0]})


def test_mint(accounts, erc20_ubd):
    with reverts("Only exchange contract"):
        erc20_ubd.mint(accounts[4], 1e18, {"from":accounts[1]})

    erc20_ubd.mint(accounts[1], 1e18, {"from":accounts[0]})
    assert erc20_ubd.balanceOf(accounts[1]) == 1e18

def test_erc20_ubd_transferFrom(accounts, erc20_ubd):
    erc20_ubd.transfer(accounts[2], 1, {"from": accounts[1]})
    with reverts("erc20_ubd: insufficient allowance"):
        erc20_ubd.transferFrom(accounts[2], accounts[3], 1, {"from": accounts[0]})
    erc20_ubd.approve(accounts[0], 1, {"from": accounts[2]})    
    erc20_ubd.transferFrom(accounts[2], accounts[0], 1, {"from": accounts[0]})
    assert erc20_ubd.balanceOf(accounts[0]) == 1
    assert erc20_ubd.balanceOf(accounts[2]) == 0

    #minter
    erc20_ubd.transfer(accounts[2], 1, {"from": accounts[0]})
    erc20_ubd.approve(accounts[0], 1, {"from": accounts[2]})
    erc20_ubd.transferFrom(accounts[2], accounts[0], 1, {"from": accounts[0]})
    assert erc20_ubd.balanceOf(accounts[0]) == 2
    assert erc20_ubd.balanceOf(accounts[2]) == 0

    erc20_ubd.approve(accounts[3], erc20_ubd.INITIAL_SUPPLY(), {"from": accounts[1]})
    with reverts("erc20_ubd: transfer amount exceeds balance"):
        erc20_ubd.transferFrom(accounts[1], accounts[3], erc20_ubd.INITIAL_SUPPLY(), {"from": accounts[3]})

def test_increaseAllowance(accounts, erc20_ubd):
    before = erc20_ubd.allowance(accounts[1], accounts[3])
    tx = erc20_ubd.increaseAllowance(accounts[3], 1e18, {'from': accounts[1]})
    assert len(tx.events['Approval']) == 1
    assert before == erc20_ubd.allowance(accounts[1], accounts[3]) - 1e18       


def test_decreaseAllowance(accounts, erc20_ubd):
    before = erc20_ubd.allowance(accounts[1], accounts[3])
    tx = erc20_ubd.decreaseAllowance(accounts[3], 1e18, {'from': accounts[1]})
    assert len(tx.events['Approval']) == 1
    assert before == erc20_ubd.allowance(accounts[1], accounts[3]) + 1e18       

def test_decreaseAllowance_fail(accounts, erc20_ubd):
    with reverts("erc20_ubd: decreased allowance below zero"):
        erc20_ubd.decreaseAllowance(accounts[4], 1e18, {'from': accounts[0]})

def test_mint(accounts, erc20_ubd):
    with reverts("Only distibutor contract"):
        erc20_ubd.mint(accounts[4], 1e18, {"from":accounts[1]})

    erc20_ubd.mint(accounts[4], 1e18, {"from":accounts[0]})
    assert erc20_ubd.balanceOf(accounts[4]) == 1e18
