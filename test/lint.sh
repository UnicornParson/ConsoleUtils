#!/bin/bash
set -e
export LOCAL_D=$(dirname "$0")
export PyExe="python3"
pushd $LOCAL_D
echo "make env in $LOCAL_D"
$PyExe -m venv ./_venv
PYBIN=$LOCAL_D/_venv/bin
$PYBIN/pip3 install --upgrade pip
$PYBIN/pip3 install pylint
$PYBIN/pip3 install -r $LOCAL_D/../requirements_dry.txt
echo "make env - DONE"
popd

$PYBIN/pylint --rcfile=$LOCAL_D/../pylintrc $LOCAL_D/..