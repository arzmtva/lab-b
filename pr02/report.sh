#!/bin/bash

if [ $# -lt 2 ]; then
    echo "Usage: $0 <directory> <ERROR|WARN> [--top N]"
    exit 1
fi

DIRECTORY="$1"
LEVEL="$2"
TOP=""

if [ ! -d "$DIRECTORY" ]; then
    echo "Error: directory '$DIRECTORY' does not exist."
    exit 1
fi

if [ "$LEVEL" != "ERROR" ] && [ "$LEVEL" != "WARN" ]; then
    echo "Error: level must be ERROR or WARN."
    exit 1
fi

if [ "$#" -eq 4 ]; then
    if [ "$3" != "--top" ]; then
        echo "Error: expected --top N."
        exit 1
    fi

    if ! [[ "$4" =~ ^[0-9]+$ ]] || [ "$4" -eq 0 ]; then
        echo "Error: N must be a positive number."
        exit 1
    fi

    TOP="$4"
elif [ "$#" -ne 2 ]; then
    echo "Usage: $0 <directory> <ERROR|WARN> [--top N]"
    exit 1
fi

echo "Module       Messages"
echo "---------------------"

grep -h -w "$LEVEL" "$DIRECTORY"/*.log 2>/dev/null |
    awk '{print $4}' |
    sort |
    uniq -c |
    sort -nr |
    if [ -n "$TOP" ]; then
        head -n "$TOP"
    else
        cat
    fi |
    awk '{printf "%-12s %d\n", $2, $1}'
