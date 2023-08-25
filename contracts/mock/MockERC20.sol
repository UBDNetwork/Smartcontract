// SPDX-License-Identifier: MIT

//   UBDN Token ERC20

//***************************************************************
// ERC20 part of this contract based on best community practice 
// of https://github.com/OpenZeppelin
// Adapted and amended by IBERGroup, email:maxsizmobile@iber.group; 
// Code released under the MIT License.
////**************************************************************

pragma solidity 0.8.21;

//import "../ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockToken is ERC20 {

    uint256 constant public MAX_SUPPLY = 5_000_000_000e18;
    uint8 decimals_;
    constructor(string memory _name, string memory _symbol, uint8 _decimals)
        ERC20(_name, _symbol)
    { 
        //Initial supply mint  - review before PROD
        _mint(msg.sender, MAX_SUPPLY);
        decimals_ = _decimals;
    }
    
    function decimals() public view virtual override returns (uint8) {
        return decimals_;
    }

    function mint(address _for, uint256 _amount) external {
        _mint(_for, _amount);
    }
}

