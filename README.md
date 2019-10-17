# pyportal

A Python wrapper around the API for the Natural History Museum's [Data Portal](https://data.nhm.ac.uk).

This module is new and under development, so does not include all actions available through the API; it prioritises the record search functionality.

We have more generic (and comprehensive) API documentation available [here](https://naturalhistorymuseum.github.io/dataportal-docs).


## Requirements

- Python 3.7+


## Installation

```sh
pip install -e git+git://github.com/NaturalHistoryMuseum/nhm-pyportal.git#egg=pyportal
```


## Quickstart Usage

Start by creating an `API` object:

```python
import pyportal

api = pyportal.API()
```

### Searching

You can either search for all records, or specifically for assets/media. The syntax is very similar for both.

```python
from pyportal import constants

# specify any resource you want, but the IDs for the specimens and index lots resources are built in
resource_id = constants.resources.specimens

# find all records in the specimens resource
search = api.records(resource_id)

# OR find all assets (images) in the specimens resource
search = api.assets(resource_id)
```

The search above is equivalent to [this search](https://data.nhm.ac.uk/dataset/56e711e6-c847-4f99-915a-6894bb5c5dea/resource/05ff2255-c38a-40c9-b657-4ccb55ab2feb) on the Data Portal website.

There is a helper method to transform a data portal URL into a `dict` that can be passed into the search constructor.

```python
url = 'https://data.nhm.ac.uk/dataset/56e711e6-c847-4f99-915a-6894bb5c5dea/resource/05ff2255-c38a-40c9-b657-4ccb55ab2feb?filters=collectionCode%3Abot'

# these two searches are equivalent

print(api.records(constants.resources.specimens, collectionCode='bot').count())  # 775440

print(api.records(**api.from_url(url)).count())  # 775440
```

You can specify the following parameters (all are optional):

- `query`: a free-text search, e.g. `query='bugs'`
- `sort`: a list of fields and sort directions, e.g. `sort=['country asc', 'family desc']`
- `fields`: a list of fields to return for each record (leave blank to return all), e.g. `fields=['country', 'family', 'genus']`
- `offset`: skip the first _n_ results, e.g. `offset=50`
- `limit`: return only _n_ results _per page_ (defaults to 100), e.g. `limit=10`

Any other keyword arguments will be considered `filters`.

```python
search = api.records(constants.resources.specimens, query='bugs', sort=['country asc', 'family desc'], fields=['country', 'family', 'genus'], offset=50, limit=10)
```

### Viewing results

Iterate through all results using `.all()` (this ignores `limit`):

```python
for record in search.all():
    print(record)
```

Or just view the first one with `.first()`:

```python
print(search.first())
```

You could also view a page (blocks of records in the size set by `limit`) at a time using `.next()`:

```python
try:
    page = search.next()
    for record in page:
        print(record)
except StopIteration:  # raised by search.next() if there's no next page
    print('No more results.')
```

If you just want the total number of records, use `.count()`:

```python
print(search.count())
```