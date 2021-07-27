import pytest

import restlog.backend


pytestmark = pytest.mark.asyncio


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / 'restlog.db'


async def test_create(db_path):
    assert not db_path.exists()

    backend = await restlog.backend.create(db_path, 100)
    assert db_path.exists()

    await backend.async_close()
    assert db_path.exists()


async def test_register(db_path):
    backend = await restlog.backend.create(db_path, 100)

    result = await backend.get_entries()
    assert result == {'entries': [],
                      'more': False}

    entry = await backend.register(timestamp=123,
                                   address='address',
                                   source='source',
                                   type='type',
                                   data={'abc': 123})
    assert entry['entry_id'] is not None
    assert entry['timestamp'] == 123
    assert entry['address'] == 'address'
    assert entry['source'] == 'source'
    assert entry['type'] == 'type'
    assert entry['data'] == {'abc': 123}

    result = await backend.get_entry(entry['entry_id'])
    assert entry == result

    result = await backend.get_entries()
    assert result == {'entries': [entry],
                      'more': False}

    await backend.async_close()

    backend = await restlog.backend.create(db_path, 100)
    result = await backend.get_entry(entry['entry_id'])
    assert entry == result
    await backend.async_close()


@pytest.mark.parametrize('entries_count', [1, 2, 10])
async def test_get_entry(db_path, entries_count):
    backend = await restlog.backend.create(db_path, 100)

    result = await backend.get_entry(123)
    assert result is None

    entry_ids = []
    for _ in range(entries_count):
        entry = await backend.register(timestamp=123,
                                       address='address',
                                       source='source',
                                       type='type',
                                       data={'abc': 123})
        entry_ids.append(entry['entry_id'])

    for entry_id in entry_ids:
        result = await backend.get_entry(entry_id)
        assert result['entry_id'] == entry_id

    await backend.async_close()


@pytest.mark.parametrize('entries_count', [1, 2, 10])
async def test_get_entries(db_path, entries_count):
    backend = await restlog.backend.create(db_path, 100)

    result = await backend.get_entry(123)
    assert result is None

    entry_ids = []
    for i in range(entries_count):
        entry = await backend.register(timestamp=123,
                                       address='address',
                                       source=f'source{i}',
                                       type=f'type{i}',
                                       data={'abc': 123})
        entry_ids.append(entry['entry_id'])

    assert entry_ids == sorted(entry_ids)

    result = await backend.get_entries()
    assert ([i['entry_id'] for i in result['entries']] ==
            sorted(entry_ids, reverse=True))

    for i in range(entries_count):
        result = await backend.get_entries(source=f'source{i}')
        assert len(result['entries']) == 1
        assert result['entries'][0]['entry_id'] == entry_ids[i]

        result = await backend.get_entries(type=f'type{i}')
        assert len(result['entries']) == 1
        assert result['entries'][0]['entry_id'] == entry_ids[i]

        result = await backend.get_entries(last_entry_id=entry_ids[i])
        assert len(result['entries']) == 1 + i

    await backend.async_close()
