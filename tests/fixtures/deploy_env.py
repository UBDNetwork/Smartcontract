import pytest

@pytest.fixture(scope="module")
def distributor(accounts, UBDNDistributor):
    d = accounts[0].deploy(UBDNDistributor)
    yield d

@pytest.fixture(scope="module")
def lockerdistributor(accounts, UBDNLockerDistributor):
    d = accounts[0].deploy(UBDNLockerDistributor, 0)
    yield d    

@pytest.fixture(scope="module")
def ubdn(accounts, UBDNToken, distributor):
    erc = accounts[0].deploy(UBDNToken, 
        distributor.address, 
        distributor.address, 
        50_000_000e18
    )
    yield erc

@pytest.fixture(scope="module")
def ubdnlocked(accounts, UBDNToken, lockerdistributor):
    erc = accounts[0].deploy(UBDNToken, 
        accounts[0], 
        lockerdistributor.address, 
        5_000_000e18
    )
    yield erc    

@pytest.fixture(scope="module")
def erc20(accounts, UBDNToken):
    erc = accounts[0].deploy(UBDNToken, accounts[1], accounts[0], 5_000_000e18)
    yield erc

@pytest.fixture(scope="module")
def erc20_ubd(accounts, UBDToken):
    erc = accounts[0].deploy(UBDToken, accounts[0])
    yield erc

@pytest.fixture(scope="module")
def usdt(accounts, MockToken):
    erc = accounts[0].deploy(MockToken, 'USDT Mock Token', 'USDT', 6)
    yield erc

@pytest.fixture(scope="module")
def usdc(accounts, MockToken):
    erc = accounts[0].deploy(MockToken, 'USDC Mock Token', 'USDC', 12)
    yield erc

@pytest.fixture(scope="module")
def dai(accounts, MockToken):
    erc = accounts[0].deploy(MockToken, 'DAI Mock Token', 'DAI', 18)
    yield erc

@pytest.fixture(scope="module")
def wbtc(accounts, MockToken):
    erc = accounts[0].deploy(MockToken, 'Wrapped BTC Token', 'WBTC', 8)
    yield erc

@pytest.fixture(scope="module")
def wbnb(accounts, MockToken):
    erc = accounts[0].deploy(MockToken, 'Wrapped BNB Token', 'WBNB', 18)
    yield erc


@pytest.fixture(scope="module")
def weth(accounts, MockToken):
    erc = accounts[0].deploy(MockToken, 'Wrapped ETHER', 'WETH', 18)
    yield erc

#------------------------------
@pytest.fixture(scope="module")
def exchange_single(accounts, UBDExchange, usdt):
    exch = accounts[0].deploy(UBDExchange, usdt.address, accounts[9])
    yield exch

@pytest.fixture(scope="module")
def ubd_exch(accounts, UBDToken, exchange_single):
    erc = accounts[0].deploy(UBDToken, exchange_single)
    yield erc

@pytest.fixture(scope="module")
def markets(accounts, MarketRegistry):
    m = accounts[0].deploy(MarketRegistry, 1)
    yield m

@pytest.fixture(scope="module")
def sandbox1(accounts, SandBox1, usdt, markets):
    snb1 = accounts[0].deploy(SandBox1, markets.address, usdt.address)
    yield snb1

@pytest.fixture(scope="module")
def sandbox2(accounts, SandBox2, markets, dai):
    snb2 = accounts[0].deploy(SandBox2, markets.address, dai.address)
    yield snb2

@pytest.fixture(scope="module")
def treasury(accounts, Treasury, markets):
    tr = accounts[0].deploy(Treasury,  markets.address)
    yield tr

@pytest.fixture(scope="module")
def ubd(accounts, UBDToken, sandbox1):
    erc = accounts[0].deploy(UBDToken, sandbox1)
    #sandbox1.setUBDToken(erc.address, {'from':accounts[0]})
    yield erc

##############################################################
@pytest.fixture(scope="module")
def mockuniv2(accounts, MockSwapRouter, dai, usdt, wbtc, weth, usdc, wbnb):
    uni = accounts[0].deploy(MockSwapRouter, weth, weth)
    #accounts[9].transfer(uni.address, accounts[9].balance()-1e18)
    #uni.setRate(weth.address, usdt.address, (1800, 1))
    #uni.setRate(wbtc.address, usdt.address, (28000, 1))
    uni.setRate(usdt.address, wbtc.address, (28000, 1))
    uni.setRate(usdt.address, weth.address, (1400, 1))
    uni.setRate(wbtc.address, usdt.address, (1, 28000))
    uni.setRate(weth.address, usdt.address, (1,  1400))
    uni.setRate(wbtc.address, dai.address, (1, 28000))
    uni.setRate(weth.address, dai.address, (1,  1400))
    uni.setRate(dai.address, wbtc.address, (28000, 1))
    uni.setRate(dai.address, weth.address, (1400, 1))
    uni.setRate(usdc.address, usdt.address, (1, 1))
    uni.setRate(usdt.address, usdc.address, (1, 1))
    uni.setRate(wbtc.address, usdc.address, (1, 28000))
    uni.setRate(weth.address, usdc.address, (1,  1400))
    uni.setRate(usdc.address, wbtc.address, (28000, 1))
    uni.setRate(usdc.address, weth.address, (1400, 1))

    uni.setRate(usdt.address, wbnb.address, (200, 1))
    uni.setRate(wbnb.address, usdt.address, (1, 200))

   
    # uni.setRate(weth.address, usdt.address, (1800, 1))
    # uni.setRate(weth.address, usdt.address, (1800, 1))
    # #sandbox1.setUBDToken(erc.address, {'from':accounts[0]})
    yield uni

@pytest.fixture(scope="module")
def market_adapter(accounts, MarketAdapterCustomMarket, mockuniv2):
    ma = accounts[0].deploy(MarketAdapterCustomMarket, 'Mock UniSwapV2 adapter', mockuniv2)
    yield ma
#MarketAdapterCustomMarket
#28_000_000 00000000
#1000 000000

@pytest.fixture(scope="module")
def hackERC20(accounts, HackERC20, market_adapter, sandbox1):
    erc = accounts[0].deploy(HackERC20, 'Hack ERC20', 'Hack', market_adapter, sandbox1)
    yield erc
