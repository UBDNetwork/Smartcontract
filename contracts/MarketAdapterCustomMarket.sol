// SPDX-License-Identifier: MIT
// SandBox1 
pragma solidity 0.8.21;

//import "./UBDExchange.sol";
import '@uniswap/contracts/libraries/TransferHelper.sol';
import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IMarketAdapter.sol";

/// @dev Adapter for MockMarket based on Uniswap2
/// @dev must be called from ???
contract MarketAdapterCustomMarket is IMarketAdapter {

	string public name;

	constructor(string memory _name)
	{
		name = _name;

	}

	function swapExactERC20InToERC20Out(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] memory path,
        address recipient,
        uint deadline
    ) external returns (uint256 amountOut){}

    function swapExactERC20InToNativeOut(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] memory path,
        address recipient,
        uint deadline
    ) external payable returns (uint256 amountOut){}

    function swapERC20InToExactNativeOut(
        uint256 amountInMax,
        uint256 amountOut,
        address[] memory path,
        address recipient,
        uint deadline
    ) external returns (uint256 amountIn){}

    function swapNativeInToExactERC20Out(
        uint256 amountInMax,
        uint256 amountOut,
        address[] memory path,
        address recipient,
        uint deadline
    ) external returns (uint256 amountIn){}


    function getAmountsOut(
        uint amountIn, 
        address[] memory path
    ) external view returns (uint256 amountOut){}

	

}