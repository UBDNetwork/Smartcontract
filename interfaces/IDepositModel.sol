// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;


struct Deposit {
    uint256 startDate;
    uint256 body;
    uint256[] amountParams;
    address[] addressParams;
    uint8 depositModelIndex;
}

struct DepositInfo {
    uint256 startDate;
    uint256 body;
    uint8 depositModelIndex;
}

interface IDepositModel  {

    event InterestsAccrued(
        uint256 indexed MonthNumber, 
        uint256 Rate, 
        uint256 BodyForCalc,  
        uint256 Interests
    );
    function checkOpen(address _user, Deposit memory _deposit) 
        external 
        view returns(bool ok, Deposit memory depositData);

    function accrueInterests(Deposit memory _deposit) 
        external 
        returns(Deposit memory, uint256 increment);
        
    function payInterestsToBody(Deposit memory _deposit) 
        external 
        returns(Deposit memory);

    function getRateForPeriodAndAmount(uint256 _amount, uint256 _currMonth) 
        external 
        view 
        returns(uint256);

    function calcInterests(Deposit memory _deposit, uint256 _monthCount) 
        external 
        view
        returns(Deposit memory, uint256 increment);
}