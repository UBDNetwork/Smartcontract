import pytest
import logging
from brownie import Wei, reverts
LOGGER = logging.getLogger(__name__)


def test_erc20_params(accounts, erc20):
    assert erc20.totalSupply() == erc20.INITIAL_SUPPLY()
    assert erc20.symbol() == 'UBDN'
    assert erc20.name() == 'UBD Network'
    assert erc20.decimals() == 18
    assert erc20.INITIAL_SUPPLY() == 5_000_000e18
    assert erc20.balanceOf(accounts[1]) == erc20.INITIAL_SUPPLY()


