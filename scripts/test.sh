#!/bin/bash

set -eux

pytest --cov=src --cov-report=term-missing --cov-report=xml tests/
