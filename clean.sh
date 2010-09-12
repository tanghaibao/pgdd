#!/bin/bash

set -v
find usr/tmp* -mtime +2 -exec rm -f {} \;
