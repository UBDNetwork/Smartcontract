// SPDX-License-Identifier: MIT
// SandBox1 
pragma solidity 0.8.21;

import "../interfaces/IMarket.sol";
import "@openzeppelin/contracts/access/Ownable.sol";


contract MarketRegistry is IMarket, Ownable{

    struct UBDNetwork {
        address sandbox1;
        address treasury;
        address sandbox2;
        address marketAdapter;
        address oracleAdapter;
        address UBDToken;
    }

    UBDNetwork public ubdNetwork;

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


    function swapExactBASEInToETH(uint256 _amountIn) external{}
    function swapExactBASEInToWBTC(uint256 _amountIn) external{}
    function redeemSandbox1() external returns(uint256){}
    function swapTreasuryToDAI(address[] memory _assets, uint256 _stableAmountUnits) external {}

    
    ///////////////////////////////////////////////////////////
    ///////    Admin Functions        /////////////////////////
    ///////////////////////////////////////////////////////////
    function setMarket(address _market) 
        external 
        onlyOwner 
    {
        ubdNetwork.marketAdapter = _market;
    }

    function setOracle(address _oracle) 
        external 
        onlyOwner 
    {
        ubdNetwork.oracleAdapter = _oracle;
    }


    ///////////////////////////////////////////////////////////////

    function getAmountsOut(
        uint amountIn, 
        address[] memory path
    ) external view returns (uint256 amountOut)
    {

    }
    function getCollateralLevelM10() external view returns(uint256){}
    function getBalanceInStableUnits(address _holder, address[] memory _assets) external view returns(uint256){}
}