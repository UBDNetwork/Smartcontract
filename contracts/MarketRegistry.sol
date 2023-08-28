// SPDX-License-Identifier: MIT
// SandBox1 
pragma solidity 0.8.21;

import "../interfaces/IMarket.sol";
import "../interfaces/IMarketAdapter.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import '@uniswap/contracts/libraries/TransferHelper.sol';


contract MarketRegistry is IMarket, Ownable{

    uint8 immutable public MIN_NATIVE_PERCENT;
    UBDNetwork public ubdNetwork;
    mapping(address => address) public marketAdapterForAsset;
    mapping(address => address) public oracleAdapterForAsset;


    constructor(uint8 _minNativePercent)
    {
        MIN_NATIVE_PERCENT = _minNativePercent;
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
    function swapTreasuryToDAI(uint256 _stableAmountUnits) external {}

    function swapExactBASEInToTreasuryAssets(uint256 _amountIn, address _baseAsset) external {
        // Prepare all parameters: percenet of native and erc20 assets for swap
        // Call adapter swap methods
        // 1. First define shares of Native asset
        address mrktAdapter = marketAdapterForAsset[address(0)];
        //uint256 amountInForNative = _amountIn * _getNativeTreasurePercent() / 100;
        // 2. Transfer all in assets from sandbox1 to adapter
        TransferHelper.safeTransferFrom(
            _baseAsset, msg.sender, mrktAdapter, 
            _amountIn // all base asset - to adapter
        );
        // 3. Call Swap
        address[] memory path = new address[](2);
        path[0] = _baseAsset;
        path[1] = IMarketAdapter(mrktAdapter).WETH(); // Native asset
        IMarketAdapter(mrktAdapter).swapExactERC20InToNativeOut(
            _amountIn * _getNativeTreasurePercent() / 100,
            0, // TODO add value from oracle
            path,
            ubdNetwork.treasury,
            block.timestamp
        );

        // 4. Call Swap for other Treasuru assets
        uint256 inSwap;
        for (uint256 i; i < ubdNetwork.treasuryERC20Assets.length; ++ i){
            inSwap = _amountIn * uint256(ubdNetwork.treasuryERC20Assets[i].percent) / 100;
            path[0] = _baseAsset;
            path[1] = ubdNetwork.treasuryERC20Assets[i].asset; // TODO replace with internal var for gas safe
            IMarketAdapter(mrktAdapter).swapExactERC20InToERC20Out(
                inSwap,
                0, // TODO add value from oracle
                path,
                ubdNetwork.treasury,
                block.timestamp
            );
        }


    }

    
    ///////////////////////////////////////////////////////////
    ///////    Admin Functions        /////////////////////////
    ///////////////////////////////////////////////////////////
    function setMarket(address _asset, address _market) 
        external 
        onlyOwner 
    {
        require(_market != address(0), 'No zero address');
        marketAdapterForAsset[_asset] = _market; 
        //ubdNetwork.marketAdapter = _market;
    }

    function setOracle(address _asset, address _oracle) 
        external 
        onlyOwner 
    {
        //ubdNetwork.oracleAdapter = _oracle;
        require(_oracle != address(0), 'No zero address');
        oracleAdapterForAsset[_asset] = _oracle;
    }

    function setSandbox1(address _adr) 
        external 
        onlyOwner 
    {
        ubdNetwork.sandbox1 = _adr;
    }
    function setSandbox2(address _adr) 
        external 
        onlyOwner 
    {
        ubdNetwork.sandbox2 = _adr;
    }

    function setTreasury(address _adr) 
        external 
        onlyOwner 
    {
        ubdNetwork.treasury = _adr;
    }

    function addERC20AssetToTreasury(AsssetShare memory _assetShare) 
        external 
        onlyOwner 
    {
        for (uint256 i; i < ubdNetwork.treasuryERC20Assets.length; ++ i){
            require(ubdNetwork.treasuryERC20Assets[i].asset != _assetShare.asset, 'Asset already exist');
        }
        ubdNetwork.treasuryERC20Assets.push(_assetShare);
        
        //check sum percent
        uint8 sumPercent;
        for (uint256 i; i < ubdNetwork.treasuryERC20Assets.length; ++ i){
            sumPercent += ubdNetwork.treasuryERC20Assets[i].percent;
        }
        require(sumPercent + MIN_NATIVE_PERCENT < 100, 'Sum percent to much');
    }

    function removeERC20AssetFromTreasury(address _erc20) 
        external 
        onlyOwner 
    {
        uint256 assetsCount = ubdNetwork.treasuryERC20Assets.length;
        for (uint256 i; i < assetsCount; ++ i){
            if (ubdNetwork.treasuryERC20Assets[i].asset == _erc20){
                // if not last then replace last  to this position
                if (i != assetsCount - 1){
                    ubdNetwork.treasuryERC20Assets[i] = ubdNetwork.treasuryERC20Assets[assetsCount-1];
                }
                ubdNetwork.treasuryERC20Assets.pop();

            } 
        }
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
    function treasuryERC20Assets() external view returns(address[] memory assets) {}
    function getUBDNetworkTeamAddress() external view returns(address) {}
    function getUBDNetworkInfo() external view returns(UBDNetwork memory) {
        return ubdNetwork;
    }
    
    function isInitialized() public view returns(bool){
        UBDNetwork memory _ubdnetwork = ubdNetwork;
        if (_ubdnetwork.sandbox1 != address(0) &&
            _ubdnetwork.sandbox2 != address(0) &&
            _ubdnetwork.treasury != address(0) &&
            //_ubdnetwork.marketAdapter != address(0) &&
            //_ubdnetwork.oracleAdapter != address(0) &&
            _ubdnetwork.treasuryERC20Assets.length > 0 
        ) {
            return true; 
        }
    }

    function _getNativeTreasurePercent() internal view returns(uint256) {
        uint8 sumPercent;
        for (uint256 i; i < ubdNetwork.treasuryERC20Assets.length; ++ i){
            sumPercent += ubdNetwork.treasuryERC20Assets[i].percent;
        }
        return uint256(100 - sumPercent);

    }

}