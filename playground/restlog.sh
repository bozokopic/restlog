#!/bin/sh

. $(dirname -- "$0")/env.sh

LOG_LEVEL=DEBUG
CONF_PATH=$DATA_PATH/restlog.yaml
DB_PATH=$DATA_PATH/restlog.db

cat > $CONF_PATH << EOF
log:
    version: 1
    formatters:
        console_formatter:
            format: "[%(asctime)s %(levelname)s %(name)s] %(message)s"
    handlers:
        console_handler:
            class: logging.StreamHandler
            formatter: console_formatter
            level: DEBUG
    loggers:
        hat.monitor:
            level: $LOG_LEVEL
    root:
        level: INFO
        handlers: ['console_handler']
    disable_existing_loggers: false
host: '127.0.0.1'
port: 23233
db_path: $DB_PATH
max_results: 100
EOF

exec $PYTHON -m restlog --conf $CONF_PATH "$@"
