// SPDX-License-Identifier: MIT
// UBDNetwork Mock 
pragma solidity 0.8.21;

import '@uniswap/contracts/libraries/TransferHelper.sol';

import '../../interfaces/IUniswapV2Router02.sol';
import '../../interfaces/IERC20Mint.sol';

contract MockSwapRouter is IUniswapV2Router02 {

    struct Rate {
        uint256 nominatot;
        uint256 denominator;
    }
    address public immutable override factory;
    address public immutable override WETH;

    uint256 public slippagePercent;

    /// @dev Mapping from addres1 from address2 to rate
    /// @dev rate is price of address2 asset expressed in address1 asset units
    /// @dev Example WBTC/USDT pair: address1 - usdt, address2 - wbtc, rate (28_000, 1)
    mapping(address => mapping(address => Rate)) public rates;

    modifier ensure(uint deadline) {
        require(deadline >= block.timestamp, 'UniswapV2Router: EXPIRED');
        _;
    }

    constructor(address _factory, address _WETH)  {
        factory = _factory;
        WETH = _WETH;
    }

    receive() external payable {
       // assert(msg.sender == WETH); // only accept ETH via fallback from the WETH contract
    }

    function setRate(address asset1, address asset2, Rate memory _rate) external {
        rates[asset1][asset2] = _rate;
    }

    function setSlippgae(uint _percent) external {
        slippagePercent = _percent;
    }

    // **** ADD LIQUIDITY ****
    function _addLiquidity(
        address tokenA,
        address tokenB,
        uint amountADesired,
        uint amountBDesired,
        uint amountAMin,
        uint amountBMin
    ) internal virtual returns (uint amountA, uint amountB) {
        
    }
    function addLiquidity(
        address tokenA,
        address tokenB,
        uint amountADesired,
        uint amountBDesired,
        uint amountAMin,
        uint amountBMin,
        address to,
        uint deadline
    ) external virtual override ensure(deadline) returns (uint amountA, uint amountB, uint liquidity) {
        
    }

    function addLiquidityETH(
        address token,
        uint amountTokenDesired,
        uint amountTokenMin,
        uint amountETHMin,
        address to,
        uint deadline
    ) external virtual override payable ensure(deadline) returns (uint amountToken, uint amountETH, uint liquidity) {
    
    }

    // **** REMOVE LIQUIDITY ****
    function removeLiquidity(
        address tokenA,
        address tokenB,
        uint liquidity,
        uint amountAMin,
        uint amountBMin,
        address to,
        uint deadline
    ) public virtual override ensure(deadline) returns (uint amountA, uint amountB) {
    
    }

    function removeLiquidityETH(
        address token,
        uint liquidity,
        uint amountTokenMin,
        uint amountETHMin,
        address to,
        uint deadline
    ) public virtual override ensure(deadline) returns (uint amountToken, uint amountETH) {
    
    }
    function removeLiquidityWithPermit(
        address tokenA,
        address tokenB,
        uint liquidity,
        uint amountAMin,
        uint amountBMin,
        address to,
        uint deadline,
        bool approveMax, uint8 v, bytes32 r, bytes32 s
    ) external virtual override returns (uint amountA, uint amountB) {
    
    }

    function removeLiquidityETHWithPermit(
        address token,
        uint liquidity,
        uint amountTokenMin,
        uint amountETHMin,
        address to,
        uint deadline,
        bool approveMax, uint8 v, bytes32 r, bytes32 s
    ) external virtual override returns (uint amountToken, uint amountETH) {
        
    }

    // **** REMOVE LIQUIDITY (supporting fee-on-transfer tokens) ****
    function removeLiquidityETHSupportingFeeOnTransferTokens(
        address token,
        uint liquidity,
        uint amountTokenMin,
        uint amountETHMin,
        address to,
        uint deadline
    ) public virtual override ensure(deadline) returns (uint amountETH) {
        
    }

    function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
        address token,
        uint liquidity,
        uint amountTokenMin,
        uint amountETHMin,
        address to,
        uint deadline,
        bool approveMax, uint8 v, bytes32 r, bytes32 s
    ) external virtual override returns (uint amountETH) {
    
    }

    // **** SWAP ****
    // requires the initial amount to have already been sent to the first pair
    function _swap(uint[] memory amounts, address[] memory path, address _to) internal virtual {
        
    }

    // Tested
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external virtual override 
      //ensure(deadline) 
      returns (uint[] memory amounts) {
        Rate memory rt = rates[path[0]][path[1]];
        TransferHelper.safeTransferFrom(path[0], msg.sender, address(this), amountIn);
        // so we need devide inAmount by rate
        uint256 amountOut = amountIn * rt.denominator / rt.nominatot
            * 10**IERC20Metadata(path[1]).decimals()
            / 10**IERC20Metadata(path[0]).decimals(); 
        if (slippagePercent > 0) {
            amountOut = amountOut - amountOut * slippagePercent / 100;
        }
        IERC20Mint(path[1]).mint(address(this), amountOut);    
        TransferHelper.safeTransfer(path[1], to, amountOut);
        amounts = new uint[](path.length);
        amounts[0] = amountIn;
        amounts[1] =  amountOut;
        
    }
    function swapTokensForExactTokens(
        uint amountOut,
        uint amountInMax,
        address[] calldata path,
        address to,
        uint deadline
    ) external virtual override ensure(deadline) returns (uint[] memory amounts) {
        
    }

    // Tested 
    function swapExactETHForTokens(uint amountOutMin, address[] calldata path, address to, uint deadline)
        external
        virtual
        override
        payable
        //ensure(deadline)
        returns (uint[] memory amounts)
    {
         Rate memory rt = rates[path[0]][path[1]];
         uint256 amountOut = msg.value * rt.denominator / rt.nominatot
            * 10**IERC20Metadata(path[1]).decimals()
            / 10**IERC20Metadata(path[0]).decimals();
        if (slippagePercent > 0) {
            amountOut = amountOut - amountOut * slippagePercent / 100;
        }    
        IERC20Mint(path[1]).mint(address(this), amountOut);   
        TransferHelper.safeTransfer(path[1], to,  amountOut);
        amounts = new uint[](path.length);
        amounts[0] = msg.value;
        amounts[1] =  amountOut;
    }

    function swapTokensForExactETH(uint amountOut, uint amountInMax, address[] calldata path, address to, uint deadline)
        external
        virtual
        override
        ensure(deadline)
        returns (uint[] memory amounts)
    {
        
    }
    // Tested
    function swapExactTokensForETH(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline)
        external
        virtual
        override
        ensure(deadline)
        returns (uint[] memory amounts)
    {
        Rate memory rt = rates[path[0]][path[1]];
        TransferHelper.safeTransferFrom(path[0], msg.sender, address(this), amountIn);
        uint256 amountOut = amountIn * rt.denominator / rt.nominatot
            * 10**IERC20Metadata(path[1]).decimals()
            / 10**IERC20Metadata(path[0]).decimals(); 
        if (slippagePercent > 0) {
            amountOut = amountOut - amountOut * slippagePercent / 100;
        } 
        address payable toPayable = payable(to);
        toPayable.transfer(amountOut);
        amounts = new uint[](path.length);
        amounts[0] = amountIn;
        amounts[1] =  amountOut;
        //TransferHelper.safeTransfer(path[1], to, amountOut);
        
    }
    function swapETHForExactTokens(uint amountOut, address[] calldata path, address to, uint deadline)
        external
        virtual
        override
        payable
        ensure(deadline)
        returns (uint[] memory amounts)
    {
        
    }

    // **** SWAP (supporting fee-on-transfer tokens) ****
    // requires the initial amount to have already been sent to the first pair
    function _swapSupportingFeeOnTransferTokens(address[] memory path, address _to) internal virtual {
        
    }
    function swapExactTokensForTokensSupportingFeeOnTransferTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external virtual override ensure(deadline) {
        
    }
    function swapExactETHForTokensSupportingFeeOnTransferTokens(
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    )
        external
        virtual
        override
        payable
        ensure(deadline)
    {
        
    }
    function swapExactTokensForETHSupportingFeeOnTransferTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    )
        external
        virtual
        override
        ensure(deadline)
    {
        
    }

    // **** LIBRARY FUNCTIONS ****
    function quote(uint amountA, uint reserveA, uint reserveB) public pure virtual override returns (uint amountB) {
        
    }

    function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut)
        public
        pure
        virtual
        override
        returns (uint amountOut)
    {
        
    }

    function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut)
        public
        pure
        virtual
        override
        returns (uint amountIn)
    {
        
    }

    // tested
    function getAmountsOut(uint amountIn, address[] memory path)
        public
        view
        virtual
        override
        returns (uint[] memory amounts)
    {
        // get rate
        // !!!!! 1-0 vs 0-1 TODO check crossrate case!!
        Rate memory rt = rates[path[1]][path[0]];
        // so we need devide inAmount by rate
        uint256 amountOut = amountIn * rt.nominatot / rt.denominator 
            * 10**IERC20Metadata(path[1]).decimals()
            / 10**IERC20Metadata(path[0]).decimals(); 
        
        amounts = new uint[](path.length);
        amounts[0] = amountIn;
        amounts[1] =  amountOut;
    }

    function getAmountsIn(uint amountOut, address[] memory path)
        public
        view
        virtual
        override
        returns (uint[] memory amounts)
    {
        Rate memory rt = rates[path[0]][path[1]];
        // so we need devide inAmount by rate
        uint256 amountIn = amountOut * rt.nominatot / rt.denominator 
            * 10**IERC20Metadata(path[0]).decimals()
            / 10**IERC20Metadata(path[1]).decimals(); 
        
        amounts = new uint[](path.length);
        amounts[0] = amountIn;
        amounts[1] =  amountOut;
        
    }
}
