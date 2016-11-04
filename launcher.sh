#!/bin/bash
# -*- coding: utf-8 -*-
# Description:
# Author: fkolacek@redhat.com
# Version: 0.9

while true; do

  LOGFILE="log-"$(date '+%d-%m-%Y-%H-%M-%S');
  ./iSecretary.py | tee ${LOGFILE}

  sleep 10
done

exit 0
