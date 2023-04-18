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



