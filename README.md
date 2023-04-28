## UBD Network Token & Sale


### Tests
We use Brownie framework for developing and unit test. For run tests
first please [install it](https://eth-brownie.readthedocs.io/en/stable/install.html)

```bash
brownie test
```
Don't forget [ganache](https://www.npmjs.com/package/ganache)

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

#### 2023-04-27 Deployed in Ethereum Mainnet 
UBDN Token deployed at block 17135062 from addreess 
`0x71373aa15b6d537E70138A39709B50e32C3660Ec` (Keys can be obtain on demand)   
 
**Locker&Distributor**  
https://etherscan.io/address/0x6e574932CDEe39866aEc86C560B5A0367BA5424F#code  

**UBDN ERC20**  
https://etherscan.io/address/0xdA7d1CA5019D4Ca46fA9E70035a0764C7547cf2c#code  
Initial supply keeper address `0xE206f8AC6067d8253C57D86ac96A789Cd90ed4D4` is UBD project multisig contract


---
#### Gas Consumption Info
```bash
UBDNLockerDistributor
   ├─ constructor             -  avg: 1460462  avg (confirmed): 1460462  low: 1460462  high: 1460462
   ├─ buyTokensForExactStable -  avg:  129927  avg (confirmed):  150626  low:   23869  high:  401396
   ├─ setPaymentTokenStatus   -  avg:   45326  avg (confirmed):   45326  low:   45319  high:   45331
   ├─ setDistributionToken    -  avg:   44633  avg (confirmed):   44633  low:   44633  high:   44633
   └─ claimTokens             -  avg:   35455  avg (confirmed):   39741  low:   22303  high:   51643
UBDNToken 
   ├─ constructor             -  avg:  735129  avg (confirmed):  735129  low:  735119  high:  735143
   ├─ transfer                -  avg:   41234  avg (confirmed):   50876  low:   21951  high:   50876
   ├─ approve                 -  avg:   38614  avg (confirmed):   44169  low:   21953  high:   44217
   ├─ mint                    -  avg:   37229  avg (confirmed):   51522  low:   22936  high:   51522
   ├─ increaseAllowance       -  avg:   30242  avg (confirmed):   30242  low:   30242  high:   30242
   ├─ transferFrom            -  avg:   26865  avg (confirmed):   26014  low:   22264  high:   31836
   └─ decreaseAllowance       -  avg:   26701  avg (confirmed):   30226  low:   23176  high:   30226


```

