// SPDX-License-Identifier: MIT
// SandBox1 
pragma solidity 0.8.21;

import "../interfaces/IMarketRegistry.sol";
import "../interfaces/IMarketAdapter.sol";
import "../interfaces/IOracleAdapter.sol";
import "../interfaces/ISandbox1.sol";
import "../interfaces/ISandbox2.sol";
import "../interfaces/ITreasury.sol";
import '../interfaces/IERC20Mint.sol';
import "@openzeppelin/contracts/access/Ownable.sol";
import '@uniswap/contracts/libraries/TransferHelper.sol';


contract MarketRegistry is IMarketRegistry, Ownable{

    uint8 constant public TEAM_PERCENT = 3;
    uint8 constant public NATIVE_TOKEN_DECIMALS = 18;
    uint8 immutable public MIN_NATIVE_PERCENT;
    address public UBD_TEAM_ADDRESS;
    UBDNetwork public ubdNetwork;
    mapping(address => address) public marketAdapterForAsset;
    mapping(address => address) public oracleAdapterForAsset;
    event ReceivedEther(address, uint);

    constructor(uint8 _minNativePercent)
    {
        MIN_NATIVE_PERCENT = _minNativePercent;
    }

    receive() external payable {
        emit ReceivedEther(msg.sender, msg.value);
    }

    function swapExactInToBASEOut(
        uint256 amountIn,
        uint256 amountOutMin,
        address assetIn,
        address to,
        uint deadline
    ) external returns (uint256 amountOut) 

    {
        require(msg.sender == ubdNetwork.sandbox1, 'For SandBox1 only');
        address mrktAdapter = marketAdapterForAsset[assetIn];
        address orclAdapter = oracleAdapterForAsset[assetIn];
        address[] memory path = new address[](2);
        path[0] = assetIn;
        path[1] = ISandbox1(ubdNetwork.sandbox1).EXCHANGE_BASE_ASSET();

        TransferHelper.safeTransferFrom(
            assetIn, to, mrktAdapter, 
            amountIn // 
        );
        amountOut = IMarketAdapter(mrktAdapter).swapExactERC20InToERC20Out(
                amountIn,
                0, // TODO add value from oracle
                path,
                to,
                block.timestamp
            );
    }


    function swapExactBASEInToETH(uint256 _amountIn) external{}
    function swapExactBASEInToWBTC(uint256 _amountIn) external{}
    function redeemSandbox1() external payable returns(uint256){
        // Двумя главными условиями перехода средств из Cокровищницы в Песочницу 1,
        // является: обеспеченность 1:1 и выше, а также поступление запроса на 
        // вывод денег (aka пользователь возвращает UBD и хочет свои стейблы 
        // или выплаты от стейкинга), а денег в Песочнице 1 не хватает, чтобы 
        // покрыть сумму вывода. Только при этих двух условиях, а не какого-нибудь 
        // из них, происходит анлок средств в Сокровищнице для пополнения Песочницы 1!
        //В случае наступления двух данных условий, средства могут переходить 
        // из Сокровищницы в Песочницу 1 на закупку cтейбла на BTC и
        // ETH ровно на 1% от общей суммы, находящейся на данный момент в Сокровищнице.

        require(msg.sender == ubdNetwork.sandbox1, 'For SandBox1 only');
        // Get Treasury balance in sandbox1 base_asset
        // 1. Native asset
        // uint256 trsrNativeBalanceInBaseAsset;
        // uint256 trsrERC20BalanceInBaseAsset;
        address mrktAdapter = marketAdapterForAsset[address(0)];
        address orclAdapter = oracleAdapterForAsset[address(0)];
        address[] memory path = new address[](2);
        // path[1] = ISandbox1(ubdNetwork.sandbox1).EXCHANGE_BASE_ASSET();
        // path[0] = IMarketAdapter(mrktAdapter).WETH();
        // trsrNativeBalanceInBaseAsset = IOracleAdapter(orclAdapter).getAmountOut(
        //     ubdNetwork.treasury.balance,
        //     path
        // );

        // 2. ERC20 Asset
        // for (uint256 i; i < ubdNetwork.treasuryERC20Assets.length; ++ i){
        //     orclAdapter = oracleAdapterForAsset[ubdNetwork.treasuryERC20Assets[i].asset];
        //     path[0] = ubdNetwork.treasuryERC20Assets[i].asset; 
        //     trsrERC20BalanceInBaseAsset += IOracleAdapter(orclAdapter).getAmountOut(
        //         IERC20(ubdNetwork.treasuryERC20Assets[i].asset).balanceOf(ubdNetwork.treasury),
        //         path
        //     );
        // }
        // uint256 redeemSandbox1Amount = (trsrNativeBalanceInBaseAsset + trsrERC20BalanceInBaseAsset) / 100; //1%

        // Swap treasure asssets on market for Sandbox1 redeem
        // Swap some native asset
        path[1] = ISandbox1(ubdNetwork.sandbox1).EXCHANGE_BASE_ASSET();
        path[0] = IMarketAdapter(mrktAdapter).WETH();
        // First need withdraw ether to this contracr from treasury
        uint256 etherFromTreasuryAmount = ITreasury(ubdNetwork.treasury).sendEtherForRedeem(
            ITreasury(ubdNetwork.treasury).SANDBOX1_REDEEM_PERCENT()
        );
        //TODO check with amount from just msg.value 
        IMarketAdapter(mrktAdapter).swapExactNativeInToERC20Out{value: etherFromTreasuryAmount} (
            etherFromTreasuryAmount, 
            0, // TODO add value from oracle
            path,
            ubdNetwork.sandbox1,
            block.timestamp
        );
        
        // TODO    Approve treasure assets
        //ITreasury(ubdNetwork.treasury).approveForRedeem(mrktAdapter);
        uint256[] memory sended = new uint256[](ubdNetwork.treasuryERC20Assets.length);
        sended = ITreasury(ubdNetwork.treasury).sendForRedeem(mrktAdapter);

        // Swap erc20 treasure assets on market for Sandbox1 redeem
        for (uint256 i; i < sended.length; ++ i){
            // 2. Transfer all in assets from sandbox1 to adapter
        // TransferHelper.safeTransferFrom(
        //     _baseAsset, msg.sender, mrktAdapter, 
        //     _amountIn // all base asset - to adapter
        // );

            path[0] = ubdNetwork.treasuryERC20Assets[i].asset;
            IMarketAdapter(mrktAdapter).swapExactERC20InToERC20Out(
                sended[i],
                0, // TODO add value from oracle
                path,
                ubdNetwork.sandbox1,
                block.timestamp
            );

        }
    }

    // Если обеспечение UBD 3:1 и выше, то Сокровищница меняет  
    // 1/3 своих средств на DAI и переводит их в Песочницу 2.
    function topupSandBox2() external payable {
        require(ITreasury(ubdNetwork.treasury).isReadyForTopupSandBox2(), 'Too less for Sandbox2 TopUp');
        // Native asset
        // 1. Ether transfer to this contract
        uint256 etherFromTreasuryAmount = ITreasury(ubdNetwork.treasury).sendEtherForRedeem(
            ITreasury(ubdNetwork.treasury).SANDBOX2_TOPUP_PERCENT()
        );
        
        uint256 totalDAITopup;
        address[] memory path = new address[](2);
        path[1] = ISandbox2(ubdNetwork.sandbox2).SANDBOX_2_BASE_ASSET();
        address mrktAdapter = marketAdapterForAsset[path[1]];
        address orclAdapter = oracleAdapterForAsset[path[1]];
        path[0] = IMarketAdapter(mrktAdapter).WETH();
        //TODO check with amount from just msg.value 
        totalDAITopup = IMarketAdapter(mrktAdapter).swapExactNativeInToERC20Out{value: etherFromTreasuryAmount} (
            etherFromTreasuryAmount, 
            0, // TODO add value from oracle
            path,
            ubdNetwork.sandbox2,
            block.timestamp
        );

        // Swap ERC20 Treasury assets on DAI 
        ITreasury(ubdNetwork.treasury).approveForRedeem(mrktAdapter);
        uint256[] memory sended = new uint256[](ubdNetwork.treasuryERC20Assets.length);
        sended = ITreasury(ubdNetwork.treasury).sendForTopup(mrktAdapter);
        for (uint256 i; i < sended.length; ++ i){
            path[0] = ubdNetwork.treasuryERC20Assets[i].asset;
            totalDAITopup += IMarketAdapter(mrktAdapter).swapExactERC20InToERC20Out(
                sended[i],
                0, // TODO add value from oracle
                path,
                ubdNetwork.sandbox2,
                block.timestamp
            );

        }
        ISandbox2(ubdNetwork.sandbox2).increaseApproveForTEAM(totalDAITopup * TEAM_PERCENT / 100);
    }

    function swapTreasuryToDAI(uint256[] memory _stableAmounts) external {
        // address[] memory path = new address[](2);
        // path[1] = ISandbox2(ubdNetwork.sandbox2).SANDBOX_2_BASE_ASSET();
        // // Swap erc20 treasure assets on market for Sandbox2 topup
        // for (uint256 i; i < _stableAmounts.length; ++ i){
        //     path[0] = ubdNetwork.treasuryERC20Assets[i].asset;
        //     IMarketAdapter(mrktAdapter).swapExactERC20InToERC20Out(
        //         _stableAmounts[i],
        //         0, // TODO add value from oracle
        //         path,
        //         ubdNetwork.sandbox1,
        //         block.timestamp
        //     );
        // }

    }

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
            mrktAdapter = marketAdapterForAsset[ubdNetwork.treasuryERC20Assets[i].asset];
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

     function setTeamAddress(address _adr) 
        external 
        onlyOwner 
    {
        UBD_TEAM_ADDRESS = _adr;
    }
    ///////////////////////////////////////////////////////////////

    function getAmountOut(
        uint amountIn, 
        address[] memory path
    ) public view returns (uint256 amountOut)
    {
        address orclAdapter = oracleAdapterForAsset[path[path.length - 1]];
        return IOracleAdapter(orclAdapter).getAmountOut(amountIn, path);

    }
    // TODO check gas with replaced bdNetwork.treasuryERC20Assets[i].asset
    function getCollateralLevelM10() external view returns(uint256 level){
        //address mrktAdapter = marketAdapterForAsset[address(0)];
        
        // Sandbox 1
        address sandbox1BaseAsset = ISandbox1(ubdNetwork.sandbox1).EXCHANGE_BASE_ASSET();
        uint256 s1BalanceInBaseAsset = IERC20(sandbox1BaseAsset).balanceOf(
            ubdNetwork.sandbox1
        );

        // bring balance to common decimals (18 as native chain token)
        s1BalanceInBaseAsset = _bringAmountToNativeDecimals(
            sandbox1BaseAsset, s1BalanceInBaseAsset
        );

        uint256 ubdTotalSupply = IERC20Metadata(ISandbox1(ubdNetwork.sandbox1).ubdTokenAddress()).totalSupply();
        
        // bring supply to common decimals (18 as native chain token)
        ubdTotalSupply = _bringAmountToNativeDecimals(
            ISandbox1(ubdNetwork.sandbox1).ubdTokenAddress(), ubdTotalSupply
        );
        //uint8 ubdDecimals = IERC20Metadata(ISandbox1(ubdNetwork.sandbox1).ubdTokenAddress()).decimals();

        // uint256 tBalanceNative = ubdNetwork.treasury.balance;


        // uint256 erc20Balance;
        // uint256 erc20BalanceCommonDecimals;
        // address[] memory path = new address[](2);
        // for (uint256 i; i < ubdNetwork.treasuryERC20Assets.length; ++ i){
        //     //bring to a common denominator
        //     path[0] = ubdNetwork.treasuryERC20Assets[i].asset; // TODO replace with internal var for gas safe
        //     path[1] = sandbox1BaseAsset;
        //     erc20Balance = getAmountOut(
        //         IERC20(ubdNetwork.treasuryERC20Assets[i].asset).balanceOf(ubdNetwork.treasury), 
        //         path
        //     );
        //     erc20BalanceCommonDecimals += _bringAmountToNativeDecimals(
        //         sandbox1BaseAsset,
        //         //ubdNetwork.treasuryERC20Assets[i].asset, 
        //         erc20Balance
        //     );
        // }

        // path[0] = IMarketAdapter(mrktAdapter).WETH();
        // path[1] = sandbox1BaseAsset;
        
        // tBalanceNative = getAmountOut(tBalanceNative, path);
        // tBalanceNative = _bringAmountToNativeDecimals(
        //         sandbox1BaseAsset,
        //         tBalanceNative
        //     );


        //return (s1BalanceInBaseAsset + erc20BalanceCommonDecimals + tBalanceNative) * 10 / ubdTotalSupply;
        level =  (
            s1BalanceInBaseAsset + 
            getBalanceInStableUnits(ubdNetwork.treasury, treasuryERC20Assets()) *
            10**NATIVE_TOKEN_DECIMALS
        ) * 10 / ubdTotalSupply;

    }

    // 
    function getBalanceInStableUnits(address _holder, address[] memory _assets) 
        public 
        view 
        returns(uint256 stableUnitsNoDecimal)
    {
        address sandbox1BaseAsset = ISandbox1(ubdNetwork.sandbox1).EXCHANGE_BASE_ASSET();
        uint256 originalBalance;
        uint256 erc20BalanceCommonDecimals;
        address[] memory path = new address[](2);
        
        // First calc _holder erc20 balance in base assets but with native decimals for safe precision
        for (uint256 i; i < _assets.length; ++ i){
            //bring to a common denominator
            path[0] = _assets[i]; // TODO replace with internal var for gas safe
            path[1] = sandbox1BaseAsset;
            originalBalance = getAmountOut(
                IERC20(_assets[i]).balanceOf(_holder), 
                path
            );
            erc20BalanceCommonDecimals += _bringAmountToNativeDecimals(
                sandbox1BaseAsset,
                //ubdNetwork.treasuryERC20Assets[i].asset, 
                originalBalance
            );
        }

        
        // Calc _holder native balance
        address mrktAdapter = marketAdapterForAsset[address(0)];
        path[0] = IMarketAdapter(mrktAdapter).WETH();
        path[1] = sandbox1BaseAsset;
        
        
        uint256 tBalanceNative = _holder.balance;
        originalBalance = getAmountOut(tBalanceNative, path);
        tBalanceNative = _bringAmountToNativeDecimals(
                sandbox1BaseAsset,
                originalBalance
            );
        // Sum and devide for get balance in Stable coin units
        stableUnitsNoDecimal = (erc20BalanceCommonDecimals + tBalanceNative) / 10 ** NATIVE_TOKEN_DECIMALS;
    }
    
    function treasuryERC20Assets() public view returns(address[] memory assets) {
        // TODO Check Gas uint256
        assets = new address[](ubdNetwork.treasuryERC20Assets.length);
        for (uint8 i; i < ubdNetwork.treasuryERC20Assets.length; ++ i) {
            assets[i] = ubdNetwork.treasuryERC20Assets[i].asset;
        }
        
    }
    
    function getUBDNetworkTeamAddress() external view returns(address) {
        return UBD_TEAM_ADDRESS;
    }
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

    function _bringAmountToNativeDecimals(address _erc20, uint256 _amount) internal view returns(uint256 amount){
        uint8 decimals = IERC20Metadata(_erc20).decimals(); 
        if (decimals < NATIVE_TOKEN_DECIMALS) {
            amount = _amount * 10 ** (NATIVE_TOKEN_DECIMALS - decimals);
        } else if (decimals > NATIVE_TOKEN_DECIMALS) {
            amount = _amount / 10 ** (decimals - NATIVE_TOKEN_DECIMALS);
        } else {
            amount = _amount;
        }

    }

}