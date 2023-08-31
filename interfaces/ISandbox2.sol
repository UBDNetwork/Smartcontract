// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

//import "./IERC20Mint.sol";

interface ISandbox2 {
    function SANDBOX_2_BASE_ASSET() external view returns (address);
    function increaseApproveForTEAM(uint256 _incAmount) external;
}