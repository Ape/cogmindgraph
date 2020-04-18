#!/bin/sh

DEST=cogmindgraph/gen
mkdir -p $DEST
protoc --python_out=$DEST -I proto proto/archived_scoresheet.proto proto/cogmind-scoresheet/scoresheet.proto

# Workaround https://github.com/protocolbuffers/protobuf/issues/1491
touch $DEST/__init__.py
2to3 -wn -f import --no-diffs $DEST/archived_scoresheet_pb2.py
