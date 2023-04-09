import pytest
import logging
from brownie import Wei, reverts
LOGGER = logging.getLogger(__name__)

ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def test_approve_fail(accounts, erc20):
    with reverts("ERC20: approve to the zero address"):
        erc20.approve(ZERO_ADDRESS, 1, {"from": accounts[0]})

def test_transfer_fail(accounts, erc20):
    with reverts("ERC20: transfer to the zero address"):
        erc20.transfer(ZERO_ADDRESS, 1, {"from": accounts[0]})

def test_erc20_transferFrom(accounts, erc20):
    erc20.transfer(accounts[2], 1, {"from": accounts[1]})
    with reverts("ERC20: insufficient allowance"):
        erc20.transferFrom(accounts[2], accounts[3], 1, {"from": accounts[0]})
    erc20.approve(accounts[0], 1, {"from": accounts[2]})    
    erc20.transferFrom(accounts[2], accounts[0], 1, {"from": accounts[0]})
    assert erc20.balanceOf(accounts[0]) == 1
    assert erc20.balanceOf(accounts[2]) == 0

    #minter
    erc20.transfer(accounts[2], 1, {"from": accounts[1]})
    erc20.approve(accounts[0], 1, {"from": accounts[2]})
    erc20.transferFrom(accounts[2], accounts[0], 1, {"from": accounts[0]})
    assert erc20.balanceOf(accounts[0]) == 2
    assert erc20.balanceOf(accounts[2]) == 0

    erc20.approve(accounts[3], erc20.INITIAL_SUPPLY(), {"from": accounts[1]})
    with reverts("ERC20: transfer amount exceeds balance"):
        erc20.transferFrom(accounts[1], accounts[3], erc20.INITIAL_SUPPLY(), {"from": accounts[3]})

def test_increaseAllowance(accounts, erc20):
    before = erc20.allowance(accounts[1], accounts[3])
    tx = erc20.increaseAllowance(accounts[3], 1e18, {'from': accounts[1]})
    assert len(tx.events['Approval']) == 1
    assert before == erc20.allowance(accounts[1], accounts[3]) - 1e18       


def test_decreaseAllowance(accounts, erc20):
    before = erc20.allowance(accounts[1], accounts[3])
    tx = erc20.decreaseAllowance(accounts[3], 1e18, {'from': accounts[1]})
    assert len(tx.events['Approval']) == 1
    assert before == erc20.allowance(accounts[1], accounts[3]) + 1e18       

def test_decreaseAllowance_fail(accounts, erc20):
    with reverts("ERC20: decreased allowance below zero"):
        erc20.decreaseAllowance(accounts[4], 1e18, {'from': accounts[0]})

def test_mint(accounts, erc20):
    with reverts("Only distibutor contarct"):
        erc20.mint(accounts[4], 1e18, {"from":accounts[1]})

    erc20.mint(accounts[4], 1e18, {"from":accounts[0]})
    assert erc20.balanceOf(accounts[4]) == 1e18
