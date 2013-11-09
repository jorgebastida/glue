#!/bin/bash
rm -R htmlcov
coverage run --source=glue setup.py test
coverage html
