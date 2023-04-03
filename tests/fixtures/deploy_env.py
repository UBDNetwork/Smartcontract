import pytest

@pytest.fixture(scope="module")
def distributor(accounts, UBDNDistributor):
    d = accounts[0].deploy(UBDNDistributor)
    yield d

@pytest.fixture(scope="module")
def ubdn(accounts, UBDNToken, distributor):
    erc = accounts[0].deploy(UBDNToken, distributor.address)
    yield erc

@pytest.fixture(scope="module")
def erc20(accounts, UBDNToken):
    erc = accounts[0].deploy(UBDNToken, accounts[0])
    yield erc


@pytest.fixture(scope="module")
def usdt(accounts, MockToken):
    erc = accounts[0].deploy(MockToken, 'USDT Mock Token', 'USDT', 6)
    yield erc

@pytest.fixture(scope="module")
def usdc(accounts, MockToken):
    erc = accounts[0].deploy(MockToken, 'USDC Mock Token', 'USDC', 6)
    yield erc
 
def dai(accounts, MockToken):
    erc = accounts[0].deploy(MockToken, 'DAI Mock Token', 'DAI', 18)
    yield erc



