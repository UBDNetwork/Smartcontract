// SPDX-License-Identifier: MIT
// UBDNDistributor ERC20 Token Distributor
pragma solidity 0.8.21;


import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";

/// @title UBDNDistributor ERC20 Token Distributor
/// @author Envelop Team
/// @notice This implementation of distributor intend sell
/// all preminted erc20 tokens from this conatract balance. 
/// @dev  totallSupply must be preminted to this contract balance.
contract UBDNDistributor is Ownable {
    using SafeERC20 for IERC20;
    
    uint256 constant public START_PRICE = 1;         // 1 stable coin unit, not decimal. 
    uint256 constant public PRICE_INCREASE_STEP = 1; // 1 stable coin unit, not decimal. 
    uint256 constant public INCREASE_FROM_ROUND = 6;
    uint256 constant public ROUND_VOLUME = 1_000_000e18; // in wei

    IERC20 public distributionToken;
    mapping (address => bool) public paymentTokens;

    event DistributionTokenSet(address indexed Token);
    event PaymentTokenStatus(address indexed Token, bool Status);
    event Purchase(
        uint256 indexed PurchaseAmount, 
        address indexed PaymentToken, 
        uint256 indexed PaymentAmount
    );

    function buyTokensForExactStable(address _paymentToken, uint256 _inAmount) 
        external 
        returns(uint256) 
    {
        require(address(distributionToken) != address(0), 'Distribution not Define');
        require(paymentTokens[_paymentToken], 'This payment token not supported');
        // 1. Receive payment
        // TODO think about require
        // TODO think about real transfered anount for payments with fee
        IERC20(_paymentToken).safeTransferFrom(msg.sender, owner(),_inAmount);
        // 2. Transfer distribution tokens
        uint256 outAmount = _calcTokensForExactStable(_paymentToken,_inAmount);
        distributionToken.safeTransfer(
            msg.sender, 
            outAmount
        );
        emit Purchase(outAmount, _paymentToken, _inAmount);
    }

    ///////////////////////////////////////////////////////////
    ///////    Admin Functions        /////////////////////////
    ///////////////////////////////////////////////////////////
    function setPaymentTokenStatus(address _token, bool _state) 
        external 
        onlyOwner 
    {
        paymentTokens[_token] = _state;
        emit PaymentTokenStatus(_token, _state);
    }

    function setDistributionToken(address _token) 
        external 
        onlyOwner 
    {
        distributionToken = IERC20(_token);
        emit DistributionTokenSet(_token);
    }

    ///////////////////////////////////////////////////////////

    function calcTokensForExactStable(address _paymentToken, uint256 _inAmount) 
        external 
        view 
        returns(uint256) 
    {
        return _calcTokensForExactStable(_paymentToken, _inAmount);
    }

    function calcStableForExactTokens(address _paymentToken, uint256 _outAmount) 
        external 
        view 
        returns(uint256) 
    {
        return _calcStableForExactTokens(_paymentToken, _outAmount);
    }

    function priceInUnitsAndRemainByRound(uint256 _round) 
        external 
        view 
        returns(uint256, uint256) 
    {
        return _priceInUnitsAndRemainByRound(_round);
    }
    function _calcStableForExactTokens(address _paymentToken, uint256 _outAmount) 
        internal
        virtual 
        view 
        returns(uint256 inAmount) 
    {
        uint256 outA = _outAmount;
        uint256 curR = _currenRound();
        uint256 curPrice; 
        uint256 curRest;
        while (outA > 0) {
            (curPrice, curRest) = _priceInUnitsAndRemainByRound(curR); 
            if (outA > curRest) {
                inAmount += curRest * curPrice;
                outA -= curRest;
                ++ curR;
            } else {
                inAmount += outA / curPrice;
                return inAmount;
            }
        }
    }

    function _calcTokensForExactStable(address _paymentToken, uint256 _inAmount) 
        internal
        virtual 
        view 
        returns(uint256 outAmount) 
    {
        uint256 inA = _inAmount;
        uint256 curR = _currenRound();
        uint256 curPrice; 
        uint256 curRest;
        while (inA > 0) {
            (curPrice, curRest) = _priceInUnitsAndRemainByRound(curR); 
            if (inA / (curPrice * 10**IERC20Metadata(_paymentToken).decimals()) > curRest) {
                outAmount += curRest;
                inA -= curRest * curPrice;
                ++ curR;
            } else {
                outAmount += inA / curPrice;
                return outAmount;
            }
        }
    }

    function _priceInUnitsAndRemainByRound(uint256 _round) 
        internal 
        view 
        virtual 
        returns(uint256 price, uint256 rest) 
    {
        if (_round < INCREASE_FROM_ROUND){
            price = START_PRICE;
        } else {
            price = PRICE_INCREASE_STEP * (_round - INCREASE_FROM_ROUND + 2); 
        }
        rest = ROUND_VOLUME 
            - ((distributionToken.totalSupply() - distributionToken.balanceOf(address(this)))
             % ROUND_VOLUME); 
    }

    function _currenRound() internal view virtual returns(uint256){
        uint256 currentRoundNumber = 
            (distributionToken.totalSupply() - distributionToken.balanceOf(address(this)))
             / ROUND_VOLUME + 1;
        return currentRoundNumber;
    }
}