// SPDX-License-Identifier: MIT
// Treasury 
pragma solidity 0.8.21;

import "./MarketConnector.sol";
import "../interfaces/IERC20Burn.sol";

contract Treasury is MarketConnector {

	uint256 constant SANDBOX2_TOPUP_SHARE_DENOMINATOR = 3;
    uint256 constant SANDBOX2_TOPUP_MIN_AMOUNT = 1000; // Stable Coin Units (without decimals)

    constructor(address _markets)
        MarketConnector(_markets)
    {
        require(_markets != address(0), 'No zero markets');
    }
    event ReceivedEther(address, uint);
    
    receive() external payable {
        emit ReceivedEther(msg.sender, msg.value);
    }

    function topupSandBox2() external {
        if (_getCollateralSystemLevelM10() >= 30) {
            uint256 sandbox2TopupAmount = _getBalanceInStableUnits(
                address(this),  treasuryERC20Assets()
            ) / SANDBOX2_TOPUP_SHARE_DENOMINATOR;
            
            require(
                sandbox2TopupAmount >= SANDBOX2_TOPUP_MIN_AMOUNT, 
                'Too small topup amount'
            );
            IMarket(marketRegistry).swapTreasuryToDAI(sandbox2TopupAmount);
        }
    }

    /// Approve 1 percent
    function approveForRedeem() external {
        uint256 treasuryERC20AssetsCount = treasuryERC20Assets().length;
        address[] memory _treasuryERC20Assets = new address[](treasuryERC20AssetsCount);
        _treasuryERC20Assets = treasuryERC20Assets();
        for (uint8 i = 0; i < _treasuryERC20Assets.length; ++ i){
                IERC20(_treasuryERC20Assets[i]).approve(
                    marketRegistry, 
                    IERC20(_treasuryERC20Assets[i]).balanceOf(address(this))  / 100
                );
            }
    }

    function treasuryERC20Assets() public view returns(address[] memory assets) {
         return IMarket(marketRegistry).treasuryERC20Assets();
    }
}