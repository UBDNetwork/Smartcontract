// SPDX-License-Identifier: MIT
// UBDNDistributor ERC20 Token Distributor
pragma solidity 0.8.18;


import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";


contract UBDNDistributor is Ownable {
    using SafeERC20 for IERC20;

    IERC20 public distributionToken;
    mapping (address => bool) public paymentTokens;

    function buyTokensForExactStable(address _paymentToken, uint256 _inAmount) 
        external 
        returns(uint256) 
    {
        require(address(distributionToken) != address(0), 'Distribution not Define');
        require(paymentTokens[_paymentToken], 'This payment token not supported');
        // 1. Receive payment
        // TODO think aboy require
        IERC20(_paymentToken).safeTransferFrom(msg.sender, owner(),_inAmount);
        // 2. Transfer distribution tokens
        distributionToken.safeTransfer(
            msg.sender, 
            _calcTokensForExactStable(_paymentToken,_inAmount)
        );


    }

    ///////////////////////////////////////////////////////////
    ///////    Admin Functions        /////////////////////////
    ///////////////////////////////////////////////////////////
    function setPaymentTokenStatus(address _token, bool _state) 
        external 
        onlyOwner 
    {
        paymentTokens[_token] = _state;
        // TODO Add evnent
    }

    function setDistributionToken(address _token) 
        external 
        onlyOwner 
    {
        distributionToken = IERC20(_token);
        // TODO Add evnent
    }

    ///////////////////////////////////////////////////////////

    function calcTokensForExactStable(uint256 _inAmount) 
        external 
        view 
        returns(uint256) 
    {

    }

    function calcStableForExactTokens(uint256 _inAmount) 
        external 
        view 
        returns(uint256) 
    {

    }

    function _calcTokensForExactStable(address _paymentToken, uint256 _inAmount) 
        internal 
        view 
        returns(uint256) 
    {
        return _inAmount;
    }
}