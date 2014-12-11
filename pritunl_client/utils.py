from pritunl_client.constants import *
from pritunl_client.exceptions import *

import interface
import urllib2
import httplib
import socket
import json
import time
import uuid
import hmac
import hashlib
import base64

class Response:
    def __init__(self, url, headers, status_code, reason, content):
        self.url = url
        self.headers = headers
        self.status_code = status_code
        self.reason = reason
        self.content = content

    def json(self):
        return json.loads(self.content)

class request:
    @classmethod
    def _request(cls, method, url, data=None, json_data=None, headers=None, timeout=None):
        if headers is None:
            headers = {}
        if timeout is None:
            timeout = socket._GLOBAL_DEFAULT_TIMEOUT
        request = urllib2.Request(url, headers=headers)
        request.get_method = lambda: method

        if json_data is not None:
            request.add_header('Content-Type', 'application/json')
            data = json.dumps(json_data)

        try:
            url_response = urllib2.urlopen(request, data=data, timeout=timeout)
            return Response(url,
                headers=dict(url_response.info().items()),
                status_code=url_response.getcode(),
                reason='OK',
                content=url_response.read(),
            )
        except urllib2.HTTPError as error:
            return Response(url,
                headers=dict(error.info().items()),
                status_code=error.getcode(),
                reason=error.reason,
                content=error.read(),
            )
        except Exception as error:
            raise httplib.HTTPException(error)

    @classmethod
    def get(cls, url, **kwargs):
        return cls._request('GET', url, **kwargs)

    @classmethod
    def options(cls, url, **kwargs):
        return cls._request('OPTIONS', url, **kwargs)

    @classmethod
    def head(cls, url, **kwargs):
        return cls._request('HEAD', url, **kwargs)

    @classmethod
    def post(cls, url, **kwargs):
        return cls._request('POST', url, **kwargs)

    @classmethod
    def put(cls, url, **kwargs):
        return cls._request('PUT', url, **kwargs)

    @classmethod
    def patch(cls, url, **kwargs):
        return cls._request('PATCH', url, **kwargs)

    @classmethod
    def delete(cls, url, **kwargs):
        return cls._request('DELETE', url, **kwargs)

def auth_request(method, host, path, token, secret,
        json_data=None, timeout=None):
    if json_data:
        headers = {'Content-Type', 'application/json'}
        data = json.dumps(json_data)
    else:
        headers = None
        data = None
    auth_timestamp = str(int(time.time()))
    auth_nonce = uuid.uuid4().hex
    auth_string = '&'.join([token, auth_timestamp, auth_nonce,
        method.upper(), path] + ([data] if data else []))

    auth_signature = base64.b64encode(hmac.new(
        secret.encode(), auth_string, hashlib.sha256).digest())
    auth_headers = {
        'Auth-Token': token,
        'Auth-Timestamp': auth_timestamp,
        'Auth-Nonce': auth_nonce,
        'Auth-Signature': auth_signature,
    }
    if headers:
        auth_headers.update(headers)
    return getattr(request, method.lower())(
        host + path,
        headers=auth_headers,
        data=data,
        timeout=timeout,
    )

def get_logo():
    if PLATFORM == LINUX:
        logo_path = interface.lookup_icon('pritunl_client')
        if logo_path:
            return logo_path
    return LOGO_DEFAULT_PATH

def get_connected_logo():
    if PLATFORM == LINUX:
        logo_path = interface.lookup_icon('pritunl_client_connected')
        if logo_path:
            return logo_path
    return CONNECTED_LOGO_DEFAULT_PATH

def get_disconnected_logo():
    if PLATFORM == LINUX:
        logo_path = interface.lookup_icon('pritunl_client_disconnected')
        if logo_path:
            return logo_path
    return DISCONNECTED_LOGO_DEFAULT_PATH
