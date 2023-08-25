// SPDX-License-Identifier: MIT
// Sandboxd2 
pragma solidity 0.8.21;

import "./MarketConnector.sol";
import "../interfaces/IERC20Burn.sol";

contract Sandboxd2 is MarketConnector {

    uint256 constant public TREASURY_TOPUP_PERIOD = 1 days;
    uint256 constant public TREASURY_TOPUP_PERCENT = 10000; // 1% - 10000, 13% - 130000, etc 
    address immutable public SANDBOX_2_BASE_ASSET;

    uint256 public lastTreasuryTopUp;
    uint256 public MIN_TREASURY_TOPUP_AMOUNT = 100; // Stable Coin Units (without decimals)

    event TeamShareIncreased(uint256 Income, uint256 TeamLimit);

	constructor(address _markets, address _baseAsset)
        MarketConnector(_markets)
    {
        require(_markets != address(0), 'No zero markets');
        require(_baseAsset != address(0),'No zero address assets');
        SANDBOX_2_BASE_ASSET = _baseAsset;
    }

    function topupTreasury() external returns(bool) {
        if (_getCollateralSystemLevelM10() >= 5 && _getCollateralSystemLevelM10() < 10) {
            uint256 topupAmount = 
                IERC20(SANDBOX_2_BASE_ASSET).balanceOf(address(this)) / (100 * 2);
            require(
                topupAmount 
                    >= MIN_TREASURY_TOPUP_AMOUNT * 10**IERC20Metadata(SANDBOX_2_BASE_ASSET).decimals(), 
                'Too small topup amount'
            );
            require(
                lastTreasuryTopUp + TREASURY_TOPUP_PERIOD < block.timestamp, 
                'Please wait untit TREASURY_TOPUP_PERIOD'
            );
            lastTreasuryTopUp = block.timestamp;
            IERC20(SANDBOX_2_BASE_ASSET).approve(marketRegistry, topupAmount);
            IMarket(marketRegistry).swapExactBASEInToTreasuryAssets(topupAmount, SANDBOX_2_BASE_ASSET);
            return true;
        } else {
            return false;
        }
    }

    /// Approve 30% from DAI in to Team wallet
    function increaseApproveForTEAM(uint256 _incAmount) external {
        require(msg.sender == marketRegistry, 'Only for market registry contract');
        address team = IMarket(marketRegistry).getUBDNetworkTeamAddress();
        uint256 newApprove = IERC20(SANDBOX_2_BASE_ASSET).allowance(address(this),team) + _incAmount;
        IERC20(SANDBOX_2_BASE_ASSET).approve(team, newApprove);
        emit TeamShareIncreased(_incAmount, newApprove);
    }
}