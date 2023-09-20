// SPDX-License-Identifier: MIT
// Treasury 
pragma solidity 0.8.21;

import "./MarketConnector.sol";
import "../interfaces/IERC20Burn.sol";
import '@uniswap/contracts/libraries/TransferHelper.sol';

contract Treasury is MarketConnector {

	uint256 public constant SANDBOX2_TOPUP_PERCENT = 33;
    uint256 public constant SANDBOX2_TOPUP_MIN_AMOUNT = 1000; // Stable Coin Units (without decimals)
    uint256 public constant SANDBOX1_REDEEM_PERCENT = 1;

    constructor(address _markets)
        MarketConnector(_markets)
    {
        require(_markets != address(0), 'No zero markets');
    }
    event ReceivedEther(address, uint);
    
    receive() external payable {
        emit ReceivedEther(msg.sender, msg.value);
    }
    
    function isReadyForTopupSandBox2() public view returns(bool) {
        if (_getCollateralSystemLevelM10() >= 30) {
            uint256 sandbox2TopupAmount = _getBalanceInStableUnits(
                address(this),  treasuryERC20Assets()
            ) * SANDBOX2_TOPUP_PERCENT / 100;
            
            if (sandbox2TopupAmount >= SANDBOX2_TOPUP_MIN_AMOUNT) {
                return true;    
            }
        }
    }

    /// Approve 1 percent
    function approveForRedeem(address _marketAdapter) external {
        require(msg.sender == marketRegistry, 'Only for market regisrty');
        uint256 treasuryERC20AssetsCount = treasuryERC20Assets().length;
        address[] memory _treasuryERC20Assets = new address[](treasuryERC20AssetsCount);
        _treasuryERC20Assets = treasuryERC20Assets();
        for (uint8 i = 0; i < _treasuryERC20Assets.length; ++ i){
                // TODO thibk about more correct approve amount
                IERC20(_treasuryERC20Assets[i]).approve(
                    _marketAdapter, 
                    //IERC20(_treasuryERC20Assets[i]).balanceOf(address(this)) * SANDBOX1_REDEEM_PERCENT / 100 // 1 %
                    IERC20(_treasuryERC20Assets[i]).balanceOf(address(this)) * SANDBOX2_TOPUP_PERCENT / 100 // 33 %
                );
            }
    }

    // Depricated
    function sendForRedeem(address _marketAdapter) external returns(uint256[] memory){
        require(msg.sender == marketRegistry, 'Only for market regisrty');

        return _sendPercentOfTreasuryTokens(_marketAdapter, SANDBOX1_REDEEM_PERCENT);
    }

    // Depricated
    function sendForTopup(address _marketAdapter) external returns(uint256[] memory){
        require(msg.sender == marketRegistry, 'Only for market regisrty');
        
        return _sendPercentOfTreasuryTokens(_marketAdapter, SANDBOX2_TOPUP_PERCENT);
    }

    function sendERC20ForSwap(address _marketAdapter, uint256 _percent) 
        external 
        returns(uint256[] memory)
    {
        require(msg.sender == marketRegistry, 'Only for market regisrty');
        
        return _sendPercentOfTreasuryTokens(_marketAdapter, _percent);
    }

    function sendEtherForRedeem(uint256 _percent) external returns (uint256 amount){
        require(msg.sender == marketRegistry, 'Only for market regisrty');
        amount = address(this).balance * _percent / 100; 
        // TODO  check gas with TransferHelper
        address payable toPayable = payable(marketRegistry);
        toPayable.transfer(amount);
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