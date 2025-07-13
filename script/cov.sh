#! /bin/bash

source env/bin/activate

pytest --cov=. --cov-report=html

xdg-open htmlcov/index.html
