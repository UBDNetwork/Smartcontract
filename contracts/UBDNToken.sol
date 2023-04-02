// SPDX-License-Identifier: MIT

//   UBDN Token ERC20

//***************************************************************
// ERC20 part of this contract based on best community practice 
// of https://github.com/OpenZeppelin
// Adapted and amended by IBERGroup, email:maxsizmobile@iber.group; 
// Code released under the MIT License.
//****************************************************************

pragma solidity 0.8.18;

import "./ERC20.sol";

contract UBDNToken is ERC20 {

    uint256 constant public MAX_SUPPLY = 50_000_000e18;

    constructor(address initialKeeper)
        ERC20("UBD Network", "UBDN")
    { 
        _mint(initialKeeper, MAX_SUPPLY);
    }
    
}

