// SPDX-License-Identifier: MIT
// StakingManager 
pragma solidity 0.8.21;

import "../../interfaces/IDepositModel.sol";


contract DepositModelOne is IDepositModel{

    
    
    function checkOpen(address _user, Deposit memory _deposit) 
        external 
        view returns(bool ok, Deposit memory)
    {
         // This deposit index (TODO - move to constructor?)
         _deposit.depositModelIndex = 0;

        if (_deposit.startDate == 0) {
            // New deposit
            _deposit.startDate = block.timestamp;
        }
        require(
            _deposit.amountParams.length == 3, 
            "This Deposit require 3 amount params: Interests = 0, LastAccruedMonth = 0 and % for claim interests"
        );
        _deposit.amountParams[0] = 0;
        _deposit.amountParams[1] = 0;

        ok = true;
        return (ok, _deposit);

    }

    function accrueInterests(Deposit memory _deposit) 
        external 
        returns(Deposit memory, uint256 increment) {
       // Dummy acccrue!!!!!!
       increment = _deposit.amountParams[2];
       _deposit.amountParams[0] += increment;
       return (_deposit, increment);
    }

    function payInterestsToBody(Deposit memory _deposit) external returns(Deposit memory){
       _deposit.body += _deposit.amountParams[0];
       _deposit.amountParams[0] = 0;
       return _deposit;
    }
    
    ///////////////////////////////////////////////////////////
    ///////    Admin Functions        /////////////////////////
    ///////////////////////////////////////////////////////////
    
    ///////////////////////////////////////////////////////////

}