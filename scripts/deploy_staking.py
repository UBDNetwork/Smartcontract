from brownie import *
import json

if  web3.eth.chain_id in [4, 5, 97, 11155111]:
    # Testnets
    #private_key='???'
    accounts.load('ttwo');
    #accounts.load('secret2');

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

GOERLI_ERC20_TOKENS = [
    '0x168fF7e2F39b8048E32F52Ada62E41d61Fceda58', # USDT
    '0x59A40FAeb4D727279Ef6d72F52B3d4995f0DBf87', # USDC
    '0x50BddB7911CE4248822a60968A32CDF1D683e7AD', # DAI
    '0x2c10745ABA5FFe97bEEA7288b755342381D56980', # WBTC
    '0xFD5D5176c1E63aD1d10441Dc278F92a02F5e153b'  # WETH
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
        'enabled_erc20': GOERLI_ERC20_TOKENS,
        'market_adapter': '0xA8e732513A32eE299B87Da7Ef602cDA39cd7514f',
        'team_address': accounts[0],
        'wbtc_address': '0x2c10745ABA5FFe97bEEA7288b755342381D56980',
        'usdt_address': '0x168fF7e2F39b8048E32F52Ada62E41d61Fceda58',
        'dai_address': '0x50BddB7911CE4248822a60968A32CDF1D683e7AD',
        'timelock': 0,
        'ubd_address': '0x6771931a59500e0102aB9690f2E9473883010982'
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
        'timelock': 300,
        'ubd_address': '0x3E4673D787dD89C96075Bf6a2bE0DFaB75cC6Be8',
        'sandbox_1': '0x7Fe48EE4FBAE0aAf9540688951208D0D5609b860'
    },
    
}.get(web3.eth.chainId, {
    'explorer_base':'io',
    'premint_address': accounts[0], 
    'enabled_erc20': GOERLI_ERC20_TOKENS, 
    'timelock': 0,
    'market_adapter': '', 
    'team_address': accounts[0],
    'wbtc_address': '0xa2535BFbe7c0b0EB7B494D70cf7f47e037e19b02',
    'usdt_address': '0xE3cfED0fbCDB7AaE09816718f0f52F10140Fc61F',
    'dai_address': '0xE52E3383740e713631864Af328717966F5Fa4e22',
    'ubd_address': '0x3E4673D787dD89C96075Bf6a2bE0DFaB75cC6Be8',
    'sandbox_1': '0x7Fe48EE4FBAE0aAf9540688951208D0D5609b860'
})
print(CHAIN)
zero_address = '0x0000000000000000000000000000000000000000'

def main():
    #sandbox1 = SandBox1.at(CHAIN['sandbox_1'])
    #ubd = UBDToken.at(CHAIN['ubd_address'])
    staking = StakingManager.deploy(CHAIN['ubd_address'], CHAIN['sandbox_1'], tx_params)
    model_02 = DepositModel_02.deploy(18, tx_params) 
   
    # Print addresses for quick access from console
    print("\n**StakingManager**")  
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'], staking.address))
    print("\n**DepositModel_02**")  
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'], model_02.address))
    

    print("\n----------Deployment artifacts-------------------")
    print("```python")
    print("staking = StakingManager.at('{}')".format(staking.address))
    print("model_02 = DepositModel_02.at('{}')".format(model_02.address))
    print("```")
    

    if  web3.eth.chainId in [1,11155111,5]:
        StakingManager.publish_source(staking);
        DepositModel_02.publish_source(model_02);
        sandbox1 = SandBox1.at(CHAIN['sandbox_1'])
    
    sandbox1.setStakingContract(staking, True, tx_params)

   