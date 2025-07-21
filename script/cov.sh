#! /bin/bash

source env/bin/activate

rm -r htmlcov/

pytest --cov=. --cov-report=html

xdg-open htmlcov/index.html
