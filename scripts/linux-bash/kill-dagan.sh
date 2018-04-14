#!/usr/bin/env bash

kill $(ps -ef | grep [d]agan | awk '{print $2}')
