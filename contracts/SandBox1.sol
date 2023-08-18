// SPDX-License-Identifier: MIT
// SandBox1 
pragma solidity 0.8.21;

import "./UBDExchange.sol";
import "./MarketConnector.sol";
//import "../interfaces/IMarketRegistry.sol";


contract SandBox1 is UBDExchange, MarketConnector {

    uint256 constant TREASURY_TOPUP_PERIOD = 1 days;
    uint256 constant TREASURY_TOPUP_PERCENT = 10000; // 1% - 10000, 13% - 130000, etc 

    uint256 public lastTreasuryTopUp;
    uint256 public MIN_TREASURY_TOPUP_AMOUNT = 100; // Stable Coin Units (without decimals)

    constructor(address _baseAsset, address _markets)
        UBDExchange(_baseAsset, address(this))
        MarketConnector(_markets)
    {

    }

    function swapExactInput(
        address _inAsset,
        uint256 _inAmount, 
        uint256 _deadline, 
        uint256 _amountOutMin
    ) 
        public
        returns (uint256 outAmount)
    {
        
        // Check system balance and redeem sandbox_1 if  need
        if (_inAsset == address(ubdToken) &&
            IERC20(EXCHANGE_BASE_ASSET).balanceOf(address(this)) < _amountOutMin){
            if (_redeemSandbox1() < _amountOutMin ) {
                return 0;
            }
        }

        if (_inAsset != EXCHANGE_BASE_ASSET && _inAsset != address(ubdToken)) {
            address[] memory path = new address[](2);

            uint256 amountBASE = IMarketRegistry(marketRegistry).swapExactInToBASEOut(
                _inAmount,
                _amountOutMin,
                _inAsset,
                msg.sender,
                _deadline
            );
            return super.swapExactInput(EXCHANGE_BASE_ASSET, amountBASE, _deadline, _amountOutMin, msg.sender);
        }
        return super.swapExactInput(_inAsset, _inAmount, _deadline, _amountOutMin, msg.sender);

    }

    
    function topupTreasury() public {
        uint256 halfTopupAmount = 
            IERC20(EXCHANGE_BASE_ASSET).balanceOf(address(this)) / (100 * PERCENT_DENOMINATOR) / 2;
        require(
            halfTopupAmount 
                >= MIN_TREASURY_TOPUP_AMOUNT * 10**IERC20Metadata(EXCHANGE_BASE_ASSET).decimals(), 
            'Too small topup amount'
        );
        require(
            lastTreasuryTopUp + TREASURY_TOPUP_PERIOD < block.timestamp, 
            'Please wait untit TREASURY_TOPUP_PERIOD'
        );
        lastTreasuryTopUp = block.timestamp;
        IERC20(EXCHANGE_BASE_ASSET).approve(marketRegistry, halfTopupAmount *2);
        IMarketRegistry(marketRegistry).swapExactBASEInToETH(halfTopupAmount);
        IMarketRegistry(marketRegistry).swapExactBASEInToWBTC(halfTopupAmount);
    }



    function getAmountsOut(
        uint amountIn, 
        address[] memory path
    ) external view returns (uint256 amountOut) 
    {
        return IMarketRegistry(marketRegistry).getAmountsOut(amountIn, path);
    }

     ///////////////////////////////////////////////////////////
    ///////    Admin Functions        /////////////////////////
    ///////////////////////////////////////////////////////////
    function setMinTopUp(uint256 _amount) 
        external 
        onlyOwner 
    {
        MIN_TREASURY_TOPUP_AMOUNT = _amount;
    }

    function _redeemSandbox1() internal returns(uint256 newBASEBalance) {
        if (_getCollateralSystemLevelM10() >= 10) {
            IMarketRegistry(marketRegistry).redeemSandbox1();
        }
        newBASEBalance = IERC20(EXCHANGE_BASE_ASSET).balanceOf(address(this));
    }

}