// SPDX-License-Identifier: MIT
// MarketAdapterCustomMarket for like UniSwapV2 market 
pragma solidity 0.8.21;

//import "./UBDExchange.sol";
import '@uniswap/contracts/libraries/TransferHelper.sol';
import "@openzeppelin/contracts/access/Ownable.sol";
import "../../interfaces/IMarketAdapter.sol";
import "../../interfaces/IOracleAdapter.sol";
import '../../interfaces/IUniswapV2Router02.sol';

/// @dev Adapter for MockMarket based on Uniswap2
/// @dev All assets should be transfered to this contract balance 
/// @dev before call. Native asset should 
contract MarketAdapterCustomMarket is IMarketAdapter, IOracleAdapter {

    string public name;
    address immutable public ROUTERV2;
    address immutable public WETH;
    event ReceivedEther(address, uint);

    constructor(string memory _name, address _routerV2)
    {
        WETH = IUniswapV2Router02(_routerV2).WETH();
        require(WETH != address(0), 'Seems like bad router');
        name = _name;
        ROUTERV2 = _routerV2;

    }

    receive() external payable {
        emit ReceivedEther(msg.sender, msg.value);
    }

    function swapExactNativeInToERC20Out(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] memory path,
        address recipient,
        uint deadline
    ) external payable returns (uint256 amountOut){
        uint256[] memory amts = new uint256[](path.length); 
        amountOut = amts[amts.length-1];
        amts = IUniswapV2Router02(ROUTERV2).swapExactETHForTokens{value: amountIn}(
            amountOutMin,
            path,
            recipient,
            deadline   
        );
        amountOut = amts[amts.length-1];
    }


    function swapExactERC20InToERC20Out(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] memory path,
        address recipient,
        uint deadline
    ) external returns (uint256 amountOut){
        TransferHelper.safeApprove(path[0], ROUTERV2, amountIn);
        uint256[] memory amts = new uint256[](path.length); 
        amountOut = amts[amts.length-1];
        amts = IUniswapV2Router02(ROUTERV2).swapExactTokensForTokens(
            amountIn, 
            amountOutMin, 
            path, 
            recipient, 
            deadline
        );
        amountOut = amts[amts.length-1];
    }

    function swapExactERC20InToNativeOut(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] memory path,
        address recipient,
        uint deadline
    ) external returns (uint256 amountOut){
        TransferHelper.safeApprove(path[0], ROUTERV2, amountIn);
        uint256[] memory amts = new uint256[](path.length); 
        amountOut = amts[amts.length-1];
        amts = IUniswapV2Router02(ROUTERV2).swapExactTokensForETH(
            amountIn, 
            amountOutMin, 
            path, 
            recipient, 
            deadline
        );
        amountOut = amts[amts.length-1];
    }

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
    ) external payable returns (uint256 amountIn){}

    function swapERC20InToExactERC20Out(
        uint256 amountInMax,
        uint256 amountOut,
        address[] memory path,
        address recipient,
        uint deadline
    ) external returns (uint256 amountIn){}

    //////////////////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////
    ///                       Oracle Adpater Featrures                     ///
    //////////////////////////////////////////////////////////////////////////
    function getAmountOut(uint amountIn,  address[] memory path ) 
        external 
        view 
        returns (uint256 amountOut)
    {
        uint256[] memory amts = new uint256[](path.length); 
        amts = IUniswapV2Router02(ROUTERV2).getAmountsOut(amountIn, path);
        amountOut = amts[amts.length-1];
    }

    function getAmountIn(uint amountOut, address[] memory path)
        external
        view
        returns (uint256 amountIn)
    {}

    

}