// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "./IERC20Mint.sol";

interface IERC20Burn is IERC20Metadata {
	function burn(uint256 _amount) external;
}