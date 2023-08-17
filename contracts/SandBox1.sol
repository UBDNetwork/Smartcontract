// SPDX-License-Identifier: MIT
// SandBox1 
pragma solidity 0.8.21;

import "./UBDExchange.sol";
import "../interfaces/IMarketRegistry.sol";


contract SandBox1 is UBDExchange {

    uint256 constant TREASURY_TOPUP_PERIOD = 1 days;
    uint256 constant TREASURY_TOPUP_PERCENT = 10000; // 1% - 10000, 13% - 130000, etc 
    address immutable public marketRegistry;

    uint256 public lastTreasuryTopUp;

    constructor(address _baseAsset, address _markets)
        UBDExchange(_baseAsset, address(this))
    {
        marketRegistry = _markets;

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
        if (_getCollateralSystemLevelM10() >= 30) {
            uint256 halfTopupAmount = 
                IERC20(EXCHANGE_BASE_ASSET).balanceOf(address(this)) / (100 * PERCENT_DENOMINATOR) / 2;
            IERC20(EXCHANGE_BASE_ASSET).approve(marketRegistry, halfTopupAmount *2);
            IMarketRegistry(marketRegistry).swapExactBASEInToETH(halfTopupAmount);
            IMarketRegistry(marketRegistry).swapExactBASEInToWBTC(halfTopupAmount);
        }
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
    // function setPaymentTokenStatus(address _token, bool _state, uint256 _feePercent) 
    //     external 
    //     onlyOwner 
    // {
    // }

    function _redeemSandbox1() internal returns(uint256 newBASEBalance) {
        if (_getCollateralSystemLevelM10() >= 10) {
            IMarketRegistry(marketRegistry).redeemSandbox1();
        }
        newBASEBalance = IERC20(EXCHANGE_BASE_ASSET).balanceOf(address(this));
    }

    function _getCollateralSystemLevelM10() internal view returns(uint256) {
        return  IMarketRegistry(marketRegistry).getCollateralLevelM10();
    }

}