// SPDX-License-Identifier: MIT
// UBDNDistributor ERC20 Token Distributor
pragma solidity 0.8.21;


contract MockRateGuardian  {
    
    uint256 public EMERGENCY_PAYMENT_PAUSE = 10 minutes;

    mapping (address => uint256) public paymentTokens;

    event PaymentTokenPaused(address indexed Token, uint256 Until);



    /// @notice Temprory disable payments with token
    /// @param _paymentToken stable coin address
    function emergencyPause(address _paymentToken) external {
        paymentTokens[_paymentToken] = block.timestamp + EMERGENCY_PAYMENT_PAUSE;
        emit PaymentTokenPaused(_paymentToken, paymentTokens[_paymentToken]);
    }

    function setEMERGENCY_PAYMENT_PAUSE(uint256 period) external {
        EMERGENCY_PAYMENT_PAUSE = period;
    }

}