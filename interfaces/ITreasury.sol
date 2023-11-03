// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

//import "./IERC20Mint.sol";

interface ITreasury  {
    function approveForRedeem(address _marketAdapter) external returns (bool);
    function sendForRedeem(address _marketAdapter) external returns(uint256[] memory);
    function sendERC20ForSwap(address _marketAdapter, uint256 _percent) 
        external 
        returns(uint256[] memory);
    function sendOneERC20ForSwap(address _marketAdapter, address _erc20, uint256 _amount) external;     
    function sendEtherForRedeem(uint256 _percent) external returns(uint256);
    function SANDBOX1_REDEEM_PERCENT() external view returns(uint256);
    function SANDBOX2_TOPUP_PERCENT() external view returns(uint256);
    function isReadyForTopupSandBox2() external view returns(bool);
}