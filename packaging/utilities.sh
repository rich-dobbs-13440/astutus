#!/usr/bin/env bash

# This file should be sourced, not called.

# Turn off echoing during defining these capabilities.  The output is not useful
# in the logs, and messes up identification of real errors

set +x

if [ "${BASH_VERSINFO:-0}" -lt 4 ]; then
    printf "DEBUG: Associative array usage requires 4 or greater."
    >&2 printf "\e[31mERROR: This script requires BASH to be greater than 4\e[0m\n"
    printf "\x1b[33m           On a Macintosh upgrade BASH by:\e[0m\n"
    printf "\x1b[33m                $ brew install bash\n"
    exit 203
fi


declare -A ANSI

    ANSI[RED]="\x1b[31m"
    ANSI[GREEN]="\x1b[32m"
    ANSI[YELLOW]="\x1b[33m"
    ANSI[BLUE]="\x1b[34m"
    ANSI[BOLD]="\x1b[1m"
    ANSI[RESET]='\e[0m'
    ANSI[ERROR]='\e[31m'
    ANSI[INFO]="\x1b[33m"
    ANSI[PLACEHOLDER]="\x1b[34m"



function mark_with_color() {
    set +x
    color=$1
    text=$2
    section_mark="---------------------------------------"
    printf "${color}${section_mark} ${text} ${section_mark}${ANSI[RESET]}\n";
    set -x
}

function mark_section() {
    set +x
    text=$1
    mark_with_color "${ANSI[YELLOW]}" "${text}"
    set -x
}

function mark_end_section() {
    set +x
    text=$1
    mark_with_color "${ANSI[YELLOW]}" "${ANSI[GREEN]}${text}${ANSI[YELLOW]}"
    set -x
}

function mark_sub_section() {
    set +x
    text=$1
    mark_with_color "${ANSI[BLUE]}" "${text}"
    set -x
}

function print_success() {
    text=$1
    printf "${ANSI[GREEN]}SUCCESS: ${text}${ANSI[RESET]}\n";
}

function print_error() {
    text=$1
    >&2 printf "${ANSI[ERROR]}${text}${ANSI[RESET]}\n"
}

function print_info() {
    text=$1
    printf "${ANSI[INFO]}${text}${ANSI['RESET']}\n"
}