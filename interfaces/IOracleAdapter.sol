// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

//import "./IERC20Mint.sol";


interface IOracleAdapter  {

    
    function getAmountOut(
        uint amountIn, 
        address[] memory path
    ) external view returns (uint256 amountOut);

    function getAmountIn(uint amountOut, address[] memory path)
        external
        view
        returns (uint256 amountIn);

    //function WETH() external view returns(address);
}