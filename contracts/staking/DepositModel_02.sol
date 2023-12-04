// SPDX-License-Identifier: MIT
// StakingManager 
pragma solidity 0.8.21;

import "../../interfaces/IDepositModel.sol";
import "./Rates_02.sol";

/// _deposit.amountParams[0]  - accrued and available for claim interests
/// _deposit.amountParams[1]  - Last Accrued Month 
/// _deposit.amountParams[2]  - percent of accrued that available for claim
contract DepositModel_02 is Rates_02, IDepositModel{

    uint256 public constant INTEREST_ACCRUE_PERIOD = 30 days;
    uint256 public immutable DECIMALS10;
    
    constructor(uint8 _decimals) {
        DECIMALS10 = 10**_decimals;
    }

    function checkOpen(address _user, Deposit memory _deposit) 
        external 
        view returns(bool ok, Deposit memory)
    {
         // This deposit index (TODO - move to constructor?)
         //_deposit.depositModelIndex = 1;

        if (_deposit.startDate == 0) {
            // New deposit
            _deposit.startDate = block.timestamp;
        }
        require(
            _deposit.amountParams.length == 3, 
            "This Deposit require 3 amount params: Interests = 0, LastAccruedMonth = 0 and % for claim interests"
        );
        require(_deposit.amountParams[2] <= 100 * PERCENT_DENOMINATOR, "Must be not more 100%");
        _deposit.amountParams[0] = 0;
        _deposit.amountParams[1] = 0;

        ok = true;
        return (ok, _deposit);

    }

    function accrueInterests(Deposit memory _deposit) 
        external 
        returns(Deposit memory, uint256 increment) {

        // 1. How many full months since start deposit
        uint256 fullM = (block.timestamp -  _deposit.startDate) / INTEREST_ACCRUE_PERIOD;
        // uint256 currRate = 100000;
        uint256 currRate;
        uint256 availableForClaim;
        uint256 oneMonthAccrued;
        for (uint256 i = _deposit.amountParams[1] + 1; i <= fullM; ++ i) {
            currRate = _getRateForPeriodAndAmount(_deposit.body / DECIMALS10, i);
            //oneMonthAccrued = _deposit.body * (currRate / 12) / (100 * PERCENT_DENOMINATOR) ;
            oneMonthAccrued = _deposit.body * currRate / (100 * PERCENT_DENOMINATOR) / 12 ;
            // In this deposit type only part of increment available for claim
            availableForClaim = oneMonthAccrued * _deposit.amountParams[2] / (100 * PERCENT_DENOMINATOR);
            if (availableForClaim > 0) {
                _deposit.amountParams[0] += availableForClaim;
            }
            // THIS IS DEBUG TIME EVENT ONLY! COMMENT BEFORE PRODUCTION
            emit InterestsAccrued(i, currRate, _deposit.body, oneMonthAccrued);
            _deposit.body += oneMonthAccrued - availableForClaim;
            increment += oneMonthAccrued;

        }
        _deposit.amountParams[1] = fullM;
        return (_deposit, increment);
    }

    function calcInterests(Deposit memory _deposit, uint256 _monthCount) 
        external 
        view
        returns(Deposit memory, uint256 increment) {

        uint256 currRate;
        uint256 availableForClaim;
        uint256 oneMonthAccrued;
        for (uint256 i = _deposit.amountParams[1] + 1; i <= _monthCount; i ++) {
            currRate = _getRateForPeriodAndAmount(_deposit.body / DECIMALS10, i);
            //oneMonthAccrued = _deposit.body * (currRate / 12) / (100 * PERCENT_DENOMINATOR) ;
            oneMonthAccrued = _deposit.body * currRate / (100 * PERCENT_DENOMINATOR) / 12 ;
            // In this deposit type only part of increment available for claim
            availableForClaim = oneMonthAccrued * _deposit.amountParams[2] / (100 * PERCENT_DENOMINATOR);
            if (availableForClaim > 0) {
                _deposit.amountParams[0] += availableForClaim;
            }
            _deposit.body += oneMonthAccrued - availableForClaim;
            increment += oneMonthAccrued;
        }
        _deposit.amountParams[1] = _monthCount;
        return (_deposit, increment);
    }

    function payInterestsToBody(Deposit memory _deposit) external returns(Deposit memory){
       _deposit.body += _deposit.amountParams[0];
       _deposit.amountParams[0] = 0;
       return _deposit;
    }
    
    function getRateForPeriodAndAmount(uint256 _amount, uint256 _currMonth) external view returns(uint256) {
        return _getRateForPeriodAndAmount(_amount, _currMonth);
    }
    ///////////////////////////////////////////////////////////
    ///////    Admin Functions        /////////////////////////
    ///////////////////////////////////////////////////////////
    
    ///////////////////////////////////////////////////////////

}