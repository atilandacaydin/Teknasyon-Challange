#!/bin/bash

host=${POSTGRES_HOST}
port=${POSTGRES_PORT}

until nc -z -v -w30 $host $port; do
  echo "Waiting for PostgreSQL to be available at $host:$port..."
  sleep 5
done

echo "PostgreSQL is up!"
sleep 2
exec "$@"
