#!/bin/bash

set -v
find usr/*.??? -mtime +2 -exec rm -f {} \;
