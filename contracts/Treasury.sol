// SPDX-License-Identifier: MIT
// SandBox1 
pragma solidity 0.8.21;

contract Treasury {

     address immutable public marketRegistry;
	constructor(address _markets)
    {
        marketRegistry = _markets;

    }
}