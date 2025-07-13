#! /bin/bash

rm -r htmlcov/

pytest -q --disable-warnings
