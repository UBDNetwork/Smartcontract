// SPDX-License-Identifier: MIT
// StakingManager 
pragma solidity 0.8.21;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@uniswap/contracts/libraries/TransferHelper.sol";
import "../../interfaces/IDepositModel.sol";
import "../../interfaces/ISandbox1.sol";


contract StakingManager is  Ownable {

    struct DepositModel {
        uint256 validAfter;
        uint256 notValidAfter;
        address modelAddress;
    }


    address public immutable stakedToken;
    address public immutable rewardMintAddress;

    DepositModel[] public depositModels;


    mapping(address => Deposit[]) public deposits;
    event DepositModelChanged(address Model, uint256 ValidAfter, uint256 NotValidAfer);

    constructor(address _erc20, address _rewardMintAddress) {
        require(_erc20 != address(0), "Cant be zero address");
        stakedToken = _erc20;
        rewardMintAddress = _rewardMintAddress;
        
    }

    function deposit(uint8 _modelIndex, Deposit memory _newDeposit) external {
        require(_modelIndex < depositModels.length, "Model with this index not exist yet");
        require(depositModels[_modelIndex].validAfter <= block.timestamp, "Model not valid yet");
        require(depositModels[_modelIndex].notValidAfter >= block.timestamp, "Model not valid already");
        // Pre Check
        bool isOK;
        (isOK, _newDeposit) = IDepositModel(depositModels[_modelIndex].modelAddress).checkOpen(
            msg.sender, 
            _newDeposit
        );

        // Save stake(depost) info
        if (isOK){
            Deposit storage d = deposits[msg.sender].push(); 
            _insertNewDepositInfo(d, _newDeposit); 
        }       
 
        // Receive funds
        TransferHelper.safeTransferFrom(stakedToken, msg.sender, address(this), _newDeposit.body);
    }

    function addFundsToDeposit(uint256 _depositIndex, uint256 _addAmount) external {
        Deposit storage d = deposits[msg.sender][_depositIndex];
        _accrueInterests(d);
        d.body += _addAmount;
        // Receive funds
        TransferHelper.safeTransferFrom(stakedToken, msg.sender, address(this), _addAmount);
    }

    function claimInterests(uint256 _depositIndex) external returns (uint256 claimedAmount) {
        Deposit storage d = deposits[msg.sender][_depositIndex];
        _accrueInterests(d);
        // amountParams[0] - is always interest that accrued but not payed yey
        claimedAmount = d.amountParams[0];
        d.amountParams[0] = 0;
        //
        // TODO mint reward
        TransferHelper.safeTransfer(stakedToken, msg.sender, claimedAmount);
    }

    function withdraw(uint256 _depositIndex) external returns (uint256 withdrawAmount){
        Deposit storage d = deposits[msg.sender][_depositIndex];
        _accrueInterests(d);
        _payInterestToBody(d); 
        // accrue interests(with MINT!!!!) and pay all interest to body
        withdrawAmount = d.body;
        //IERC20Mint(stakedToken).mint()
        // TODO mint reward
        TransferHelper.safeTransfer(stakedToken, msg.sender, withdrawAmount);
    }
    function withdrawEmergency() external returns (uint256 withdrawAmount){
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
    function getUserDeposits(address _user) external view returns(Deposit[] memory) {
        return deposits[msg.sender];
    }

    function getUserDepositByIndex(address _user, uint256 _index) public view returns(Deposit memory) {
        return deposits[msg.sender][_index];
    }

    function _accrueInterests(Deposit storage _deposit) 
        internal 
        returns(Deposit memory _newValues, uint256 increment)
    {
        (_newValues, increment) = IDepositModel(depositModels[_deposit.depositModelIndex].modelAddress)
            .accrueInterests(_deposit);
        _updateDepositInfo(_deposit, _newValues); 
        ISandbox1(rewardMintAddress).mintReward(address(this), increment);   
    }

    function _payInterestToBody(Deposit storage _deposit) internal returns(Deposit memory _newValues){
        _newValues = IDepositModel(depositModels[_deposit.depositModelIndex].modelAddress)
            .payInterestsToBody(_deposit);
        _updateDepositInfo(_deposit, _newValues);

    }

    function _insertNewDepositInfo(Deposit storage _deposit, Deposit memory _newValues) 
        internal 
        returns(Deposit memory)
    {
        _deposit.body = _newValues.body;
        _deposit.startDate = _newValues.startDate;
        _deposit.depositModelIndex = _newValues.depositModelIndex;
        for (uint256 i = 0; i < _newValues.amountParams.length; ++ i){
            _deposit.amountParams.push(_newValues.amountParams[i]);
        }

        for (uint256 i = 0; i < _newValues.addressParams.length; ++ i){
            _deposit.addressParams.push(_newValues.addressParams[i]);
        } 
        
    }

    function _updateDepositInfo(Deposit storage _deposit, Deposit memory _newValues) 
        internal 
        returns(Deposit memory)
    {
        _deposit.body = _newValues.body;
        //_deposit.startDate = _newValues.startDate;
        //_deposit.depositModelIndex = _newValues.depositModelIndex
        for (uint256 i = 0; i < _newValues.amountParams.length; ++ i){
            _deposit.amountParams[i] =_newValues.amountParams[i];
        }

        for (uint256 i = 0; i < _newValues.addressParams.length; ++ i){
            _deposit.addressParams[i] = _newValues.addressParams[i];
        } 
        
    }

}