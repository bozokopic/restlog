import r from '@hat-core/renderer';
import * as u from '@hat-core/util';

import * as common from './common';


export function main() {
    const entries = r.get('entries');

    return ['div.main',
        ['table',
            ['thead',
                ['tr',
                    ['th.col-id', 'ID'],
                    ['th.col-time', 'Time'],
                    ['th.col-address', 'Address'],
                    ['th.col-source', 'Source'],
                    ['th.col-type', 'Type'],
                    ['th.col-data', 'Data']
                ]
            ],
            ['tbody', entries.map(entry =>
                ['tr',
                    ['td.col-id', String(entry.entry_id)],
                    ['td.col-time', common.timestampToString(entry.timestamp)],
                    ['td.col-address', String(entry.address)],
                    ['td.col-source', String(entry.source)],
                    ['td.col-type', String(entry.type)],
                    ['td.col-data', data(entry.type, entry.data)]
                ]
            )]
        ]
    ];
}


function data(type, data) {
    if (type == 'builtin.status.linux')
        return builtinStatusLinux(data);

    return JSON.stringify(data);
}


function builtinStatusLinux(data) {
    const timestamp = u.get('timestamp', data);
    const uptime = u.get('uptime', data);
    const thermal = u.get('thermal', data) || [];
    const disks = u.get('disks', data) || [];

    return ['div.data',
        ['label', 'Time:'],
        ['span', common.timestampToString(timestamp)],
        ['label', 'Uptime:'],
        ['span', `${uptime}s`],
        thermal.map(i => [
            ['label', `Temp - ${i.type}:`],
            ['span', `${i.temp}°C`]
        ]),
        disks.map(i => [
            ['label', `Disk - ${i.name}:`],
            ['span', `${i.percent} (${i.used}/${i.size})`]
        ]),
    ];
}
