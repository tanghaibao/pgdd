#!/bin/bash

set -v
find usr/tmp_[0-5]* -mtime +2 -exec rm -f {} \;
find usr/tmp_[6-9]* -mtime +2 -exec rm -f {} \;
