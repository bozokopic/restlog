from pathlib import Path
import sqlite3
import typing

from hat import aio
from hat import json


async def create(path: Path,
                 max_results: int
                 ) -> 'Backend':
    backend = Backend()
    backend._max_results = max_results
    backend._async_group = aio.Group()
    backend._executor = aio.create_executor(1)

    backend._db = await backend._executor(_ext_sqlite_connect, path)
    backend.async_group.spawn(aio.call_on_cancel, backend._executor,
                              _ext_sqlite_close, backend._db)

    return backend


class Backend(aio.Resource):

    @property
    def async_group(self):
        return self._async_group

    async def register(self,
                       timestamp: float,
                       address: str,
                       source: str,
                       type: str,
                       data: json.Data
                       ) -> json.Data:
        params = {'timestamp': timestamp,
                  'address': address,
                  'source': source,
                  'type': type,
                  'data': json.encode(data)}
        sql = ("INSERT INTO entries (timestamp, address, source, type, data) "
               "VALUES (:timestamp, :address, :source, :type, :data)")
        rowid = await self._executor(_ext_sqlite_execute, self._db, sql,
                                     params, False)

        params = {'rowid': rowid}
        sql = ("SELECT entry_id, timestamp, address, source, type, data "
               "FROM entries "
               "WHERE rowid = :rowid")
        result = await self._executor(_ext_sqlite_execute, self._db, sql,
                                      params)

        return _row_to_entry(result[0])

    async def get_entries(self,
                          source: typing.Optional[str] = None,
                          type: typing.Optional[str] = None,
                          last_entry_id: typing.Optional[int] = None,
                          max_results: typing.Optional[int] = None
                          ) -> json.Data:
        params = {}
        sql_conditions = []

        if source is not None:
            params['source'] = source
            sql_conditions.append('source = :source')

        if type is not None:
            params['type'] = type
            sql_conditions.append('type = :type')

        if last_entry_id is not None:
            params['last_entry_id'] = last_entry_id
            sql_conditions.append('entry_id <= :last_entry_id')

        if max_results is None or not (0 < max_results < self._max_results):
            max_results = self._max_results
        params['max_results'] = max_results

        sql_condition = (f"WHERE {' AND '.join(sql_conditions)}"
                         if sql_conditions else "")
        sql = (f"SELECT entry_id, timestamp, address, source, type, data "
               f"FROM entries "
               f"{sql_condition} "
               f"ORDER BY entry_id DESC "
               f"LIMIT :max_results")
        result = await self._executor(_ext_sqlite_execute, self._db, sql,
                                      params)

        return {'entries': [_row_to_entry(i) for i in result[:max_results]],
                'more': len(result) > max_results}

    async def get_entry(self, entry_id: int) -> typing.Optional[json.Data]:
        params = {'entry_id': entry_id}
        sql = ("SELECT entry_id, timestamp, address, source, type, data "
               "FROM entries "
               "WHERE entry_id = :entry_id")
        result = await self._executor(_ext_sqlite_execute, self._db, sql,
                                      params)

        return _row_to_entry(result[0]) if result else None


def _row_to_entry(row):
    return {'entry_id': row[0],
            'timestamp': row[1],
            'address': row[2],
            'source': row[3],
            'type': row[4],
            'data': json.decode(row[5])}


def _ext_sqlite_connect(db_path):
    db_path.parent.mkdir(exist_ok=True)
    db = sqlite3.connect(f'file:{db_path}?nolock=1', uri=True,
                         isolation_level=None,
                         detect_types=sqlite3.PARSE_DECLTYPES)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS entries (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            address TEXT,
            source TEXT,
            type TEXT,
            data TEXT);
    """)
    db.commit()
    return db


def _ext_sqlite_execute(db, sql, parameters, returns=True):
    c = db.execute(sql, parameters)
    return c.fetchall() if returns else c.lastrowid


def _ext_sqlite_close(db):
    db.close()
