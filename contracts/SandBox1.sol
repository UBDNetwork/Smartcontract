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
    uint256 public MIN_TREASURY_TOPUP_AMOUNT = 1000; // Stable Coin Units (without decimals)

    constructor(address _markets, address _baseAsset)
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

    
    function topupTreasury() external {
        uint256 topupAmount = 
            IERC20(EXCHANGE_BASE_ASSET).balanceOf(address(this)) 
            * TREASURY_TOPUP_PERCENT 
            / (100 * PERCENT_DENOMINATOR);
        require(
            topupAmount 
                >= MIN_TREASURY_TOPUP_AMOUNT * 10**IERC20Metadata(EXCHANGE_BASE_ASSET).decimals(), 
            'Too small topup amount'
        ); //TODO CHECK this
        require(
            lastTreasuryTopUp + TREASURY_TOPUP_PERIOD < block.timestamp, 
            'Please wait untit TREASURY_TOPUP_PERIOD'
        );
        lastTreasuryTopUp = block.timestamp;
        IERC20(EXCHANGE_BASE_ASSET).approve(marketRegistry, topupAmount);
        IMarketRegistry(marketRegistry).swapExactBASEInToTreasuryAssets(topupAmount, EXCHANGE_BASE_ASSET);
    }

    function topupTreasuryEmergency(address _token) external onlyOwner {
        require(_token != EXCHANGE_BASE_ASSET && _token != address(ubdToken), 'Only for other assets');
        uint256 topupAmount = IERC20(_token).balanceOf(address(this));
        IERC20(_token).approve(marketRegistry, topupAmount);
        IMarketRegistry(marketRegistry).swapExactBASEInToTreasuryAssets(topupAmount, EXCHANGE_BASE_ASSET);
    }


    // function getAmountOut(
    //     uint amountIn, 
    //     address[] memory path
    // ) external view returns (uint256 amountOut) 
    // {
    //     return IMarketRegistry(marketRegistry).getAmountOut(amountIn, path);
    // }

     ///////////////////////////////////////////////////////////
    ///////    Admin Functions        /////////////////////////
    ///////////////////////////////////////////////////////////
    function setMinTopUp(uint256 _amount) 
        external 
        onlyOwner 
    {
        MIN_TREASURY_TOPUP_AMOUNT = _amount;
    }
    ///////////////////////////////////////////////////////////

    function _redeemSandbox1() internal returns(uint256 newBASEBalance) {
        if (_getCollateralSystemLevelM10() >= 10) {
            IMarketRegistry(marketRegistry).redeemSandbox1();
        }
        newBASEBalance = IERC20(EXCHANGE_BASE_ASSET).balanceOf(address(this));
    }

}