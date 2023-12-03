## UBD Network 

[Attractor subsystem](./attractor.md)
[Staking calculator](https://docs.google.com/spreadsheets/d/1ohNOF006gBw4JxIQcPatxtm-5PpoJYrqt9rGlRlWVxM/edit#gid=0)


### Tests
We use Brownie framework for developing and unit test. For run tests
first please [install it](https://eth-brownie.readthedocs.io/en/stable/install.html)

```bash
brownie test
```
Don't forget [ganache](https://www.npmjs.com/package/ganache)

### Tests in separate Ganache/Anvil (after london)
1. Install Ganache (chainid: 1337) https://github.com/trufflesuite/ganache#command-line-use or Anvil (chainid: 31337) ..  
2. Add  network in live networks as follow:
```yaml
  - name: Local New
   networks:
     - name: Local
       id: local
       host: http://127.0.0.1:8545
       chainid: 1337
```
3. Remove deployments info  
`rm -r build/deployments/1337/`  

4. **In separate** terminal run ganache
```bash
ganachee
```
4. Run test
```bash
brownie test ./tests/test_staking_05.py --network local

```


### Deployments Info
Deploy is very simple. You can find workflow in 
[fixtures](./tests/fixtures/deploy_env.py) 

#### 2023-04-17  Deploy in Testnet PreProd
----------Deployment artifacts-------------------  
**Locker&Distributor**  
https://goerli.etherscan.io/address/0x372301eCF4699B731783bAB8dbc4e485ccB57efe#code

**UBDN ERC20**  
https://goerli.etherscan.io/address/0xd0F967Fb429C13f14F1910776029D52aa98d2982#code

**test USDT**  
https://goerli.etherscan.io/address/0x985190ff075d46e29f863E906122F8faf35aC1Ac#code

#### 2023-06-27 Deployed in Ethereum Mainnet 
UBDN Token deployed at block 17570025 from addreess 
`0x71373aa15b6d537E70138A39709B50e32C3660Ec` (Keys can be obtain on demand)   
 
**Locker&Distributor**  
https://etherscan.io/address/0x6D8b29c195b9478D678cD9eA7aD870ECfb0A869F#code

**UBDN ERC20**  
https://etherscan.io/address/0xD624E5C89466A15812c1D45Ce1533be1F16C1702#code
Initial supply keeper address `0xE206f8AC6067d8253C57D86ac96A789Cd90ed4D4` is UBD project multisig contract


---
#### Gas Consumption Info
```bash
UBDNLockerDistributor <Contract>
   ├─ constructor                         -  avg: 1526199  avg (confirmed): 1526199  low: 1526199  high: 1526199
   ├─ buyTokensForExactStable             -  avg:  113110  avg (confirmed):  122152  low:   22952  high:  239710
   ├─ setPaymentTokenStatus               -  avg:   43666  avg (confirmed):   44606  low:   23027  high:   44611
   ├─ setDistributionToken                -  avg:   42051  avg (confirmed):   45560  low:   22815  high:   45560
   ├─ claimTokens                         -  avg:   35438  avg (confirmed):   39723  low:   22292  high:   51621
   ├─ setGuardianStatus                   -  avg:   33433  avg (confirmed):   43849  low:   23018  high:   43849
   ├─ buyTokensForExactStableWithSlippage -  avg:   32855  avg (confirmed):       0  low:   32855  high:   32855
   └─ emergencyPause                      -  avg:   25309  avg (confirmed):   25941  low:   22782  high:   31136
UBDNToken <Contract>
   ├─ constructor                         -  avg:  724273  avg (confirmed):  724273  low:  724273  high:  724285
   ├─ transfer                            -  avg:   41234  avg (confirmed):   50876  low:   21951  high:   50876
   ├─ approve                             -  avg:   38614  avg (confirmed):   44169  low:   21953  high:   44217
   ├─ mint                                -  avg:   36429  avg (confirmed):   50722  low:   22136  high:   50722
   ├─ increaseAllowance                   -  avg:   30242  avg (confirmed):   30242  low:   30242  high:   30242
   ├─ transferFrom                        -  avg:   26865  avg (confirmed):   26014  low:   22264  high:   31836
   └─ decreaseAllowance                   -  avg:   26701  avg (confirmed):   30226  low:   23176  high:   30226

```

