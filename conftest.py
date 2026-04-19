from sys import modules

import niquests
from niquests.packages import urllib3

# see https://niquests.readthedocs.io/en/latest/community/extensions.html#responses
modules["requests"] = niquests
modules["requests.models"] = niquests.models
modules["requests.adapters"] = niquests.adapters
modules["requests.exceptions"] = niquests.exceptions
modules["requests.packages.urllib3"] = urllib3
