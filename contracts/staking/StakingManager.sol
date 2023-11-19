// SPDX-License-Identifier: MIT
// StakingManager 
pragma solidity 0.8.21;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@uniswap/contracts/libraries/TransferHelper.sol";
//import "./TimeLock.sol";


contract StakingManager is  Ownable {

    struct DepositModel {
        uint256 validAfter;
        uint256 notValidAfter;
        address modelAddress;
    }

    struct Deposit {
        uint256 startDate;
        uint256 body;
        uint256 interestAmount;
        uint256 lastInterestPayDate;
        uint8 depositModelIndex;

    }

    address public immutable stakedToken;

    DepositModel[] public depositModels;
    mapping(address => Deposit) public deposits;
    event DepositModelChanged(address Model, uint256 ValidAfter, uint256 NotValidAfer);

    constructor(address _erc20) {
        require(_erc20 != address(0), "Cant be zero address");
        stakedToken = _erc20;
    }

    function deposit(uint256 _amount, uint256 _modelIndex) external {
        require(_modelIndex < depositModels.length, "Model with this index not exist yet");
        require(depositModels[_modelIndex].validAfter <= block.timestamp, "Model not valid yet");
        require(depositModels[_modelIndex].notValidAfter >= block.timestamp, "Model not valid already");
        Deposit storage d = deposits[msg.sender];
        if (d.startDate == 0) {
            // New deposit
            d.startDate = block.timestamp;
            d.body = _amount;
            d.depositModelIndex = uint8(_modelIndex);
        } else {
            // Add amount to deposit
            // TODO Check that add enable
            d.body += _amount;
        }
        TransferHelper.safeTransferFrom(stakedToken, msg.sender, address(this), _amount);
    }

    function claimInterest() public returns (uint256 claimedAmount) {
        // TODO mint reward
        TransferHelper.safeTransfer(stakedToken, msg.sender, claimedAmount);
    }

    function withdraw() public returns (uint256 withdrawAmount){
        // TODO mint reward
        TransferHelper.safeTransfer(stakedToken, msg.sender, withdrawAmount);
    }
    ///////////////////////////////////////////////////////////
    ///////    Admin Functions        /////////////////////////
    ///////////////////////////////////////////////////////////
    function modelRegister(DepositModel calldata _newModel) external onlyOwner {
        require(_newModel.modelAddress != address(0), "Cant be zero address");
        require(depositModels.length < type(uint8).max, "Too much models");
        depositModels.push(_newModel);
        emit DepositModelChanged(_newModel.modelAddress, _newModel.validAfter, _newModel.notValidAfter);
    }

    function editModelEndDate(uint256 _modelIndex, uint256 _notValidAfter) external onlyOwner {
        depositModels[_modelIndex].notValidAfter = _notValidAfter;
        emit DepositModelChanged(
            depositModels[_modelIndex].modelAddress, 
            depositModels[_modelIndex].validAfter, 
            _notValidAfter
        );  
    }
    ///////////////////////////////////////////////////////////

}