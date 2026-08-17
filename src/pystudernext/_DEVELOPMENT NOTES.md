
# Running the examples or the unit tests
Before running the examples or the unit tests, install the 'pystudernext' library locally:
- Open a command prompt at the root of this project
- Run: pip install -e .    (or: python -m pip install -e .)

# Do not edit *_sync.py files
The pystudernext library provides both an async as well as a sync Api.
To maintain development consistency the sync api is auto generated from the async api.
Therefore, do NOT edit the *_sync.py files.

To re-generate the sync api after editing of the async api, unit-tests or examples do:
- Open a command prompt at the root of this project
- (first time) Run: pip install unasyncd  (or: python -m pip install unasyncd)
- Run: unasyncd
