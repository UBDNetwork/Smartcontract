from brownie import *
import json

if  web3.eth.chain_id in [4, 5, 97, 11155111]:
    # Testnets
    #private_key='???'
    accounts.load('ttwo');
elif web3.eth.chain_id in [1,56,137]:
    accounts.load('ubd_deployer')
    
print('Deployer:{}, balance: {}'.format(accounts[0],Wei(accounts[0].balance()).to('ether') ))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))

tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4, 5, 137, 11155111]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

ETH_ERC20_TOKENS = [
'0x6b175474e89094c44da98b954eedeac495271d0f',  #DAI
'0xdAC17F958D2ee523a2206206994597C13D831ec7',  #USDT
'0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  #USDC
]



SEPOLIA_ERC20_TOKENS = [
    '0xE3cfED0fbCDB7AaE09816718f0f52F10140Fc61F', # USDT
    '0xBF8528699868B1a5279084C92B1d31D9C0160504', # USDC
    '0xE52E3383740e713631864Af328717966F5Fa4e22', # DAI
    '0xa2535BFbe7c0b0EB7B494D70cf7f47e037e19b02', # WBTC
    '0x947b627800c349854ea3665cc7C3A139662D3e49'  # WETH
]

CHAIN = {   
    0:{'explorer_base':'io', 'premint_address': accounts[0], 'timelock': 700},
    1:{
        'explorer_base':'etherscan.io', 
        'enabled_erc20': ETH_ERC20_TOKENS, 
        'premint_address': '0xE206f8AC6067d8253C57D86ac96A789Cd90ed4D4',
        'timelock': 0,
        'market_adapter': '',
        'team_address': accounts[0],
        'wbtc_address': ''
    },
    5:{
        'explorer_base':'goerli.etherscan.io', 
        'premint_address': accounts[0],
        'timelock': 700
    },
    56:{'explorer_base':'bscscan.com', },

    11155111:{
        'explorer_base':'sepolia.etherscan.io', 
        'enabled_erc20': SEPOLIA_ERC20_TOKENS,
        'market_adapter': '0x8aC7c971D0DA91034c75bA261ca67FF6c506F2fA',
        'team_address': accounts[0],
        'wbtc_address': '0xa2535BFbe7c0b0EB7B494D70cf7f47e037e19b02',
        'usdt_address': '0xE3cfED0fbCDB7AaE09816718f0f52F10140Fc61F',
        'dai_address': '0xE52E3383740e713631864Af328717966F5Fa4e22',
    },
    

}.get(web3.eth.chainId, {
    'explorer_base':'io',
    'premint_address': accounts[0], 
    'enabled_erc20':SEPOLIA_ERC20_TOKENS, 
    'timelock': 0,
    'market_adapter': '',
    'team_address': accounts[0],
    'wbtc_address': '0xa2535BFbe7c0b0EB7B494D70cf7f47e037e19b02',
    'usdt_address': '0xE3cfED0fbCDB7AaE09816718f0f52F10140Fc61F',
    'dai_address': '0xE52E3383740e713631864Af328717966F5Fa4e22',
})
print(CHAIN)
zero_address = '0x0000000000000000000000000000000000000000'

def main():
    markets = MarketRegistry.deploy(40, tx_params)
    sandbox1 = SandBox1.deploy(markets.address, CHAIN['usdt_address'], tx_params)
    sandbox2 = SandBox2.deploy(markets.address, CHAIN['dai_address'], tx_params)
    treasury = Treasury.deploy(markets.address, tx_params)
    ubd = UBDToken.deploy(sandbox1.address, tx_params)


    # Print addresses for quick access from console
    print("----------Deployment artifacts-------------------")
    print("markets = MarketRegistry.at('{}')".format(markets.address))
    print("sandbox1 = SandBox1.at('{}')".format(sandbox1.address))
    print("sandbox2 = SandBox2.at('{}')".format(sandbox2.address))
    print("treasury = Treasury.at('{}')".format(treasury.address))
    print("ubd = UBDToken.at('{}')".format(ubd.address))
    print("\n")
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'], markets.address))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'], sandbox1.address))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'], sandbox2.address))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'], treasury.address))
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'], ubd.address))

    if  web3.eth.chainId in [1,11155111]:
        MarketRegistry.publish_source(markets);
        SandBox1.publish_source(sandbox1);
        SandBox2.publish_source(sandbox2);
        Treasury.publish_source(treasury);
        UBDToken.publish_source(ubd);
    


    
    # Init
    markets.setSandbox1(sandbox1, tx_params)
    markets.setSandbox2(sandbox2, tx_params)
    markets.setTreasury(treasury, tx_params)    
    markets.setTeamAddress(CHAIN['team_address'], tx_params)
    sandbox1.setBeneficiary(CHAIN['team_address'], tx_params)
    markets.addERC20AssetToTreasury((CHAIN['wbtc_address'], 50), tx_params)
    sandbox1.setUBDToken(ubd, tx_params)

    if len(CHAIN['market_adapter']) > 0 :
        market_adapter = MarketAdapterCustomMarket.at(CHAIN['market_adapter'])
        
    ####   Ganach   Testnet CASE  only
    else:
        mockuniv2 = MockSwapRouter.deploy(accounts[2], accounts[2], tx_params)
        market_adapter = MarketAdapterCustomMarket.deploy('Mock UniSwapV2 adapter', mockuniv2, tx_params)

    markets.setMarketParams(ZERO_ADDRESS, (market_adapter, market_adapter, 0), tx_params)
    for a in CHAIN['enabled_erc20']:
        markets.setMarketParams(a, (market_adapter, market_adapter, 0), tx_params)


