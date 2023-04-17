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


#### Ethereum Mainnet 
Deployed at block ... with addreess 
`...` (Keys can be obtain on demand)    
https://etherscan.io/address/  
Initial supply keeper is UBDNDistributor contract


---
#### Gas Consumption Info
```bash
UBDNLockerDistributor <Contract>
   ├─ constructor             -  avg: 1446589  avg (confirmed): 1446589  low: 1446589  high: 1446589
   ├─ buyTokensForExactStable -  avg:  131670  avg (confirmed):  147001  low:   23869  high:  401361
   ├─ setPaymentTokenStatus   -  avg:   45326  avg (confirmed):   45326  low:   45319  high:   45331
   ├─ setDistributionToken    -  avg:   44631  avg (confirmed):   44631  low:   44621  high:   44633
   └─ claimTokens             -  avg:   36973  avg (confirmed):   41220  low:   22303  high:   51643
UBDNToken <Contract>
   ├─ constructor             -  avg:  735131  avg (confirmed):  735131  low:  735131  high:  735143
   ├─ transfer                -  avg:   41234  avg (confirmed):   50876  low:   21951  high:   50876
   ├─ approve                 -  avg:   38614  avg (confirmed):   44169  low:   21953  high:   44217
   ├─ mint                    -  avg:   37229  avg (confirmed):   51522  low:   22936  high:   51522
   ├─ increaseAllowance       -  avg:   30242  avg (confirmed):   30242  low:   30242  high:   30242
   ├─ transferFrom            -  avg:   26865  avg (confirmed):   26014  low:   22264  high:   31836
   └─ decreaseAllowance       -  avg:   26701  avg (confirmed):   30226  low:   23176  high:   30226

```

