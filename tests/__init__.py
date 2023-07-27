from fastapi.testclient import TestClient
from pytest import fixture

from .app import app

client = TestClient(app)

@fixture
def test_file():
    return open('tests/test_data/Forex-Trading-For-Beginners.pdf', 'rb')
