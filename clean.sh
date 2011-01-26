#!/bin/bash

set -v

for i in {0..9}
    do
        find /home/bao/duplication/usr/tmp_${i}* -mtime +2 -exec rm -f {} \;
    done
