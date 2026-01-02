#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
python3 /opt/odoo/wait-for-psql.py db 5432

exec "$@"
