"""Regression guard for SUPPORT-17624.

Marketo stopped accepting the OAuth token as an ``access_token`` query
parameter on 2026-08-31. Every request must carry it in an
``Authorization: Bearer`` header instead.

This component makes no HTTP calls of its own; it delegates everything to
``marketorestpython``. The fix is therefore the ``marketorestpython==0.5.25``
pin in the Dockerfile. These tests assert the property we actually depend on,
so an unpinned or downgraded library fails the build instead of failing the
customer.

They run inside the built image (``python -m unittest discover``), so they
also prove the pinned dependency stack imports on this base image.
"""
import unittest
from unittest import mock

import pandas  # noqa: F401  pinned to 1.3.5; must import on this base image
from marketorestpython.client import MarketoClient
from marketorestpython.helper import http_lib

# Every method this component dispatches through mc.execute(method=...).
# See src/functions.py.
METHODS_USED_BY_COMPONENT = [
    'get_lead_by_id',
    'get_multiple_leads_by_filter_type',
    'get_companies',
    'get_lead_activities',
    'get_lead_changes',
    'get_deleted_leads',
    'get_opportunities',
    'get_multiple_campaigns',
    'get_activity_types',
]


class FakeResponse(object):
    status_code = 200

    def json(self):
        return {'success': True, 'result': []}


class TestTokenTransport(unittest.TestCase):
    """The token must travel in the header, never in the query string."""

    def _http(self):
        # Older versions of the library take fewer arguments. Fall back so the
        # test fails on the header assertion below, not on the constructor.
        try:
            return http_lib.HttpLib(max_retry_time_conf=1, requests_timeout=None)
        except TypeError:
            return http_lib.HttpLib(1)

    def test_get_uses_authorization_header(self):
        with mock.patch.object(http_lib.requests, 'get',
                               return_value=FakeResponse()) as request:
            self._http().get('https://x.mktorest.com/rest/v1/leads.json',
                             {'access_token': 'TOKEN', 'batchSize': 10})

        kwargs = request.call_args[1]
        self.assertEqual('Bearer TOKEN', kwargs['headers'].get('Authorization'))
        self.assertNotIn('access_token', kwargs['params'])
        self.assertEqual(10, kwargs['params']['batchSize'])

    def test_post_uses_authorization_header(self):
        with mock.patch.object(http_lib.requests, 'post',
                               return_value=FakeResponse()) as request:
            self._http().post('https://x.mktorest.com/rest/v1/leads.json',
                              {'access_token': 'TOKEN'}, data={'input': []})

        kwargs = request.call_args[1]
        self.assertEqual('Bearer TOKEN', kwargs['headers'].get('Authorization'))
        self.assertNotIn('access_token', kwargs['params'])


class TestLibraryContract(unittest.TestCase):
    """Guard the library upgrade: the methods we call must still be there."""

    def test_methods_used_by_component_exist(self):
        for name in METHODS_USED_BY_COMPONENT:
            self.assertTrue(callable(getattr(MarketoClient, name, None)),
                            'MarketoClient.%s is missing' % name)


if __name__ == '__main__':
    unittest.main()
