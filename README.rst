restlog
=======

JSON log-structured data storage with REST API.


About
-----

`restlog` provides simple data storage with REST access for registering
and retrieving arbitrary JSON data. During data registration, additional
meta-data is associated with each entry:

    * `entry_id`

        Number uniquely identifying each entry. This number is generated
        by `restlog` and provides monotonously rising sequence used for
        determining order of entry registrations.

    * `timestamp`

        Timestamp representing point in time when `restlog` obtained
        registration request.

    * `address`

        IP address, as seen by `restlog`, of client initiating registration
        request. `restlog` will try to use ``X-Forwarded-*`` HTTP header values
        provided by reverse proxy.

    * `source`

        String label, set by client, used for filtering and additional
        identification of client instance.

    * `type`

        String label, set by client, used for filtering and additional
        identification of data structure/semantics.

    * `data`

        Arbitrary JSON data.

Registered entries can be obtained based on optional query parameters
`last_entry_id`, `source` and `type`. If `last_entry_id` is not specified,
resulting entries will contain "newest" entries (entries with greatest
`entry_id` number). If `last_entry_id` is specified, resulting entries will
have `entry_id` less or equal to specified `last_entry_id`. Entry retrieval
results always contain lists of entries ordered by `entry_id` where "latest"
entries (entries with greater `entry_id`) are first and "oldest" entries are
last.

Together with REST API, `restlog` provides simple web-based view of data
available through REST API.


Runtime requirements
--------------------

* python >=3.8


Install
-------

::

    $ pip install restlog


Configuration
-------------

Configuration structure is defined by `JSON schema <schemas_json/main.yaml>`_ .

Example::

    log:
        version: 1
    host: '127.0.0.1'
    port: 23233
    db_path: restlog.db
    max_results: 100


Run
---

::

    $ restlog [--conf restlog.yaml]

If path to configuration file is not set, default configuration path
``$XDG_CONFIG_HOME/restlog/restlog.{yaml|yml|json}`` is assumed.

Once `restlog` is running, web-based data view can be accessed on
`http://<host>:<port>` (`<host>` and `<port>` are defined by configuration
parameters).


REST API
--------

REST API is defined by `Open API schema <schemas_openapi/main.yaml>`_ .

Available endpoints:

    * POST ``/entry/{source}/{type}``

        Registration of single entry with JSON data provided as content
        of HTTP request body.

    * GET ``/entries?source={source}&type={type}&last_entry_id={last_entry_id}&max_results={max_results}``

        Multiple entry retrieval. All query parameters are optional.
        HTTP response contains list of entries and `more` flag indicating
        if more entries, satisfying provided filters, are available.

    * GET ``/entry/{entry_id}``

        Single entry retrieval.


Security
--------

If `restlog` is used by clients not running on the same machine, reverse
proxy with additional authentication methods should be used. Additionally,
`X-Forward-*` header entries should be included.

Example of `nginx <https://nginx.org/>`_ configuration::

    location / {
        proxy_pass        http://127.0.0.1:23233;
        proxy_set_header  X-Real-IP $remote_addr;
        proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header  X-Forwarded-Proto $scheme;

        auth_basic            "restlog";
        auth_basic_user_file  /etc/nginx/restlog.htpasswd;
    }


License
-------

restlog - JSON log-structured data storage with REST API

Copyright (C) 2021 Bozo Kopic

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
