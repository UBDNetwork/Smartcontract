import pytest
import logging
from brownie import Wei, reverts
LOGGER = logging.getLogger(__name__)


def test_erc20_ubd_params(accounts, erc20_ubd):
    assert erc20_ubd.totalSupply() == erc20.INITIAL_SUPPLY()
    assert erc20_ubd.symbol() == 'UBD'
    assert erc20_ubd.name() == 'United Blockchain Dollar'
    assert erc20_ubd.decimals() == 18
    assert erc20_ubd.balanceOf(accounts[0]) == 0


