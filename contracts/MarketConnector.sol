// SPDX-License-Identifier: MIT
// MarketConnector 
pragma solidity 0.8.21;

import "../interfaces/IMarketRegistry.sol";

contract MarketConnector {

    address immutable public marketRegistry;
	constructor(address _markets)
    {
        marketRegistry = _markets;

    }

    function _getCollateralSystemLevelM10() internal view returns(uint256) {
        return  IMarketRegistry(marketRegistry).getCollateralLevelM10();
    }
    
    function _getBalanceInStableUnits(address _holder, address[] memory _assets) 
        internal 
        view 
        returns(uint256)
    {
        return IMarketRegistry(marketRegistry).getBalanceInStableUnits(_holder, _assets);
    }
}