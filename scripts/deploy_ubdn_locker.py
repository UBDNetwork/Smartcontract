from brownie import *
import json

if  web3.eth.chain_id in [4, 5, 97, 11155111]:
    # Testnets
    #private_key='???'
    accounts.load('ttwo');
elif web3.eth.chain_id in [1,56,137, 11155111]:
    accounts.load('ubd_deployer')
    
print('Deployer:{}, balance: {}'.format(accounts[0],Wei(accounts[0].balance()).to('ether') ))
print('web3.eth.chain_id={}'.format(web3.eth.chainId))

tx_params = {'from':accounts[0]}
if web3.eth.chainId in  [1,4, 5, 137,11155111]:
    tx_params={'from':accounts[0], 'priority_fee': chain.priority_fee}

ETH_PAYMENT_TOKENS = [
'0x6b175474e89094c44da98b954eedeac495271d0f',  #DAI
'0xdAC17F958D2ee523a2206206994597C13D831ec7',  #USDT
'0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  #USDC
]

GOERLI_PAYMENT_TOKENS = [
'0x3a1A748d061fb00dD3D43c4130713A505be5D5d5',  #DAI
'0x985190ff075d46e29f863E906122F8faf35aC1Ac'  #test USDT
]


SEPOLIA_ERC20_TOKENS = [
    '0xE3cfED0fbCDB7AaE09816718f0f52F10140Fc61F', # USDT
    '0xBF8528699868B1a5279084C92B1d31D9C0160504', # USDC
    '0xE52E3383740e713631864Af328717966F5Fa4e22', # DAI
]

CHAIN = {   
    0:{'explorer_base':'io', 'premint_address': accounts[0], 'timelock': 700},
    1:{
        'explorer_base':'etherscan.io', 
        'enabled_erc20': ETH_PAYMENT_TOKENS, 
        'premint_address': '0xE206f8AC6067d8253C57D86ac96A789Cd90ed4D4',
        'timelock': 0
    },
    5:{
        'explorer_base':'goerli.etherscan.io', 
        'enabled_erc20': GOERLI_PAYMENT_TOKENS,
        'premint_address': accounts[0],
        'timelock': 700
    },
    56:{'explorer_base':'bscscan.com', },
    97:{'explorer_base':'testnet.bscscan.com', },
    137:{'explorer_base':'polygonscan.com', },
    80001:{'explorer_base':'mumbai.polygonscan.com', },  
    43114:{'explorer_base':'cchain.explorer.avax.network', },
    43113:{'explorer_base':'cchain.explorer.avax-test.network', },
    11155111:{
        'explorer_base':'sepolia.etherscan.io', 
        'enabled_erc20': SEPOLIA_ERC20_TOKENS,
        'premint_address': accounts[0],
        'timelock': 300,
    }

}.get(web3.eth.chainId, {
    'explorer_base':'io',
    'premint_address': accounts[0], 
    'enabled_erc20':GOERLI_PAYMENT_TOKENS, 
    'timelock': 0
})
print(CHAIN)
zero_address = '0x0000000000000000000000000000000000000000'

def main():
    locker = UBDNLockerDistributor.deploy(CHAIN['timelock'], tx_params)
    erc20 = UBDNToken.deploy(CHAIN['premint_address'], locker.address, 5_000_000e18, tx_params)
    # Print addresses for quick access from console
    
    print("\n**UBDNLockerDistributor**")
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],locker.address))
    print("\n**UBDNToken**")
    print('https://{}/address/{}#code'.format(CHAIN['explorer_base'],erc20.address))

    print("```python")
    print("locker = UBDNLockerDistributor.at('{}')".format(locker.address))
    print("erc20 = UBDNToken.at('{}')".format(erc20.address))
    print("```")
    
    locker.setDistributionToken(erc20,tx_params)
    for t in CHAIN['enabled_erc20']:
       locker.setPaymentTokenStatus(t, True, tx_params)
       
    if  web3.eth.chainId in [1,4, 5,56, 137, 43114,11155111,1313161554]:
        UBDNLockerDistributor.publish_source(locker);
        UBDNToken.publish_source(erc20);
    
    




### Encoding in python
#from eth_abi import encode_single
#from eth_account.messages import encode_defunct
#encoded_msg = encode_single('(string)',('ETH/USDT',))
#pair_hash = Web3.solidityKeccak(['bytes32'],[encoded])


