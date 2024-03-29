import pytest
import logging
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1005e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
def test_usdt_to_ubd(accounts, ubd, sandbox1, usdt):
    sandbox1.setUBDToken(ubd, {'from':accounts[0]})
    sandbox1.setBeneficiary(accounts[2], {'from':accounts[0]})
    chain.sleep(10)
    
    usdt.approve(sandbox1, PAY_AMOUNT, {'from':accounts[0]})
    logging.info('Calculated UBD amount: {}'.format(
        sandbox1.calcOutUBDForExactInBASE(PAY_AMOUNT))
    )

    chain.sleep(10)
    logging.info('paymentTokens(usdt): {}, chain.time {}'.format(
        sandbox1.paymentTokens(usdt), chain.time() 
    ))
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    #logging.info('tx: {}'.format(tx.infwo()))
    assert tx.return_value == MINT_UBD_AMOUNT
    assert ubd.balanceOf(accounts[0]) == MINT_UBD_AMOUNT
    
def test_ubd_to_usdt(accounts, ubd, sandbox1, usdt):
    # In this test SANDBOX_1 - just EOA (accounts[9]). Hense we need approve
    #usdt.approve(sandbox1, usdt.balanceOf(accounts[9]), {'from':accounts[9]})
    logging.info('Calculated USDT amount: {}'.format(
        sandbox1.calcOutBASEForExactInUBD(MINT_UBD_AMOUNT))
    )
    ubd_balance = ubd.balanceOf(accounts[0])
    logging.info('UBD.balanceOf(acc0): {}'.format(
        ubd_balance
    ))

    usdt_balance = usdt.balanceOf(sandbox1)
    logging.info('USDT.balanceOf(sandbox1): {}'.format(
        usdt_balance
    ))

    fee_ubd_calc = sandbox1.getFeeFromInAmount(ubd, MINT_UBD_AMOUNT)
    logging.info(
        '\nCalculated Fee UBD: {}'
        '\nCalculated UBD Balance(acc0)  - Fee: {}'.format(
        fee_ubd_calc,
        ubd_balance - fee_ubd_calc 
    ))

    ubd.approve(sandbox1, MINT_UBD_AMOUNT, {'from':accounts[0]})
    chain.sleep(10)
    tx = sandbox1.swapExactInput(
        ubd, 
        MINT_UBD_AMOUNT,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    logging.info('tx.return_value: {}'.format(tx.return_value))
    usdt_balance = usdt.balanceOf(sandbox1)
    logging.info('USDT.balanceOf(SANDBOX1): {}'.format(
        usdt_balance
    ))
    assert ubd.balanceOf(accounts[0]) == 0

def test_usdt_to_ubd_100k(accounts, ubd, sandbox1, usdt):
    usdt.approve(sandbox1, PAY_AMOUNT * 100, {'from':accounts[0]})
    logging.info('Calculated UBD amount: {}'.format(
        sandbox1.calcOutUBDForExactInBASE(PAY_AMOUNT * 100))
    )
    
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT * 100,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    #logging.info('tx: {}'.format(tx.infwo()))
    assert tx.return_value == MINT_UBD_AMOUNT * 100
    assert ubd.balanceOf(accounts[0]) == MINT_UBD_AMOUNT * 100

#def test_init_market(accounts, ubd, sandbox1, sandbox2, treasury, usdt):

def test_topup_treasury(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    logging.info(
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{}'
        '\ntreasury.balance(eth):{}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury),
            treasury.balance()
    ))
    logging.info('UBDNetwork.state:{}'.format(markets.ubdNetwork()))
    init_market_registry(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury, 
        ubd, markets, wbtc, market_adapter, weth, usdc
    )

    logging.info('UBDNetwork.state:{}'.format(markets.getUBDNetworkInfo()))
    logging.info('Treasury assets:{}'.format(markets.treasuryERC20Assets()))
    accounts[7].transfer(mockuniv2, 40e18)

    tx = sandbox1.topupTreasury({'from':accounts[1]})
    logging.info('Ether transfer:{}'.format(tx.events['ReceivedEther']))
    [logging.info('\nfrom:{} to:{} value:{}'.format(x['from'],x['to'],x['value'])) for x in tx.events['Transfer']]
    logging.info(
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{}'
        '\ntreasury.balance(eth):{}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury),
            treasury.balance()
    ))

def test_buy_ubd_with_USDC(accounts, sandbox1, markets, ubd, usdt, usdc):
    usdc_amount = 100_000*10**usdc.decimals()
    usdt_amount = 100_000*10**usdt.decimals()
    usdc.transfer(accounts[1], usdc_amount, {'from':accounts[0]})
    usdc.approve(markets, usdc_amount, {'from':accounts[1]})
    usdt.approve(sandbox1, usdt_amount, {'from':accounts[1]})
    tx = sandbox1.swapExactInput(
        usdc, 
        usdc_amount,
        0,
        0,
        {'from':accounts[1]}
    )
    [logging.info('\nfrom:{} to:{} value:{}'.format(x['from'],x['to'],x['value'])) for x in tx.events['Transfer']]
    assert ubd.balanceOf(accounts[1]) == 99502487563000000000000

def test_topupTreasuryEmergency(accounts, sandbox1, markets, ubd, usdt, usdc, dai, treasury, wbtc):
    dai_amount = 100_000*10**dai.decimals()
    dai.transfer(sandbox1, dai_amount, {'from':accounts[0]})
    assert dai.balanceOf(sandbox1) == dai_amount
    treasury_wbtc_before = wbtc.balanceOf(treasury)
    treasury_eth_befroe = treasury.balance()
    tx = sandbox1.topupTreasuryEmergency(dai)

    [logging.info('\nfrom:{} to:{} value:{}'.format(x['from'],x['to'],x['value'])) for x in tx.events['Transfer']]
    assert wbtc.balanceOf(treasury) > treasury_wbtc_before
    assert treasury.balance() > treasury_eth_befroe

def test_mintReward(accounts, sandbox1, ubd):
    with reverts('Only for staking reward'):
        sandbox1.mintReward(accounts[0], 1, {'from': accounts[7]})
    sandbox1.setStakingContract(accounts[7], True, {'from': accounts[0]})
    sandbox1.mintReward(accounts[7], 1, {'from': accounts[7]})
    assert ubd.balanceOf(accounts[7]) == 1

def test_timelock(accounts, markets_timelocked, wbtc,
    mockuniv2, dai, usdt, sandbox1, sandbox2, treasury_t, ubd,  market_adapter, weth, usdc):
    init_market_registry(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury_t, 
        ubd, markets_timelocked, wbtc, market_adapter, weth, usdc
    )

    tx1 = markets_timelocked.addERC20AssetToTreasury((wbtc, 200), {'from':accounts[0]})
    chain.sleep(markets_timelocked.TIME_LOCK_DELAY())
    with reverts('Percent sum too much'):
        tx1 = markets_timelocked.addERC20AssetToTreasury((wbtc, 200), {'from':accounts[0]})
    tx1 = markets_timelocked.addERC20AssetToTreasury((wbtc, 70), {'from':accounts[0]})
    assert len(markets_timelocked.treasuryERC20Assets()) == 0
    assert len(tx1.events['ChangeScheduled']) == 1
    with reverts('Still pending'):
        tx2 = markets_timelocked.addERC20AssetToTreasury((wbtc, 70), {'from':accounts[0]})
    chain.sleep(markets_timelocked.TIME_LOCK_DELAY())
    tx3 = markets_timelocked.addERC20AssetToTreasury((wbtc, 70), {'from':accounts[0]})
    assert len(markets_timelocked.treasuryERC20Assets()) == 1
    assert len(tx3.events['Changed']) == 1