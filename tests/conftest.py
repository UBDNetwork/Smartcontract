import pytest

from brownie._config import CONFIG
#from brownie import chain


pytest_plugins = [
   #"fixtures.conftest",
   "fixtures.accounts",
   "fixtures.deploy_env"
  ]
#brownie._config.CONFIG.active_network['settings']['priority_fee'] = chain.priority_fee

@pytest.fixture(scope="session")
def is_forked():
    yield "fork" in CONFIG.active_network['id']
