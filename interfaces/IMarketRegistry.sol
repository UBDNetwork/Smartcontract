// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

//import "./IERC20Mint.sol";


interface IMarketRegistry  {

    struct AsssetShare {
        address asset;
        uint8 percent;
    }

    struct UBDNetwork {
        address sandbox1;
        address treasury;
        address sandbox2;
        //address marketAdapter;
        //address oracleAdapter;
        AsssetShare[] treasuryERC20Assets;

    }

    function swapExactInToBASEOut(
        uint256 amountIn,
        uint256 amountOutMin,
        address assetIn,
        address to,
        uint deadline
    ) external returns (uint256 amountOut);


    function swapExactBASEInToETH(uint256 _amountIn) external;
    function swapExactBASEInToWBTC(uint256 _amountIn) external;
    function swapExactBASEInToTreasuryAssets(uint256 _amountIn, address _baseAsset) external;
    function redeemSandbox1() external payable returns(uint256);
    function swapTreasuryToDAI(uint256[] memory _stableAmounts) external;

    function getAmountOut(
        uint amountIn, 
        address[] memory path
    ) external view returns (uint256 amountOut);
    function getCollateralLevelM10() external view returns(uint256);
    function getBalanceInStableUnits(address _holder, address[] memory _assets) external view returns(uint256);
    function treasuryERC20Assets() external view returns(address[] memory assets);
    function getUBDNetworkTeamAddress() external view returns(address);
    function getUBDNetworkInfo() external view returns(UBDNetwork memory);
}