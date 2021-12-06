#! /usr/bin/env bash

set -euxo pipefail
DAY=$1

cd "$(git rev-parse --show-toplevel)"
cp -r template $DAY
cd $DAY

mv template.py $DAY.py
sed -i "s/PLACEHOLDER/$DAY/" Makefile
