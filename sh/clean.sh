#!/bin/bash


echo "cleaning $(pwd)"

echo "removing *.pyc"
find . -name '*.pyc' -print -exec rm {} \;

echo "removing lazertag.log"
rm lazertag.log
