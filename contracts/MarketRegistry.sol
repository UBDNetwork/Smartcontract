// SPDX-License-Identifier: MIT
// SandBox1 
pragma solidity 0.8.21;

import "../interfaces/IMarketRegistry.sol";


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
}