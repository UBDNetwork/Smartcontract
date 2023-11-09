import pytest
import logging
import math
from brownie import Wei, reverts, chain
from help_init_registry import init_market_registry
LOGGER = logging.getLogger(__name__)

PAY_AMOUNT = 1005e6
MINT_UBD_AMOUNT = 1000e18
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
def test_usdt_to_ubd(accounts, ubd, sandbox1, usdt):
    logging.info('!!!!!!!!!!!!!!!!!   exchange from usdt to ubd    !!!!!!!!!!!!!!!')
    sandbox1.setUBDToken(ubd, {'from':accounts[0]})
    sandbox1.setBeneficiary(accounts[1], {'from':accounts[0]})
    
    usdt.approve(sandbox1, PAY_AMOUNT, {'from':accounts[0]})
    
    chain.sleep(10)
    
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



def test_usdt_to_ubd_100k_1(accounts, ubd, sandbox1, usdt):
    usdt.approve(sandbox1, PAY_AMOUNT * 100, {'from':accounts[0]})

    before_ubd_acc0 = ubd.balanceOf(accounts[0])
    
    tx = sandbox1.swapExactInput(
        usdt, 
        PAY_AMOUNT * 100,
        0,
        0,
        ZERO_ADDRESS, 
        {'from':accounts[0]}
    )
    
    assert tx.return_value == MINT_UBD_AMOUNT * 100
    assert ubd.balanceOf(accounts[0]) == before_ubd_acc0 + MINT_UBD_AMOUNT * 100

def test_topup_treasury_from_sandbox1(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc):
    logging.info('!!!!!!!!!!!!!!!!!   topup treasury from sandbox1 - after changing of erc20 token in treasury !!!!!!!!!!!!!!!')
    
    init_market_registry(accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, treasury, ubd, markets, wbtc, market_adapter, weth, usdc)
    logging.info(
        '\nSandbox1.balance(usdt):{}'
        '\ntreasury.balance(wbtc):{}'
        '\ntreasury.balance(eth):{}'.format(
            usdt.balanceOf(sandbox1),
            wbtc.balanceOf(treasury),
            treasury.balance()
    ))
    logging.info('UBDNetwork.state:{}'.format(markets.ubdNetwork()))
    logging.info('UBDNetwork.state:{}'.format(markets.getUBDNetworkInfo()))
    accounts[1].transfer(mockuniv2, 10e18)

    #sandbox has 1% of balance > 1000 usdt - can exchange usdt to ether and wbtc
    before_usdt_sandbox = usdt.balanceOf(sandbox1.address)
    tx = sandbox1.topupTreasury({'from':accounts[1]})

    logging.info(tx.events['ReceivedEther'])
    assert tx.events['ReceivedEther'][0][''] == treasury.balance()



    assert usdt.balanceOf(sandbox1.address) == before_usdt_sandbox - before_usdt_sandbox/100  #-1%


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

    #exchange 1% usdt of sandbox1 to swap => 50% ETH and 50% WBTC + 1% slippage in defi happened - treasury got assets 1% less due to slippage
    assert wbtc.balanceOf(treasury) - (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, wbtc.address)[0])*10**wbtc.decimals()/10**usdt.decimals() <=100
    assert (before_usdt_sandbox/100/2/mockuniv2.rates(usdt.address, weth.address)[0])*10**weth.decimals()/10**usdt.decimals() - treasury.balance()  <= 3000000000000

def test_treasury_change_asset(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, usdc, wbnb):
    
    mockuniv2.setRate(usdt.address, wbtc.address, (100000, 1))
    mockuniv2.setRate(wbtc.address, usdt.address, (1, 100000))
    
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))

    with reverts('Ownable: caller is not the owner'):
        markets.setMarketParams(wbnb, (market_adapter, market_adapter, 0), {'from':accounts[1]})
    markets.setMarketParams(wbnb, (market_adapter, market_adapter, 0), {'from':accounts[0]})
    with reverts("Ownable: caller is not the owner"):
        markets.addERC20AssetToTreasury((wbnb, 50), {'from':accounts[1]})
    with reverts("Percent sum too much"):
        markets.addERC20AssetToTreasury((wbnb, 50), {'from':accounts[0]})

    with reverts('Ownable: caller is not the owner'):
        markets.removeERC20AssetFromTreasury(wbtc, {"from": accounts[1]})
    #remove wbtc from treasury assets and add wbnb
    with reverts('Cant remove asset with non zero balance'):
        markets.removeERC20AssetFromTreasury(wbtc, {"from": accounts[0]})

    #change asset shares. Rebalance happened
    logging.info('wbtc balance before rebalance = {}'.format(wbtc.balanceOf(treasury)))
    with reverts('Ownable: caller is not the owner'):
        markets.editAssetShares([0], {"from": accounts[1]})
    markets.editAssetShares([0], {"from": accounts[0]})
    logging.info('wbtc balance after rebalance = {}'.format(wbtc.balanceOf(treasury)))
    markets.editAssetShares([0], {"from": accounts[0]})

    logging.info('wbtc balance after rebalance = {}'.format(wbtc.balanceOf(treasury)))

    #rebalance happened. Can remove asset
    markets.removeERC20AssetFromTreasury(wbtc, {"from": accounts[0]})
    

    markets.addERC20AssetToTreasury((wbnb, 50), {'from':accounts[0]})

    #wbnb is treasuryERC20Assets
    assert markets.treasuryERC20Assets()[0] == wbnb.address
    assert len(markets.treasuryERC20Assets()) == 1
    
    logging.info('getCollateralLevelM10 after delete wbtc from assets= {}'.format(markets.getCollateralLevelM10()))
    '''
    sandbox1.setMinTopUp(990, {"from": accounts[0]})
    #check - after topup treasury wbtc balance will not be changed but wbnb balance will be changed

    before_wbtc = wbtc.balanceOf(treasury)
    before_wbnb =  wbnb.balanceOf(treasury)
    before_eth = treasury.balance()
    before_usdt_sandbox1 = usdt.balanceOf(sandbox1)

    #again topup treasury
    chain.sleep(sandbox1.TREASURY_TOPUP_PERIOD() + 10)
    tx = sandbox1.topupTreasury({'from':accounts[1]})

    assert wbnb.balanceOf(treasury) - (before_usdt_sandbox1/100/2/mockuniv2.rates(usdt.address, wbnb.address)[0])*10**wbnb.decimals()/10**usdt.decimals() == 0
    assert (before_usdt_sandbox1/100/2/mockuniv2.rates(usdt.address, weth.address)[0])*10**weth.decimals()/10**usdt.decimals() + before_eth - treasury.balance()  < 1e12

    assert wbtc.balanceOf(treasury) == before_wbtc
    assert wbnb.balanceOf(treasury) > 0
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))
    mockuniv2.setRate(usdt.address, wbnb.address, (2000, 1))
    mockuniv2.setRate(wbnb.address, usdt.address, (1, 2000))
    logging.info('getCollateralLevelM10 with wbnb and big rates = {}'.format(markets.getCollateralLevelM10()))

def test_topup_sandbox2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, wbnb):
    logging.info('!!!!!!!!!!!!!!!!!   topup sandbox2 from treasury    !!!!!!!!!!!!!!!')

    #add rates for defi
    mockuniv2.setRate(dai.address, wbnb.address, (2000, 1))
    mockuniv2.setRate(wbnb.address, dai.address, (1, 2000))

    #topup manually treasury
    wbnb.transfer(treasury, 150*10**wbnb.decimals(), {"from": accounts[0]})

    #logging.info(markets.getCollateralLevelM10())
    assert treasury.isReadyForTopupSandBox2() == True


    #let's go to topup sandbox2
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))
    logging.info('treasury_wbnb_usdt = {}'.format(mockuniv2.getAmountsOut(wbnb.balanceOf(treasury), [wbnb.address,usdt.address])))
    logging.info('treasury_eth_usdt = {}'.format(mockuniv2.getAmountsOut(treasury.balance(), [weth.address,usdt.address])))
    logging.info('sandbox1_usdt_amount = {}'.format(usdt.balanceOf(sandbox1.address)))
    logging.info('ubd_amount = {}'.format(ubd.totalSupply()))


    assert dai.balanceOf(sandbox2.address) == 0
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_wbnb_treasury_amount = wbnb.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()

    tx = sandbox2.topupSandBox2( {'from':accounts[0]})

    #1/3 of amount
    wbnb_to_dai_amount = before_wbnb_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/100
    eth_to_dai_amount = before_eth_treasury_amount*treasury.SANDBOX2_TOPUP_PERCENT()/100

    logging.info('wbnb_to_dai_amount = {}'.format(wbnb_to_dai_amount))
    logging.info('eth_to_dai_amount = {}'.format(eth_to_dai_amount))
    logging.info('eth_balance_market = {}'.format(markets.balance()))

    dai_amount_calc = wbnb_to_dai_amount*mockuniv2.rates(wbnb.address, dai.address)[1]*10**dai.decimals()/10**wbnb.decimals() + eth_to_dai_amount*mockuniv2.rates(weth.address, dai.address)[1]*10**dai.decimals()/10**weth.decimals()
    logging.info('dai_amount_calc = {}'.format(dai_amount_calc))
    
    #logging.info(mockuniv2.getAmountsOut(eth_to_dai_amount, [weth.address,dai.address]))
    #logging.info(mockuniv2.getAmountsOut(wbtc_to_dai_amount, [wbtc.address,dai.address]))

    assert dai_amount_calc - dai.balanceOf(sandbox2) < 1e9  #mathematical error of Solidity and python 
    assert wbnb.balanceOf(treasury) == before_wbnb_treasury_amount - wbnb_to_dai_amount
    assert treasury.balance() == before_eth_treasury_amount - eth_to_dai_amount
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount

def test_topup_treasury_from_sandbox2(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, wbnb):
    
    logging.info('!!!!!!!!!!!!!!!!!   topup treasury from sandbox2    !!!!!!!!!!!!!!!')
    
    mockuniv2.setRate(dai.address, wbnb.address, (10, 1))
    mockuniv2.setRate(dai.address, weth.address, (200, 1))
    mockuniv2.setRate(weth.address, dai.address, (1, 200))
    mockuniv2.setRate(wbnb.address, dai.address, (1, 10))

    mockuniv2.setRate(usdt.address, wbnb.address, (10, 1))
    mockuniv2.setRate(usdt.address, weth.address, (200, 1))
    mockuniv2.setRate(wbnb.address, usdt.address, (1, 10))
    mockuniv2.setRate(weth.address, usdt.address, (1, 200))

    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))

    
    #topup treasury from sandbox2 - 1% of dai - to wbnb and eth 50x50
    before_wbnb_treasury_amount = wbnb.balanceOf(treasury.address)
    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_dai_sandbox2_amount = dai.balanceOf(sandbox2.address)

    # add call constant with percent!!!!
    logging.info('dai to exchange = {}'.format(before_dai_sandbox2_amount/100))
    logging.info('sandbox2 dai balance  = {}'.format(dai.balanceOf(sandbox2)))
    assert sandbox2.lastTreasuryTopUp() == 0
    tx = sandbox2.topupTreasury()
    assert tx.return_value == True
    assert sandbox2.lastTreasuryTopUp() > 0


    ##need call of constant from contract with topup percent - wait appearing it!! and 1% of slippage in defi
    wbnb_amount_calc = (before_dai_sandbox2_amount*10**wbnb.decimals()/mockuniv2.rates(dai, wbnb)[0]/10**dai.decimals()/2/100)
    eth_amount_calc = (before_dai_sandbox2_amount*10**weth.decimals()/mockuniv2.rates(dai, weth)[0]/10**dai.decimals()/2/100)

    assert dai.balanceOf(sandbox2) - before_dai_sandbox2_amount*99/100 <1e10
    assert before_wbnb_treasury_amount + wbnb_amount_calc - wbnb.balanceOf(treasury) < 1e5
    assert  before_eth_treasury_amount + eth_amount_calc - treasury.balance()  == 0 #< 1e4
    assert wbtc.balanceOf(treasury)  == before_wbtc_treasury_amount

def test_redeem_for_sandbox1(
        accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, wbnb):

    ubd.approve(sandbox1, 100000*10**ubd.decimals(), {"from": accounts[0]})
    logging.info('getCollateralLevelM10 = {}'.format(markets.getCollateralLevelM10()))

    before_wbtc_treasury_amount = wbtc.balanceOf(treasury.address)
    before_wbnb_treasury_amount = wbnb.balanceOf(treasury.address)
    before_eth_treasury_amount = treasury.balance()
    before_usdt_sandbox1_amount = usdt.balanceOf(sandbox1)
    wbnb_to_swap = before_wbnb_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/100
    eth_to_swap = before_eth_treasury_amount*treasury.SANDBOX1_REDEEM_PERCENT()/100
    
    #and 1% of defi slippage of usdt
    usdt_amount_calc = wbnb_to_swap*mockuniv2.rates(wbnb.address, usdt.address)[1]*10**usdt.decimals()/10**wbnb.decimals() + eth_to_swap*mockuniv2.rates(weth.address, usdt.address)[1]*10**usdt.decimals()/10**weth.decimals()

    #redeem only - topup sandbox1 from treasury
    tx = sandbox1.swapExactInput(ubd.address, 
                                100000*10**ubd.decimals(),
                                0,
                                100000*10**usdt.decimals())

    assert wbnb.balanceOf(treasury) - before_wbnb_treasury_amount*(100 - treasury.SANDBOX1_REDEEM_PERCENT()) /100 < 10
    assert before_eth_treasury_amount*(100 - treasury.SANDBOX1_REDEEM_PERCENT())/100 - treasury.balance()  < 1000
    assert before_usdt_sandbox1_amount + usdt_amount_calc - usdt.balanceOf(sandbox1) < 10
    assert wbtc.balanceOf(treasury) == before_wbtc_treasury_amount

def test_other_funscion(accounts, mockuniv2, dai, usdt, sandbox1, sandbox2, 
        treasury, ubd, markets, wbtc, market_adapter, weth, wbnb):
    with reverts("Only for MarketRegistry"):
        treasury.sendERC20ForSwap(wbnb,1)
    with reverts("Only for MarketRegistry"):
        treasury.sendEtherForRedeem(1)

    with reverts("Only for SandBoxes"):
        markets.swapExactInToBASEOut(1,1,wbtc, accounts[0],chain.time(), {"from": accounts[0]})

    with reverts("Only for SandBoxes"):
        markets.swapTreasuryAssetsPercentToSandboxAsset({"from": accounts[0]})

    with reverts("Only for SandBoxes"):
        markets.swapExactBASEInToTreasuryAssets(1, wbtc, {"from":accounts[0]})

    with reverts("Ownable: caller is not the owner"):
        markets.setSandbox1(sandbox1, {'from':accounts[1]})

    with reverts("Ownable: caller is not the owner"):
        markets.setSandbox2(sandbox2, {'from':accounts[1]})

    with reverts("Ownable: caller is not the owner"):
        markets.setTreasury(treasury, {'from':accounts[1]})

    with reverts("Ownable: caller is not the owner"):
        markets.setTeamAddress(accounts[8], {'from':accounts[1]})

    assert markets.isInitialized() == True

    assert markets.getUBDNetworkInfo()[0] == sandbox1
    assert markets.getUBDNetworkInfo()[1] == treasury
    assert markets.getUBDNetworkInfo()[2] == sandbox2
    assert markets.getUBDNetworkInfo()[3][0][0] == wbnb
    assert markets.getUBDNetworkInfo()[3][0][1] == 50'''