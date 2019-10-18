import pyportal
import pyportal.errors
import pytest


def test_api_construction():
    api_without_key = pyportal.API()
    assert api_without_key.key is None
    api_with_key = pyportal.API('random-test-key')
    assert api_with_key.key == 'random-test-key'


def test_extract_params_from_url():
    url = 'https://data.nhm.ac.uk/dataset/56e711e6-c847-4f99-915a-6894bb5c5dea/resource/05ff2255' \
          '-c38a-40c9-b657-4ccb55ab2feb?view_id=203a0ae5-6a14-480a-a407-27eeb9373858&value' \
          '=&_genus_limit=0&q=banana&filters=collectionCode%3Abot%7Ccountry%3Aaustralia&sort' \
          '=genus%20desc%26fields%3Dcountry%2Cfamily%2Cgenus'
    expected_params = {
        'resource_id': '05ff2255-c38a-40c9-b657-4ccb55ab2feb',
        'query': 'banana',
        'collectionCode': 'bot',
        'country': 'australia',
        'sort': ['genus desc'],
        'fields': ['country', 'family', 'genus']
        }
    assert pyportal.API.from_url(url) == expected_params


def test_rejects_incorrect_url():
    wrong_host = 'https://google.com/dataset/56e711e6-c847-4f99-915a-6894bb5c5dea/resource' \
                 '/05ff2255-c38a-40c9-b657-4ccb55ab2feb'
    with pytest.raises(pyportal.errors.IncorrectURLError):
        pyportal.API.from_url(wrong_host)

    no_resource = 'https://data.nhm.ac.uk'
    with pytest.raises(pyportal.errors.IncorrectURLError):
        pyportal.API.from_url(no_resource)
