import pytest
import logging
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT_USDC = 1000e12
PAY_AMOUNT_USDT = 1005e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def test_usdt_to_ubd(accounts, ubd, sandbox1, usdt, usdc):
    sandbox1.setUBDToken(ubd, {'from':accounts[0]})
    sandbox1.setBeneficiary(accounts[1], {'from':accounts[0]})
    
    assert sandbox1.ubdTokenAddress() == ubd.address
    with reverts("Ownable: caller is not the owner"):
        sandbox1.setMinTopUp(1000, {"from": accounts[1]})
    sandbox1.setMinTopUp(1000, {"from": accounts[0]})
    assert sandbox1.MIN_TREASURY_TOPUP_AMOUNT() == 1000
