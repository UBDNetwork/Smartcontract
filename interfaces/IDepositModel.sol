// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;


struct Deposit {
        uint256 startDate;
        uint256 body;
        uint256[] amountParams;
        address[] addressParams;
        uint8 depositModelIndex;

    }

interface IDepositModel  {


    function checkOpen(address _user, Deposit memory _deposit) 
        external 
        view returns(bool ok, Deposit memory depositData);

    function accrueInterests(Deposit memory _deposit) external returns(Deposit memory, uint256 increment);
    function payInterestsToBody(Deposit memory _deposit) external returns(Deposit memory);
}