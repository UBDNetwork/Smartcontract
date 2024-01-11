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
    event DepositNew(address indexed User , uint256 indexed DepositIndex, uint256 DepositValue);

    constructor(address _erc20, address _rewardMintAddress) {
        require(_erc20 != address(0), "Cant be zero address");
        stakedToken = _erc20;
        rewardMintAddress = _rewardMintAddress;
        
    }

    function deposit(Deposit memory _newDeposit) external {
        require(_newDeposit.depositModelIndex < depositModels.length, "Model with this index not exist yet");
        require(depositModels[_newDeposit.depositModelIndex].validAfter <= block.timestamp, "Model not valid yet");
        require(depositModels[_newDeposit.depositModelIndex].notValidAfter >= block.timestamp, "Model not valid already");
        // Pre Check
        bool isOK;
        (isOK, _newDeposit) = IDepositModel(depositModels[_newDeposit.depositModelIndex].modelAddress).checkOpen(
            msg.sender, 
            _newDeposit
        );

        // Save stake(depost) info
        if (isOK){
            Deposit storage d = deposits[msg.sender].push(); 
            _insertNewDepositInfo(d, _newDeposit);
            emit DepositNew(msg.sender,deposits[msg.sender].length - 1, d.body); 
            // Receive funds
            TransferHelper.safeTransferFrom(stakedToken, msg.sender, address(this), _newDeposit.body);
        }      
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
        // amountParams[0] - is always interest that accrued but not payed yet
        claimedAmount = d.amountParams[0];
        d.amountParams[0] = 0;
        if (claimedAmount > 0) {
            TransferHelper.safeTransfer(stakedToken, msg.sender, claimedAmount);    
        }
    }

    function withdraw(uint256 _depositIndex) external returns (uint256 withdrawAmount){
        Deposit storage d = deposits[msg.sender][_depositIndex];
        // accrue interests(with MINT!!!!) and pay all interest to body
        _accrueInterests(d);
        _payInterestToBody(d); 
        withdrawAmount = d.body;
        //d.body = 0;
        _removeDepositRecord(_depositIndex);
        TransferHelper.safeTransfer(stakedToken, msg.sender, withdrawAmount);
    }

    function withdrawEmergency(uint256 _depositIndex) external returns (uint256 withdrawAmount){
        Deposit storage d = deposits[msg.sender][_depositIndex];
        _payInterestToBody(d); 
        withdrawAmount = d.body;
        //d.body = 0;
        _removeDepositRecord(_depositIndex);
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
        return deposits[_user];
    }

    function getUserDeposits2(address _user) external view returns(Deposit[] memory) {
        Deposit[] memory uds = new Deposit[](deposits[_user].length);
        for (uint256 i = 0; i < uds.length; ++ i) {
            uds[i] = deposits[_user][i];     
        }
        return uds;
    }

    function getUserDepositsCount(address _user) external view returns(uint256) {
        return deposits[_user].length;
    }

    function getUserDepositByIndex(address _user, uint256 _index) 
        public 
        view 
        returns(Deposit memory) 
    {
        return deposits[_user][_index];
    }

    function getUserDepositByIndex2(address _user, uint256 _index) 
        public 
        view 
        returns(DepositInfo memory, uint256[] memory, address[] memory) 
    {
        Deposit memory d =  deposits[_user][_index];
        DepositInfo memory di;
        di.startDate = d.startDate;
        di.body = d.body;
        di.depositModelIndex = d.depositModelIndex;

        uint256[] memory amts = new uint256[](d.amountParams.length);
        address[] memory adrs = new address[](d.addressParams.length);
        for(uint256 i = 0; i < amts.length; ++ i){
            amts[i] = d.amountParams[i];
        }
        for(uint256 i = 0; i < adrs.length; ++ i){
            adrs[i] = d.addressParams[i];
        }
        return(di, amts, adrs);
    }


    function calcInterests(Deposit memory _deposit, uint256 _monthCount) 
        external 
        view
        returns(Deposit memory _newValues, uint256 increment)
    {
        (_newValues, increment) = IDepositModel(depositModels[_deposit.depositModelIndex].modelAddress)
            .calcInterests(_deposit, _monthCount);
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

    function _removeDepositRecord(uint256 _depositIndex) 
        internal 
    {
        Deposit[] storage userDeposits = deposits[msg.sender];
        if (_depositIndex != userDeposits.length -1) {
            userDeposits[_depositIndex] = userDeposits[userDeposits.length -1];
        }
        userDeposits.pop();
    }

}