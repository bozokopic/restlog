from pathlib import Path
import time

import aiohttp.web
import aiohttp_remotes

from hat import aio

from restlog import common
import restlog.backend


static_dir: Path = common.package_path / 'ui'


async def create(host: str,
                 port: int,
                 backend: restlog.backend.Backend
                 ) -> 'Server':
    server = Server()
    server._backend = backend
    server._async_group = aio.Group()

    app = aiohttp.web.Application()
    app.add_routes([
        aiohttp.web.get('/', server._get_root_handler),
        aiohttp.web.get('/entries', server._get_entries_handler),
        aiohttp.web.get('/entry/{entry_id}', server._get_entry_handler),
        aiohttp.web.post('/entry/{source}/{type}', server._post_entry_handler),
        aiohttp.web.static('/', static_dir)])
    await aiohttp_remotes.setup(app, aiohttp_remotes.XForwardedRelaxed())

    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    server.async_group.spawn(aio.call_on_cancel, runner.cleanup)

    try:
        site = aiohttp.web.TCPSite(runner=runner,
                                   host=host,
                                   port=port,
                                   shutdown_timeout=0.1,
                                   reuse_address=True)
        await site.start()

    except BaseException:
        await aio.uncancellable(server.async_group.async_close())
        raise

    return server


class Server(aio.Resource):

    @property
    def async_group(self):
        return self._async_group

    async def _get_root_handler(self, request):
        raise aiohttp.web.HTTPFound('/index.html')

    async def _get_entries_handler(self, request):
        source = request.query.get('source')
        type = request.query.get('type')
        last_entry_id = request.query.get('last_entry_id')
        max_results = request.query.get('max_results')

        last_entry_id = int(last_entry_id) if last_entry_id else None
        max_results = int(max_results) if max_results else None

        result = await self._backend.get_entries(source=source,
                                                 type=type,
                                                 last_entry_id=last_entry_id,
                                                 max_results=max_results)

        return aiohttp.web.json_response(result)

    async def _get_entry_handler(self, request):
        entry_id = int(request.match_info['entry_id'])
        entry = await self._backend.get_entry(entry_id)
        if entry is None:
            return aiohttp.web.Response(status=404)
        return aiohttp.web.json_response(entry)

    async def _post_entry_handler(self, request):
        timestamp = time.time()
        address = request.remote
        source = request.match_info['source']
        type = request.match_info['type']
        data = await request.json()

        entry = await self._backend.register(timestamp=timestamp,
                                             address=address,
                                             source=source,
                                             type=type,
                                             data=data)

        return aiohttp.web.json_response(entry)
