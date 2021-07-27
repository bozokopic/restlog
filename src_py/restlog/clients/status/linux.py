from pathlib import Path
import asyncio
import contextlib
import subprocess
import sys
import time

import aiohttp
import click

from hat import aio


@click.command()
@click.option('--source', required=True)
@click.argument('addr')
def main(source: str, addr: str):
    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main(source, addr))


async def async_main(source: str, addr: str):
    url = f'{addr}/entry/{source}/builtin.status.linux'
    data = _get_data()

    async with aiohttp.ClientSession() as session:
        await session.post(url, json=data)


def _get_data():
    data = {'type': sys.platform,
            'timestamp': time.time()}

    if sys.platform == 'linux':
        data['uptime'] = _get_linux_uptime()
        data['thermal'] = list(_get_linux_thermal())
        data['disks'] = list(_get_linux_disks())

    return data


def _get_linux_uptime():
    return float(Path('/proc/uptime').read_text().split(maxsplit=1)[0])


def _get_linux_thermal():
    for i in Path('/sys/devices/virtual/thermal').glob('thermal_zone*'):
        yield {'type': (i / 'type').read_text().strip(),
               'temp': int((i / 'temp').read_text()) / 1000}


def _get_linux_disks():
    result = _run_with_output(['df', '-H', '-x', 'tmpfs', '-x', 'devtmpfs',
                               '--output=target,size,used,avail,pcent'])
    for line in result.split('\n')[1:]:
        if not line:
            continue
        segments = line.split()
        yield {'name': segments[0],
               'size': segments[1],
               'used': segments[2],
               'available': segments[3],
               'percent': segments[4]}


def _run_with_output(args):
    result = subprocess.run(args, capture_output=True, check=True)
    return result.stdout.decode('utf-8', errors='replace')


if __name__ == '__main__':
    sys.exit(main())
