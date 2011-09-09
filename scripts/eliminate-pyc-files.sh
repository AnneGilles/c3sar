#!/bin/bash

echo "will delete all *.pyc files..." 
find . -name '*.pyc'

find . -name '*.pyc' -delete
echo "done."