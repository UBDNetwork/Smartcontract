// SPDX-License-Identifier: MIT
// SandBox1 
pragma solidity 0.8.21;

import "./UBDExchange.sol";


contract SandBox1 is UBDExchange {

	constructor(address _baseAsset)
        UBDExchange(_baseAsset, address(this))
	{

	}

	function swapExactInput(
        address _inAsset,
        uint256 _inAmount, 
        uint256 _deadline, //TODO
        uint256 _amountOutMin, 
        address _receiver
    ) 
        public
        override 
        returns (uint256 outAmount)
    {
    	if (_inAsset != EXCHANGE_BASE_ASSET && _inAsset != address(ubdToken)) {
    		// TODO  Excange to USDT on External Market( FOR _receiver)
    		// TODO Replace _inAsset, _inAmount bellow with appropriaTE VALUES
    		// 
    	}
    	super.swapExactInput(_inAsset, _inAmount, _deadline, _amountOutMin, _receiver);

    }

}