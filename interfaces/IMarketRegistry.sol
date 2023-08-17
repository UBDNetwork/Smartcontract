// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

//import "./IERC20Mint.sol";

interface IMarketRegistry  {
    function swapExactInToBASEOut(
        uint256 amountIn,
        uint256 amountOutMin,
        address assetIn,
        address to,
        uint deadline
    ) external returns (uint256 amountOut);

    function getAmountsOut(
        uint amountIn, 
        address[] memory path
    ) external view returns (uint256 amountOut);

    function swapExactBASEInToETH(uint256 _amountIn) external;
    function swapExactBASEInToWBTC(uint256 _amountIn) external;
    function redeemSandbox1() external returns(uint256);

    function getCollateralLevelM10() external view returns(uint256);
}