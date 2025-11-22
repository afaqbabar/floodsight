#!/bin/sh
# Initialize PostGIS extension for FloodSight

set -e

# Wait for PostgreSQL to be ready
until psql -U postgres -c '\q'; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - installing PostGIS extension"

# Create PostGIS extension
psql -U postgres -d floodsight <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS postgis;
    SELECT PostGIS_Version();
EOSQL

echo "PostGIS extension installed successfully"

