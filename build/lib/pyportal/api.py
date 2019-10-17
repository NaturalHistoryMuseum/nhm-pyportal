import json
import logging
import urllib.parse

from .constants import URLs
from .errors import IncorrectURLError, ParameterMissingError
from .iterators import AssetIterator, ResultsIterator

log = logging.getLogger('pyportal')


class API(object):
    def __init__(self, api_key=None):
        self.key = api_key

    @classmethod
    def from_url(cls, url):
        extracted_params = {}
        url = urllib.parse.unquote(url)
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname != 'data.nhm.ac.uk':
            raise IncorrectURLError(f'Host must be "data.nhm.ac.uk", not "{parsed.hostname}".')
        if '/resource/' not in parsed.path:
            raise IncorrectURLError(f'"{parsed.path}" is not a resource URL.')
        resource_id = parsed.path.split('/resource/')[-1]
        extracted_params['resource_id'] = resource_id
        params = urllib.parse.parse_qs(parsed.query)
        for f in params.get('filters', []):
            k, v = f.split(':', 1)
            extracted_params[k] = v
        q = params.get('q', [None])[0]
        if q is not None:
            extracted_params['query'] = q
        sort = params.get('sort', [])
        if len(sort) > 0:
            extracted_params['sort'] = sort
        fields = params.get('fields', [])
        if len(fields) > 0:
            extracted_params['fields'] = fields
        return extracted_params

    def _get(self, endpoint, iterator, offset, limit, **kwargs):
        params = endpoint.format_params(**kwargs)
        return iterator(endpoint.url, auth=self.key, offset=offset, limit=limit, **params)

    # COMMON ACTIONS

    def records(self, resource_id, offset=0, limit=100, sort=None, fields=None, query=None,
                **filters):
        sort = sort or []
        fields = fields or []
        return self._get(datastore_search, ResultsIterator, offset, limit, sort=sort, fields=fields,
                         resource_id=resource_id, filters=filters, q=query)

    def assets(self, resource_id, offset=0, limit=100, sort=None, fields=None, query=None,
               **filters):
        filters['_has_image'] = True
        sort = sort or []
        fields = fields or []
        return self._get(datastore_search, AssetIterator, offset, limit, sort=sort, fields=fields,
                         resource_id=resource_id, filters=filters, q=query)


class Endpoint(object):
    def __init__(self, endpoint, requires_auth=False, has_records=False, has_assets=False,
                 required_params=None, optional_params=None):
        self.endpoint = endpoint
        self.url = URLs.base_url + '/action/' + endpoint
        self.requires_auth = requires_auth
        self.has_records = has_records
        self.has_assets = has_assets
        self.required_params = required_params or []
        self.optional_params = optional_params or []

    def format_params(self, **params):
        returned_params = {}
        for p in self.required_params:
            if p not in params:
                raise ParameterMissingError(f'"{p}" is a required parameter.')
            else:
                v = params[p]
                returned_params[p] = json.dumps(v) if isinstance(v, dict) else v
        for p in self.optional_params:
            if p in params:
                v = params[p]
                returned_params[p] = json.dumps(v) if isinstance(v, dict) else v
            else:
                log.debug(f'Optional parameter "{p}" not found.')
        return returned_params


datastore_search = Endpoint('datastore_search', has_records=True, has_assets=True,
                            required_params=['resource_id'],
                            optional_params=['q', 'filters', 'sort', 'fields'])
