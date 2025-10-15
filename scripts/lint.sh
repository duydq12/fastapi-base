#!/bin/bash

set -eux

ruff check src tests

typos src tests
