import json
import logging

import requests

log = logging.getLogger('pyportal')


class ResultsIterator(object):
    def __init__(self, url, auth=None, offset=0, **params):
        '''
        :param url: the API URL to request results from
        :param auth: an API key (optional)
        :param offset: skip n records (optional)
        :param params: parameters to send with the API request (e.g. filters, query etc)
        '''
        self.url = url
        self.offset = offset
        self._original_offset = offset
        self.params = params
        self._original_params = params
        self.auth = auth

    @classmethod
    def get_result(cls, response):
        '''
        Retrieve a result from the HTTP response
        :param response: a response object
        :return: either the 'result' dict, or None if no result is returned
        '''
        j = response.json()
        no_results = j.get('result', None) is None
        if response.ok and j.get('success', False) and not no_results:
            return j.get('result', j)
        else:
            return None

    def _get(self):
        '''
        Make the API request.
        :return: the response object
        '''
        self.params['offset'] = self.offset
        headers = {
            'Authorization': self.auth
            } if self.auth is not None else {}
        r = requests.get(self.url, headers=headers, params=self.params)
        if not r.ok:
            log.error(f'HTTP request failed ({r.status_code}) for {self.url}.')
            log.error(r.reason)
            raise requests.HTTPError
        return r

    def _reset(self):
        '''
        Reset the iterator to its construction state.
        '''
        self.offset = self._original_offset
        self.params = self._original_params

    def next(self):
        '''
        Get the next 'page' of results, then set the new offset for the following page. Raises
        StopIteration if there's no more results.
        :return: list of records
        '''
        try:
            r = self._get()
        except requests.HTTPError:
            self._reset()
            raise StopIteration
        result = self.get_result(r)
        no_records = result is None or 'records' not in result
        end_of_queue = self.offset >= result.get('total', 0)
        if result is None or no_records or end_of_queue:
            log.debug('Nothing else in queue.')
            self._reset()
            raise StopIteration
        else:
            self.offset += len(result['records'])
            return result['records']

    def all(self):
        '''
        A generator that paginates automatically and yields individual records.
        :return: generator that yields dicts
        '''
        self.params['limit'] = 1000
        while True:
            try:
                for record in self.next():
                    yield record
            except StopIteration:
                break

    def first(self):
        '''
        Returns the first record (taking offset into account).
        :return: dict
        '''
        self._reset()
        self.params['limit'] = 1
        page = self.next()
        self._reset()
        return page[0]

    def count(self):
        '''
        Returns a count of all records in the result set.
        :return: int
        '''
        self._reset()
        response = self._get()
        return response.json().get('result', {}).get('total', 0) if response.ok else 0


class AssetIterator(ResultsIterator):
    def next(self):
        '''
        Returns a list of record assets in the form (record_id, asset_dict). Does not group assets
        together by record.
        :return: list of tuples in the form (record_id, asset_dict)
        '''
        records = super(AssetIterator, self).next()
        assets = []
        for record in records:
            media = record.get('associatedMedia')
            media = json.loads(media) if isinstance(media, str) else media
            assets += [(record.get('_id'), media)]
        if len(assets) > 0:
            return assets
        else:
            return self.next()

    def count(self):
        raise NotImplementedError
