from dataclasses import dataclass


@dataclass
class resources:
    '''
    IDs for commonly searched resources.
    '''
    specimens = '05ff2255-c38a-40c9-b657-4ccb55ab2feb'
    indexlots = 'bb909597-dedf-427d-8c04-4c02b3a24db3'


@dataclass
class URLs:
    base_url = 'https://data.nhm.ac.uk/api/3'
    asset_url = 'https://www.nhm.ac.uk/services/media-store/asset/{0}/contents/preview'
