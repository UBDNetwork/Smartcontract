// SPDX-License-Identifier: MIT
// Treasury 
pragma solidity 0.8.21;

import "./MarketConnector.sol";
import "../interfaces/IERC20Burn.sol";
import '@uniswap/contracts/libraries/TransferHelper.sol';

contract Treasury is MarketConnector {

	uint256 public constant SANDBOX2_TOPUP_PERCENT = 33;
    uint256 public constant SANDBOX1_REDEEM_PERCENT = 1;

    
    modifier onlyMarketRegistry()
    {
        require(msg.sender == marketRegistry, 'Only for SandBoxes');
        _;
    }

    event ReceivedEther(address, uint);
    
    constructor(address _markets)
        MarketConnector(_markets)
    {
        require(_markets != address(0), 'No zero markets');
    }

    receive() external payable {
        emit ReceivedEther(msg.sender, msg.value);
    }
    

    function sendERC20ForSwap(address _marketAdapter, uint256 _percent) 
        external
        onlyMarketRegistry 
        returns(uint256[] memory)
    {
        
        return _sendPercentOfTreasuryTokens(_marketAdapter, _percent);
    }

    function sendEtherForRedeem(uint256 _percent) 
        external 
        onlyMarketRegistry 
        returns (uint256 amount)
    {
        amount = address(this).balance * _percent / 100; 
        TransferHelper.safeTransferETH(marketRegistry, amount);
    }

   
    function getBalanceInStableUnits(address _holder, address[] memory _assets) 
        external 
        view 
        returns(uint256)
    {
        return _getBalanceInStableUnits(_holder, _assets);
    }

    function isReadyForTopupSandBox2() public view returns(bool) {
        if (_getCollateralSystemLevelM10() >= 30) {
            uint256 sandbox2TopupAmount = _getBalanceInStableUnits(
                address(this),  treasuryERC20Assets()
            ) * SANDBOX2_TOPUP_PERCENT / 100;
        }
    }

    function treasuryERC20Assets() public view returns(address[] memory assets) {
         return IMarketRegistry(marketRegistry).treasuryERC20Assets();
    }

    function _sendPercentOfTreasuryTokens(address _to, uint256 _percent) internal returns(uint256[] memory){
        uint256 treasuryERC20AssetsCount = treasuryERC20Assets().length;
        address[] memory _treasuryERC20Assets = new address[](treasuryERC20AssetsCount);
        uint256[] memory _treasuryERC20sended = new uint256[](treasuryERC20AssetsCount);
        _treasuryERC20Assets = treasuryERC20Assets();
        for (uint8 i = 0; i < _treasuryERC20Assets.length; ++ i){
            _treasuryERC20sended[i] = IERC20(_treasuryERC20Assets[i]).balanceOf(address(this)) * _percent / 100; 
            TransferHelper.safeTransfer(
                _treasuryERC20Assets[i],
                _to, 
                _treasuryERC20sended[i]
            );
        }
        return _treasuryERC20sended;

    }
}