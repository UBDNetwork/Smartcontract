// SPDX-License-Identifier: MIT
// SandBox1 
pragma solidity 0.8.21;

import "../interfaces/IMarketRegistry.sol";
import "@openzeppelin/contracts/access/Ownable.sol";


contract MarketRegistry is IMarketRegistry {

    constructor()
    {

    }

    function swapExactInToBASEOut(
        uint256 amountIn,
        uint256 amountOutMin,
        address assetIn,
        address to,
        uint deadline
    ) external returns (uint256 amountOut) 

    {

    }

    function getAmountsOut(
        uint amountIn, 
        address[] memory path
    ) external view returns (uint256 amountOut)
    {

    }

    function swapExactBASEInToETH(uint256 _amountIn) external{}
    function swapExactBASEInToWBTC(uint256 _amountIn) external{}
    function redeemSandbox1() external returns(uint256){}
     function swapTreasuryToDAI(address[] memory _assets, uint256 _stableAmountUnits) external {}

    function getCollateralLevelM10() external view returns(uint256){}
    function getBalanceInStableUnits(address _holder, address[] memory _assets) external view returns(uint256){}
}