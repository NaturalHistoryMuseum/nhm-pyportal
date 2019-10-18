import json
import logging
from dataclasses import dataclass

from .constants import URLs
from .errors import ParameterMissingError

log = logging.getLogger('pyportal')


class Endpoint(object):
    def __init__(self, endpoint, requires_auth=False, has_records=False, has_assets=False,
                 required_params=None, optional_params=None):
        '''
        :param endpoint: the action name/part of the URL defining the API endpoint
        :param requires_auth: whether the action requires auth
        :param has_records: whether the API is expected to return iterable records
        :param has_assets: whether those iterable records have associated media
        :param required_params: names of parameters required in a request
        :param optional_params: names of parameters that can be optionally included in a request
        '''
        self.endpoint = endpoint
        self.url = URLs.base_url + '/action/' + endpoint
        self.requires_auth = requires_auth
        self.has_records = has_records
        self.has_assets = has_assets
        self.required_params = required_params or []
        self.optional_params = optional_params or []

    def format_params(self, **params):
        '''
        Ensure the passed parameters fit the required/optional parameters for this endpoint.
        :param params: keyword arguments for any parameters to be included, e.g. q='my query'
        :return: a dict of parameters
        '''
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


@dataclass
class endpoints:
    '''
    A convenient collection of endpoints.
    '''
    datastore_search = Endpoint('datastore_search', has_records=True, has_assets=True,
                                required_params=['resource_id'],
                                optional_params=['q', 'filters', 'sort', 'fields'])
