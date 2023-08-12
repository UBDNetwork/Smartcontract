// SPDX-License-Identifier: MIT
// UBDExchange 
pragma solidity 0.8.21;


import '@uniswap/contracts/libraries/TransferHelper.sol';
//import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IERC20Burn.sol";


contract UBDExchange is Ownable {
    //using SafeERC20 for IERC20Mint;
    
    struct PaymentTokenInfo {
        uint256 validAfter;
        uint256 feePercent;  
    }

    uint256 constant public FEE_EXCHANGE_MAX_PERCENT = 10000; // 1% - 10000, 13% - 130000, etc        
    uint256 constant public PERCENT_DENOMINATOR = 10000;
    uint256 constant public ADD_NEW_PAYMENT_TOKEN_TIMELOCK = 48 hours;
    uint256 constant public EMERGENCY_PAYMENT_PAUSE = 1 hours;

    address immutable public EXCHANGE_BASE_ASSET;
    address immutable public SANDBOX_1;


    uint256 public FEE_EXCHANGE;
    address public FEE_BENEFICIARY;


    IERC20Burn public ubdToken;
    // mapping from token address to timestamp of start validity
    mapping (address => PaymentTokenInfo) public paymentTokens;
    mapping (address => bool) public isGuardian;

   
    event PaymentTokenStatus(address indexed Token, bool Status);
    event PaymentTokenPaused(address indexed Token, uint256 Until);

    constructor (address _baseAsset, address _sandbox1) {
        require(_baseAsset != address(0) && _sandbox1 != address(0),'No zero address');
        // Add ETH USDT as default payment asset
        EXCHANGE_BASE_ASSET = _baseAsset;
        paymentTokens[_baseAsset] 
            = PaymentTokenInfo(block.timestamp, 50);
        SANDBOX_1 = _sandbox1;    
    }


    /// @notice SWap exact amount of input token for output
    /// @dev Don't forget approvement(s)
    /// @param _inAsset  UBD or BASE_TOKEN_ADDRESS,
    /// and  the last is the output token (UniswapV2 style)
    /// @param _inAmount amount of stable to spent
    /// @param _deadline Unix timestamp, Swap can't be executed after
    /// @param _amountOutMin minimum amount of output tokens that must be 
    /// received for the transaction not to revert
    function swapExactInput(
        //address[] memory _path, 
        address _inAsset,
        uint256 _inAmount, 
        uint256 _deadline, 
        uint256 _amountOutMin,
        address _receiver
    ) 
        public 
        returns (uint256 outAmount)
    {
        require(address(ubdToken) != address(0), 'UBD address not Define');

        address receiver = _receiver;
        
        if (receiver == address(0)) {
            receiver = msg.sender;
        }

        
        // Charge fee in inTokenAsset token from sender if enable(FEE_BENEFICIARY != address(0))
        uint256 feeAmount = _inAmount * paymentTokens[_inAsset].feePercent 
            / (100 * PERCENT_DENOMINATOR + paymentTokens[_inAsset].feePercent);

        if (FEE_BENEFICIARY != address(0)) {
            TransferHelper.safeTransferFrom(_inAsset, msg.sender, FEE_BENEFICIARY, feeAmount);
        }

        // Decrease in amount with charged fee(_inAmountPure)
        uint256 inAmountPure = _inAmount - feeAmount;
        

        if (_inAsset == address(ubdToken)) {
            // Back swap from UBD to Excange Base Asset
            // 4. Burn UBD for sender
            ubdToken.burn(msg.sender, inAmountPure);

            // 5. Return BASE ASSET  _inAmountPure to sender
            outAmount = inAmountPure * IERC20Metadata(EXCHANGE_BASE_ASSET).decimals() / ubdToken.decimals();
            TransferHelper.safeTransferFrom(EXCHANGE_BASE_ASSET, SANDBOX_1, msg.sender, outAmount);

        } else if (_inAsset == EXCHANGE_BASE_ASSET) {
            // Swap from BASE to UBD
            // 3. Take BAse Token _inAmountPure
            TransferHelper.safeTransferFrom(EXCHANGE_BASE_ASSET, msg.sender, SANDBOX_1,  inAmountPure);

            // 4. Mint  UBD _inAmountPure to sender
            outAmount = inAmountPure * ubdToken.decimals() / IERC20Metadata(EXCHANGE_BASE_ASSET).decimals();
            ubdToken.mint(msg.sender, outAmount); 
        }   
    }


    /// @notice Temprory disable payments with token
    /// @param _paymentToken stable coin address
    function emergencyPause(address _paymentToken) external {
        require(isGuardian[msg.sender], "Only for approved guardians");
        if (
                paymentTokens[_paymentToken].validAfter > 0 // token enabled 
                && paymentTokens[_paymentToken].validAfter <= block.timestamp // no timelock now
            ) 
        {
            paymentTokens[_paymentToken].validAfter = block.timestamp + EMERGENCY_PAYMENT_PAUSE;
            // TODO Check GAS with block.timestamp + EMERGENCY_PAYMENT_PAUSE below instead of get from mapping
            emit PaymentTokenPaused(_paymentToken, paymentTokens[_paymentToken].validAfter);
        }
    }

    ///////////////////////////////////////////////////////////
    ///////    Admin Functions        /////////////////////////
    ///////////////////////////////////////////////////////////
    function setPaymentTokenStatus(address _token, bool _state, uint256 _feePercent) 
        external 
        onlyOwner 
    {
        if (_state ) {
            require(_feePercent <= FEE_EXCHANGE_MAX_PERCENT, 'Fee is too much');
            paymentTokens[_token] = PaymentTokenInfo(
                block.timestamp + ADD_NEW_PAYMENT_TOKEN_TIMELOCK,
                _feePercent
            );    
        } else {
            paymentTokens[_token] = PaymentTokenInfo(0, 0);
        }
        
        emit PaymentTokenStatus(_token, _state);
    }

    function setUBDToken(address _token) 
        external 
        onlyOwner 
    {
        require(address(ubdToken) == address(0), "Can call only once");
        paymentTokens[_token] 
            = PaymentTokenInfo(block.timestamp, 50);
        ubdToken = IERC20Burn(_token);
    }

    function setGuardianStatus(address _guardian, bool _state)
        external
        onlyOwner
    {
        isGuardian[_guardian] = _state;
    }

    function setBeneficiary(address _addr)
        external
        onlyOwner
    {
        FEE_BENEFICIARY = _addr;
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



    /////////////////////////////////////////////////////////////////////

    function _calcStableForExactTokens(address _paymentToken, uint256 _outAmount) 
        internal
        virtual 
        view 
        returns(uint256 inAmount) 
    {
        inAmount = _outAmount + (_outAmount * FEE_EXCHANGE / PERCENT_DENOMINATOR);
    }

    function _calcTokensForExactStable(address _paymentToken, uint256 _inAmount) 
        internal
        virtual 
        view 
        returns(uint256 outAmount) 
    {
        // TODO !!!!! INCORRECT
        outAmount = _inAmount / (1 + FEE_EXCHANGE / PERCENT_DENOMINATOR);
    }

   function _getFeePercent(address _paymentToken)
       internal
       virtual
       view
       returns(uint256)
    {
        return 0; 
    }

    function _isValidForPayment(address _paymentToken) internal view returns(bool){
        if (paymentTokens[_paymentToken].validAfter == 0) {
            return false;
        }
        require(
            paymentTokens[_paymentToken].validAfter < block.timestamp,
            "Token paused or timelocked"
        );
        return true; 
    }
}