# pyportal

A Python wrapper around the API for the Natural History Museum's [Data Portal](https://data.nhm.ac.uk).

This module is new and under development, so does not include all actions available through the API; it prioritises the record search functionality.

We have more generic (and comprehensive) API documentation available [here](https://naturalhistorymuseum.github.io/dataportal-docs).


## Requirements

- Python 3.7+


## Installation

```sh
pip install -e git+git://github.com/NaturalHistoryMuseum/pyportal.git#egg=pyportal
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

# find botany records in the specimens resource
search = api.records(resource_id, collectionCode='bot')

# OR find botany assets (images) in the specimens resource
search = api.assets(resource_id, collectionCode='bot')
```

You can use any of the Data Portal's 
The search above is equivalent to [this search](https://data.nhm.ac.uk/dataset/56e711e6-c847-4f99-915a-6894bb5c5dea/resource/05ff2255-c38a-40c9-b657-4ccb55ab2feb?filters=collectionCode%3Abot) on the Data Portal website.

There is a helper method to transform a data portal URL (e.g. the one linked above) into a `dict` that can be passed into the search constructor.

```python
url = 'https://data.nhm.ac.uk/dataset/56e711e6-c847-4f99-915a-6894bb5c5dea/resource/05ff2255-c38a-40c9-b657-4ccb55ab2feb?filters=collectionCode%3Abot'

# these two searches are equivalent

print(api.records(constants.resources.specimens, collectionCode='bot').count())  # 775440

print(api.records(**api.from_url(url)).count())  # 775440
```

### Viewing results

Iterate through all results using `.all()`:

```python
for record in search.all():
    print(record)
```

Or just view the first one with `.first()`:

```python
print(search.first())
```

You could also iterate through entire pages (blocks of records) manually using `.next()`:

```python
while True:
    for record in search.next():
        print(record)
```

If you just want the total number of records, use `.count()`:

```python
print(search.count())
```