## Green Grey MetaGame Token


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


#### Ethereum Mainnet 
Deployed at block 16889176 with addreess 
`0xA5FeD2453da128747d06E937c9493F77941B7B6E` (Keys can be obtain on demand)    
https://etherscan.io/address/0x76aAb5FD2243d99EAc92d4d9EBF23525d3ACe4Ec  
Initial supply keeper is `0x607479d4b8dD98e78b0b80020c6684fd3b83D048`


---
#### Gas Consumption Info
```bash
GGMTToken <Contract>
   ├─ constructor       -  avg: 703600  avg (confirmed): 703600  low: 703600  high: 703600
   ├─ approve           -  avg:  38549  avg (confirmed):  44097  low:  21908  high:  44101
   ├─ transfer          -  avg:  37818  avg (confirmed):  43108  low:  21951  high:  50888
   ├─ increaseAllowance -  avg:  30243  avg (confirmed):  30243  low:  30243  high:  30243
   ├─ transferFrom      -  avg:  26864  avg (confirmed):  26026  low:  22276  high:  31787
   ├─ decreaseAllowance -  avg:  26696  avg (confirmed):  30227  low:  23165  high:  30227
   └─ burn              -  avg:  22686  avg (confirmed):      0  low:  22686  high:  22686
```

