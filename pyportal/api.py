import logging
import urllib.parse

from .endpoints import endpoints
from .errors import IncorrectURLError
from .iterators import AssetIterator, ResultsIterator

log = logging.getLogger('pyportal')


class API(object):
    def __init__(self, api_key=None):
        self.key = api_key

    @classmethod
    def from_url(cls, url):
        '''
        A helper method to extract search parameters from a data portal resource URL.
        :param url: the URL for a search page on the data portal
        :return: a dictionary of parameters that can be passed into API.search() as **kwargs
        '''
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
        filters = params.get('filters', [None])[0]
        if filters is not None:
            for f in filters.split('|'):
                k, v = f.split(':', 1)
                extracted_params[k] = v
        q = params.get('q', [None])[0]
        if q is not None:
            extracted_params['query'] = q
        sort = params.get('sort', [None])[0]
        if sort is not None:
            extracted_params['sort'] = sort.split(',')
        fields = params.get('fields', [None])[0]
        if fields is not None:
            extracted_params['fields'] = fields.split(',')
        return extracted_params

    def _get_result_iterator(self, endpoint, iterator, offset, limit, **kwargs):
        '''
        Common method to format parameters and return a results iterator.
        :param endpoint: the target endpoint
        :param iterator: the type of results iterator, e.g. ResultsIterator
        :param offset: skip n records
        :param limit: number of results per page
        :param kwargs: any other arguments, e.g. query, filters
        :return: a ResultIterator (or subclass) instance
        '''
        params = endpoint.format_params(**kwargs)
        return iterator(endpoint.url, auth=self.key, offset=offset, limit=limit, **params)

    # COMMON ACTIONS

    def records(self, resource_id, offset=0, limit=100, sort=None, fields=None, query=None,
                **filters):
        '''
        Use the datastore_search endpoint to search for records in a resource.
        :param resource_id: the id of the resource, i.e. the id after /resource/ in the URL
        :param offset: skip n records (optional)
        :param limit: number of results per page (optional)
        :param sort: list of fields and directions (asc, desc) to sort the records by (optional)
        :param fields: list of fields to return, default is all (optional)
        :param query: free text search (optional)
        :param filters: filter by record attributes
        :return: a ResultIterator instance
        '''
        sort = sort or []
        fields = fields or []
        return self._get_result_iterator(endpoints.datastore_search, ResultsIterator, offset, limit,
                                         sort=sort, fields=fields, resource_id=resource_id,
                                         filters=filters, q=query)

    def assets(self, resource_id, offset=0, limit=100, sort=None, query=None, **filters):
        '''
        Use the datastore_search endpoint to search for assets attached to records in a resource. Ignores records without images.
        :param resource_id: the id of the resource, i.e. the id after /resource/ in the URL
        :param offset: skip n records (optional)
        :param limit: number of results per page (optional)
        :param sort: list of fields and directions (asc, desc) to sort the records by (
        optional)
        :param query: free text search (optional)
        :param filters: filter by record attributes
        :return: an AssetIterator instance
        '''
        filters['_has_image'] = True
        sort = sort or []
        fields = ['_id', 'associatedMedia']
        return self._get_result_iterator(endpoints.datastore_search, AssetIterator, offset, limit,
                                         sort=sort, fields=fields, resource_id=resource_id,
                                         filters=filters, q=query)
