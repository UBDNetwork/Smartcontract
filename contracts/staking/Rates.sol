// SPDX-License-Identifier: MIT
// Rates 
pragma solidity 0.8.21;



contract Rates {
   
    uint256 public constant PERCENT_DENOMINATOR = 10000; // 100%  - 1000000
    uint256[9][17]  public   rates; 
    uint256[9] public months = [1, 3, 6, 12, 24, 36, 60, 84, 120];
    uint256[17] public amounts = [
                    0,
                1_000,
               10_000,
               50_000,
              100_000,
              250_000,
              500_000,
            1_000_000,
            2_500_000,
            5_000_000,
           10_000_000,
           25_000_000,
           50_000_000,
          100_000_000,
          250_000_000,
          500_000_000,
        1_000_000_000
    ];
    constructor (){
        rates[0]  = [uint256(45000),   47500,  50000,   52500,   55000,   57500,   60000,   62500,   65000];
        rates[1]  = [47500,   50000,   52500,   55000,   57500,   60000,   62500,   65000,   67500];
        rates[2]  = [50000,   52500,   55000,   57500,   60000,   62500,   65000,   67500,   70000];
        rates[3]  = [52500,   55000,   57500,   60000,   62500,   65000,   67500,   70000,   72500];
        rates[4]  = [55000,   57500,   60000,   62500,   65000,   67500,   70000,   72500,   75000];
        rates[5]  = [57500,   60000,   62500,   65000,   67500,   70000,   72500,   75000,   77500];
        rates[6]  = [60000,   62500,   65000,   67500,   70000,   72500,   75000,   77500,   80000];
        rates[7]  = [62500,   65000,   67500,   70000,   72500,   75000,   77500,   80000,   82500];
        rates[8]  = [65000,   67500,   70000,   72500,   75000,   77500,   80000,   82500,   85000];
        rates[9]  = [67500,   70000,   72500,   75000,   77500,   80000,   82500,   85000,   87500];
        rates[10] = [70000,   72500,   75000,   77500,   80000,   82500,   85000,   87500,   90000];
        rates[11] = [72500,   75000,   77500,   80000,   82500,   85000,   87500,   90000,   92500];
        rates[12] = [75000,   77500,   80000,   82500,   85000,   87500,   90000,   92500,   95000];
        rates[13] = [77500,   80000,   82500,   85000,   87500,   90000,   92500,   95000,   97500];
        rates[14] = [80000,   82500,   85000,   87500,   90000,   92500,   95000,   97500,  100000];
        rates[15] = [82500,   85000,   87500,   90000,   92500,   95000,   97500,  100000,  102500];
        rates[16] = [85000,   87500,   90000,   92500,   95000,   97500,  100000,  102500,  105000];
    }

    function _getRateForPeriodAndAmount(uint256 _amount, uint256 _currMonth) 
        internal 
        view 
        returns(uint256 rate) 
    {
        // Case too short deposit period
        if (_currMonth < months[0]) {
            return 0;
        }
        uint256 monthIndex;
        for(uint256 i = 0; i < months.length; i ++){
            // Case of last month in table
            if (i == months.length-1){
               monthIndex = i;
            } else {
                if (_currMonth >= months[i] && _currMonth < months[i + 1])
                {
                   monthIndex = i;
                   break;
                }
            }

        }

        uint256 amountIndex;
        for(uint256 i = 0; i < amounts.length; i ++){
            // Case of last amount in table
            if (i == amounts.length - 1){
               amountIndex = i;
            } else {
                if (_amount >= amounts[i] && _amount < amounts[i + 1])
                {
                   amountIndex = i;
                   break;
                }
            } 
        }
        rate = rates[amountIndex][monthIndex];
    }

    function getRateRowCol(uint256 row, uint256 col) internal view returns(uint256){
        return rates[row][col];
    }

}