import itertools

import pytest

from hat import aio
from hat import util

import restlog.server


pytestmark = pytest.mark.asyncio


@pytest.fixture
def port():
    return util.get_unused_tcp_port()


class Backend(aio.Resource):

    def __init__(self):
        self._async_group = aio.Group()
        self._next_entry_ids = itertools.count(1)

    @property
    def async_group(self):
        return self._async_group

    async def register(self, timestamp, address, source, type, data):
        return {'entry_id': next(self._next_entry_ids),
                'timestamp': timestamp,
                'address': address,
                'source': source,
                'type': type,
                'data': data}

    async def get_entries(self, source=None, type=None, last_entry_id=None,
                          max_results=None):
        return {'entries': [],
                'more': False}

    async def get_entry(self, entry_id):
        return


async def test_create(port):
    backend = Backend()
    server = await restlog.server.create('127.0.0.1', port, backend)
    assert server.is_open
    await server.async_close()
