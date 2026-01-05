#!/bin/bash

export BLOCKMYDOUGH_DATA_DIR="$PWD/.dev"
mkdir -p "$BLOCKMYDOUGH_DATA_DIR"
uv run bmd