from . import client, test_file


def test_local_single(test_file):
    response = client.post('/local_single', files={'book': test_file})
    assert response.status_code == 200
    res = response.json()
    assert res['status'] is True
    assert res['file']['filename'] == 'Forex-Trading-For-Beginners.pdf'
    assert len(res['files']) == 1
