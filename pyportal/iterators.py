import json
import logging

import requests

log = logging.getLogger('pyportal')


class ResultsIterator(object):
    def __init__(self, url, auth=None, offset=0, records_only=True, **params):
        self.url = url
        self.records_only = records_only
        self.offset = offset
        self._original_offset = offset
        self.params = params
        self.auth = auth

    @classmethod
    def get_result(cls, response):
        j = response.json()
        no_results = j.get('result', {}).get('total', 0) == 0
        if response.ok and j.get('success', False) and not no_results:
            return j.get('result', j)
        else:
            return None

    def _get(self):
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
        self.offset = self._original_offset

    def next(self):
        try:
            r = self._get()
        except requests.HTTPError:
            self._reset()
            raise StopIteration
        result = self.get_result(r)
        no_records = self.records_only and 'records' not in result
        end_of_queue = self.offset >= result.get('total', 0)
        if result is None or no_records or end_of_queue:
            log.debug('Nothing else in queue.')
            self._reset()
            raise StopIteration
        else:
            self.offset += len(result['records'])
            if self.records_only:
                return result['records']
            return result

    def all(self):
        while True:
            for record in self.next():
                yield record

    def first(self):
        self._reset()
        page = self.next()
        return page[0]

    def count(self):
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
