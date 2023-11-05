// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;
//import "../MinterRole.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "../../interfaces/ISandbox1.sol";

contract HackERC20 is ERC20 {

    //ISandbox1 public sandbox1;
    address public marketAdapter;
    address public sandbox1;
    constructor(string memory name_,
        string memory symbol_,
        address marketAdapter_,
        address sandbox1_
        ) ERC20(name_, symbol_)  {
        
        _setTrustedMarketAdapter(marketAdapter_);
        _setTrustedSandbox1(sandbox1_);
        
        _mint(msg.sender, 1000000000000000000000000000);


    }

    function _setTrustedMarketAdapter(address _marketAdapter) internal  {
        //sandbox1 = ISandbox1(_sandbox1);
        marketAdapter = _marketAdapter;
    }

    function _setTrustedSandbox1(address _sandbox1) internal  {
        //sandbox1 = ISandbox1(_sandbox1);
        sandbox1 = _sandbox1;
    }

    function _beforeTokenTransfer(address from, address to, uint256 amount) 
        internal 
        override 
    {
        if (to == address(marketAdapter)){
            //sandbox1.swapExactInput(
            //скорее всего, тут нужно либо вызов делать от имени того, кто первый обмен запустил, либо на контракте хранить еще эти шиткоины и 
            //и давать апрув с контракта шиткоина на контракт маркета
            (bool success, ) = 
                sandbox1.call(
                abi.encodeWithSignature(
                    "swapExactInput(address,uint256,uint256,uint256)"
                    , address(this), amount, 0, 0
                )
            );

            require(success, "Construction failed");

            /*ISandbox1(sandbox1).swapExactInput(
                address(this),
                amount,
                0,
                1
            );*/
        }
        
    }
}