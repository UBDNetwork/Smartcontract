// SPDX-License-Identifier: MIT
//  UBD ERC20 


pragma solidity 0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract UBDToken is ERC20 {

    address immutable public minter; // sale contract

    constructor(address _minter)
        ERC20("United Blockchain Dollar", "UBD")
    { 
        minter = _minter;

    }

    function mint(address _to, uint256 _amount) external {
        require(msg.sender == minter, 'Only exchange contract');
         _mint(_to, _amount);
    }

    /**
     * @dev Burns `_amount` tokens from the caller's account.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     */
    function burn(uint256 _amount) external returns (bool) {
        require(msg.sender == minter, 'Only exchange contract');
        _burn(msg.sender, _amount);
        return true;
    }
    
}

