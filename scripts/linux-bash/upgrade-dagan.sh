#!/usr/bin/env bash

cd /opt/dagan

cp .venv/lib/python*/site-packages/dagan/resources/dagan.db db-bup/$(date +"%Y-%m-%d-%H-%M-%S").db
cp .venv/lib/python*/site-packages/dagan/resources/dagan.db /tmp/dagan.db
.venv/bin/pip uninstall -y dagan
.venv/bin/pip install dagan*.whl
cp /tmp/dagan.db .venv/lib/python*/site-packages/dagan/resources/dagan.db
mv dagan*.whl dist/
