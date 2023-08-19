// SPDX-License-Identifier: MIT
// Treasury 
pragma solidity 0.8.21;

import "./MarketConnector.sol";
import "../interfaces/IERC20Burn.sol";

contract Treasury is MarketConnector {

	uint256 constant SANDBOX2_TOPUP_SHARE_DENOMINATOR = 3;
    uint256 constant SANDBOX2_TOPUP_MIN_AMOUNT = 1000; // Stable Coin Units (without decimals)
    address immutable public TEAM_WALLET;

    address[] public treasuryAssets;

    constructor(address _markets, address _teamWallet, address[] memory _assets)
        MarketConnector(_markets)
    {
        require(_markets != address(0), 'No zero markets');
        require(_teamWallet != address(0), 'No zero team address');
        TEAM_WALLET = _teamWallet;
        for (uint8 i = 0; i < _assets.length; ++ i){
            require(_assets[i] != address(0), 'No zero address assets');
            treasuryAssets.push(_assets[i]);
        }
        

    }

    function topupSandBox2() external {
        if (_getCollateralSystemLevelM10() >= 30) {
            uint256 sandbox2TopupAmount = _getBalanceInStableUnits(
                address(this),  treasuryAssets
            ) / SANDBOX2_TOPUP_SHARE_DENOMINATOR;
            
            require(
                sandbox2TopupAmount >= SANDBOX2_TOPUP_MIN_AMOUNT, 
                'Too small topup amount'
            );
            for (uint8 i = 0; i < treasuryAssets.length; ++ i){
                IERC20(treasuryAssets[i]).approve(
                    marketRegistry, 
                    IERC20(treasuryAssets[i]).balanceOf(address(this))  / SANDBOX2_TOPUP_SHARE_DENOMINATOR
                );
            }
            IMarket(marketRegistry).swapTreasuryToDAI(treasuryAssets, sandbox2TopupAmount);
        }
    }

    /// Approve 1 percent
    function approveForRedeem() external {
        for (uint8 i = 0; i < treasuryAssets.length; ++ i){
                IERC20(treasuryAssets[i]).approve(
                    marketRegistry, 
                    IERC20(treasuryAssets[i]).balanceOf(address(this))  / 100
                );
            }

    }
}