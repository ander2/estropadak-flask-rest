import pytest


@pytest.fixture()
def credentials():
    return dict(username='test_api', password='test_api_pass')
