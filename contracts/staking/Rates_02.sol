// SPDX-License-Identifier: MIT
// Rates 
pragma solidity 0.8.21;



abstract contract Rates_02 {
   
    uint256 public constant PERCENT_DENOMINATOR = 10000; // 100%  - 1000000
    uint256 public constant BASE_START = 45000;          // 4.5%
    uint256 public constant BASE_STEP = 2500;            // 0.25%
    uint256 public constant BASE_MAX = 105000;           // 10.5%
    uint256 public constant AMOUNT_BONUS = 2500;         // 0.25%
    uint256 public constant AMOUNT_STEP = 100_000;

    

    function _getRateForPeriodAndAmount(uint256 _amount, uint256 _currMonth) 
        internal 
        view 
        returns(uint256 rate) 
    {
        rate = BASE_START + BASE_STEP * (_currMonth / 4);
        rate += AMOUNT_BONUS * (_amount / AMOUNT_STEP);
        if (rate >= BASE_MAX) {
            rate = BASE_MAX;
        }
    }
}