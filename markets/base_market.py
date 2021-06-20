import os
import jwt
import uuid
import hashlib
import json
import time
from urllib.parse import urlencode

import requests

class BaseMarket():
    def __init__(self):
        self.access_key = 'y4YiH7yQ6IV7DH1kr8aaDxrNwrirvxqZxHRAY3gO'
        self.secret_key = 'nKowNJTxJ1xyTiQLLNZp1G6NKYP5txsR2OxDY1DV'
        self.server_url = 'https://api.upbit.com'

    