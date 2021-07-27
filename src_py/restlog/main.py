from pathlib import Path
import asyncio
import contextlib
import logging.config
import sys
import typing

import click

from hat import aio
from hat import json

from restlog import common
import restlog.backend
import restlog.server


@click.command()
@click.option('--conf', default=None, metavar='PATH', type=Path,
              help="configuration defined by restlog://main.yaml# "
                   "(default $XDG_CONFIG_HOME/restlog/restlog.{yaml|yml|json})")  # NOQA
def main(conf: typing.Optional[Path]):
    aio.init_asyncio()

    if not conf:
        for suffix in ('.yaml', '.yml', '.json'):
            conf = (common.user_conf_dir / 'restlog').with_suffix(suffix)
            if conf.exists():
                break
    conf = json.decode_file(conf)
    common.json_schema_repo.validate('restlog://main.yaml#', conf)

    logging.config.dictConfig(conf['log'])

    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main(conf))


async def async_main(conf: json.Data):
    async_group = aio.Group()

    try:
        backend = await restlog.backend.create(path=Path(conf['db_path']),
                                               max_results=conf['max_results'])
        _bind_resource(async_group, backend)

        server = await restlog.server.create(host=conf['host'],
                                             port=conf['port'],
                                             backend=backend)
        _bind_resource(async_group, server)

        await async_group.wait_closing()

    finally:
        await aio.uncancellable(async_group.async_close())


def _bind_resource(async_group, resource):
    async_group.spawn(aio.call_on_cancel, resource.async_close)
    async_group.spawn(aio.call_on_done, resource.wait_closing(),
                      async_group.close)


if __name__ == '__main__':
    sys.exit(main())
