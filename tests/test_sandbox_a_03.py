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
    
    usdt.approve(sandbox1, PAY_AMOUNT_USDT, {'from':accounts[0]})
    
    chain.sleep(10)
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT_USDT,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    assert tx.return_value == MINT_UBD_AMOUNT
    assert ubd.balanceOf(accounts[0]) == MINT_UBD_AMOUNT

    #try to topup treasury via usdt using topupTreasuryEmergency
    with reverts('Only for other assets'):
        sandbox1.topupTreasuryEmergency(usdt.address)

    #sandbox1.setPaymentTokenStatus(usdc.address, True, 5000, {'from': accounts[0]})
    chain.sleep(sandbox1.ADD_NEW_PAYMENT_TOKEN_TIMELOCK()+10)

    usdc.transfer(sandbox1.address, PAY_AMOUNT_USDC, {"from": accounts[0]})
    assert sandbox1.EXCHANGE_BASE_ASSET() == usdt.address
    with reverts('Ownable: caller is not the owner'):
        sandbox1.topupTreasuryEmergency(usdc.address, {"from": accounts[1]})
    sandbox1.topupTreasuryEmergency(usdc.address, {"from": accounts[0]})


    
