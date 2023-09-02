// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

//import "./IERC20Mint.sol";

interface IOracle  {
    function getAmountOut(
        uint amountIn, 
        address[] memory path
    ) external view returns (uint256 amountOut);
    function getCollateralLevelM10() external view returns(uint256);
    function getBalanceInStableUnits(address _holder, address[] memory _assets) external view returns(uint256);
}