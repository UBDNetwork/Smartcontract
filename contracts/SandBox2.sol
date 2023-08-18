// SPDX-License-Identifier: MIT
// Sandboxd2 
pragma solidity 0.8.21;

import "./MarketConnector.sol";

contract Sandboxd2 is MarketConnector {

	constructor(address _markets)
        MarketConnector(_markets)
    {

    }
}