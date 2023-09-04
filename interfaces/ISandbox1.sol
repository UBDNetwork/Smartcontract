// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

//import "./IERC20Mint.sol";

interface ISandbox1  {
    function EXCHANGE_BASE_ASSET() external view returns (address);
    function TREASURY_TOPUP_PERCENT() external view returns (uint256);
    function ubdTokenAddress() external view returns (address);
}