// SPDX-License-Identifier: MIT
// UBDNDistributor ERC20 Token Distributor
pragma solidity 0.8.19;


import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IERC20Mint.sol";


contract UBDNLockerDistributor is Ownable {
    using SafeERC20 for IERC20Mint;
    
    struct Lock {
        uint256 amount;
        uint256 lockedUntil;
    }

    uint256 constant public START_PRICE = 1;         // 1 stable coin unit, not decimal. 
    uint256 constant public PRICE_INCREASE_STEP = 1; // 1 stable coin unit, not decimal. 
    uint256 constant public INCREASE_FROM_ROUND = 1;
    uint256 constant public ROUND_VOLUME = 1_000_000e18; // in wei
    
    uint256 public LOCK_PERIOD = 90 days;
    uint256 public distributedAmount;

    IERC20Mint public distributionToken;
    mapping (address => bool) public paymentTokens;
    mapping (address => Lock[]) public userLocks;

    event DistributionTokenSet(address indexed Token);
    event PaymentTokenStatus(address indexed Token, bool Status);
    event Purchase(
        address indexed User,
        uint256 indexed PurchaseAmount, 
        address indexed PaymentToken, 
        uint256 PaymentAmount
    );
    event Claimed(address User, uint256 Amount, uint256 Timestamp);

    constructor (uint256 _lockPeriod) {
        if (_lockPeriod > 0) {
           LOCK_PERIOD = _lockPeriod;
        }
    }
    function buyTokensForExactStable(address _paymentToken, uint256 _inAmount) 
        external 
        returns(uint256) 
    {
        require(address(distributionToken) != address(0), 'Distribution not Define');
        require(paymentTokens[_paymentToken], 'This payment token not supported');
        // 1. Receive payment
        // TODO think about require
        // TODO think about real transfered anount for payments with fee
        IERC20Mint(_paymentToken).safeTransferFrom(msg.sender, owner(),_inAmount);
        // 2. Calc distribution tokens
        uint256 outAmount = _calcTokensForExactStable(_paymentToken,_inAmount);
        
        // 3. Save lockInfo
        _newLock(msg.sender, outAmount);
        distributedAmount += outAmount;
        // 4. Mint distribution token
        distributionToken.mint(address(this), outAmount);
        emit Purchase(msg.sender, outAmount, _paymentToken, _inAmount);
    }

    function claimTokens() external {
        uint256 claimAmount;
        // calc and mark as claimed
        for (uint256 i = 0; i < userLocks[msg.sender].length; ++i){
            if (block.timestamp >= userLocks[msg.sender][i].lockedUntil){
                claimAmount += userLocks[msg.sender][i].amount;
                userLocks[msg.sender][i].amount = 0;
            }
        }
        require(claimAmount > 0, 'Nothing to claim');
        distributionToken.safeTransfer(msg.sender, claimAmount);
        emit Claimed(msg.sender, claimAmount, block.timestamp);
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
        distributionToken = IERC20Mint(_token);
        emit DistributionTokenSet(_token);
    }

    ///////////////////////////////////////////////////////////

    /// @notice Returns amount of distributing tokens that will be
    /// get by user if he(she) pay given stable coin amount
    /// @dev _inAmount must be with given in wei (eg 1 USDT =1000000)
    /// @param _paymentToken stable coin address
    /// @param _inAmount stable coin amount that user want to spend
    function calcTokensForExactStable(address _paymentToken, uint256 _inAmount) 
        external 
        view 
        returns(uint256) 
    {
        return _calcTokensForExactStable(_paymentToken, _inAmount);
    }

    /// @notice Returns amount of stable coins that must be spent
    /// for user get given  amount of distributing token
    /// @dev _outAmount must be with given in wei (eg 1 UBDN =1e18)
    /// @param _paymentToken stable coin address
    /// @param _outAmount distributing token amount that user want to get
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

    function getUserLocks(address _user) 
        public 
        view 
        returns(Lock[] memory)
    {
        return userLocks[_user];
    }

    function getUserAvailableAmount(address _user)
        public
        view
        returns(uint256 total, uint256 availableNow)
    {
        for (uint256 i = 0; i < userLocks[_user].length; ++i){
            total += userLocks[_user][i].amount;
            if (block.timestamp >= userLocks[_user][i].lockedUntil){
                availableNow += userLocks[_user][i].amount;
            }
        }
    }

    function getCurrentRound() external view returns(uint256){
        return _currenRound();   
    }

    /////////////////////////////////////////////////////////////////////
    function _newLock(address _user, uint256 _lockAmount) internal {
        userLocks[_user].push(
            Lock(_lockAmount, block.timestamp + LOCK_PERIOD)
        );
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
                inAmount += curRest 
                    * curPrice * 10**IERC20Mint(_paymentToken).decimals()
                    / 10**distributionToken.decimals();
                outA -= curRest;
                ++ curR;
            } else {
                inAmount += outA 
                    * curPrice * 10**IERC20Mint(_paymentToken).decimals()
                    / 10**distributionToken.decimals();
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
            if (
                // calc out amount
                inA 
                / (curPrice * 10**IERC20Mint(_paymentToken).decimals())
                * (10**distributionToken.decimals())  > curRest
                ) 
            {
                // Case when inAmount more then price of all tokens 
                // in current round
                outAmount += curRest;
                inA -= curRest 
                       * curPrice * 10**IERC20Mint(_paymentToken).decimals()
                       / (10**distributionToken.decimals());
                ++ curR;
            } else {
                // Case when inAmount less or eqal then price of all tokens 
                // in current round
                outAmount += inA 
                  / (curPrice * 10**IERC20Mint(_paymentToken).decimals())
                  * 10**distributionToken.decimals();
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
            price = START_PRICE + PRICE_INCREASE_STEP * (_round - INCREASE_FROM_ROUND + 1); 
        }
        
        // in finished rounds rest always zero
        if (_round < _currenRound()){
            rest = 0;
        
        // in current round need calc 
        } else if (_round == _currenRound()){
            if (_round == 1){
                // first round
                rest = ROUND_VOLUME - distributedAmount; 
            } else {
                rest = ROUND_VOLUME - (distributedAmount % ROUND_VOLUME); 
            } 
        
        // in future rounds rest always ROUND_VOLUME
        } else {
            rest = ROUND_VOLUME;
        }
    }

    function _currenRound() internal view virtual returns(uint256){
        return distributedAmount / ROUND_VOLUME + 1;
    }
}