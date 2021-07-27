import asyncio
import pytest

from hat import aio
from hat import util

import restlog.main


pytestmark = pytest.mark.asyncio


@pytest.fixture
def conf(tmp_path):
    return {'log': {'version': 1},
            'host': '127.0.0.1',
            'port': util.get_unused_tcp_port(),
            'db_path': str((tmp_path / 'restlog.db').resolve()),
            'max_results': 100}


@pytest.fixture
async def main(conf):
    async_group = aio.Group()
    try:
        async_group.spawn(restlog.main.async_main, conf)
        yield
    finally:
        await async_group.async_close()


async def test_run(main):
    await asyncio.sleep(0.01)
