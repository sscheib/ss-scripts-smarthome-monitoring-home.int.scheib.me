#!/bin/bash
declare ip="${1}"
declare endpoint="${2}"
/usr/local/bin/lg_soundbar_query.py --ip "${ip}" --endpoint "${endpoint}"
