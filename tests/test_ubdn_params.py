import pytest
import logging
from brownie import Wei, reverts
LOGGER = logging.getLogger(__name__)


def test_erc20_params(accounts, erc20):
    assert erc20.totalSupply() == erc20.MAX_SUPPLY()
    assert erc20.symbol() == 'UBDN'
    assert erc20.name() == 'UBDN Token'
    assert erc20.decimals() == 18
    assert erc20.MAX_SUPPLY() == 50_000_000e18
    assert erc20.balanceOf(accounts[0]) == erc20.totalSupply()



