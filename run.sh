#!/usr/bin/env bash
# Kjør Villblomst direkte fra kildekoden.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec env PYTHONPATH="$DIR" python3 -m villblomst "$@"
