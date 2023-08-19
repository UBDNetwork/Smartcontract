// SPDX-License-Identifier: MIT
// MarketConnector 
pragma solidity 0.8.21;

import "../interfaces/IMarket.sol";

contract MarketConnector {

    address immutable public marketRegistry;
	constructor(address _markets)
    {
        marketRegistry = _markets;

    }

    function _getCollateralSystemLevelM10() internal view returns(uint256) {
        return  IMarket(marketRegistry).getCollateralLevelM10();
    }
    
    function _getBalanceInStableUnits(address _holder, address[] memory _assets) 
        internal 
        view 
        returns(uint256)
    {
        return IMarket(marketRegistry).getBalanceInStableUnits(_holder, _assets);
    }
}