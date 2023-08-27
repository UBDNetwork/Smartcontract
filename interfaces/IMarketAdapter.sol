// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

//import "./IERC20Mint.sol";


interface IMarketAdapter  {

    // struct AsssetShare {
    //     address asset;
    //     uint8 percent;
    // }

    // struct UBDNetwork {
    //     address sandbox1;
    //     address treasury;
    //     address sandbox2;
    //     address marketAdapter;
    //     address oracleAdapter;
    //     AsssetShare[] treasuryERC20Assets;

    // }

    function swapExactERC20InToERC20Out(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] memory path,
        address recipient,
        uint deadline
    ) external returns (uint256 amountOut);

    function swapExactERC20InToNativeOut(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] memory path,
        address recipient,
        uint deadline
    ) external  returns (uint256 amountOut);

    function swapERC20InToExactNativeOut(
        uint256 amountInMax,
        uint256 amountOut,
        address[] memory path,
        address recipient,
        uint deadline
    ) external returns (uint256 amountIn);

    function swapNativeInToExactERC20Out(
        uint256 amountInMax,
        uint256 amountOut,
        address[] memory path,
        address recipient,
        uint deadline
    ) external returns (uint256 amountIn);


    function getAmountsOut(
        uint amountIn, 
        address[] memory path
    ) external view returns (uint256 amountOut);

    function WETH() external view returns(address);
}