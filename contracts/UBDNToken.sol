// SPDX-License-Identifier: MIT

//   UBDN Token ERC20

//***************************************************************
// ERC20 part of this contract based on best community practice 
// of https://github.com/OpenZeppelin
// Adapted and amended by IBERGroup, email:maxsizmobile@iber.group; 
// Code released under the MIT License.
//****************************************************************

pragma solidity 0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract UBDNToken is ERC20 {

    uint256 constant public INITIAL_SUPPLY = 5_000_000e18;
    address public minter; // sale contract

    constructor(address _initialKeeper, address _minter)
        ERC20("UBD Network", "UBDN")
    { 
        _mint(_initialKeeper, INITIAL_SUPPLY);
        minter = _minter;
    }

    function mint(address _to, uint256 _amount) external {
        require(msg.sender == minter, 'Only distibutor contarct');
         _mint(_to, _amount);
    }
    
}

