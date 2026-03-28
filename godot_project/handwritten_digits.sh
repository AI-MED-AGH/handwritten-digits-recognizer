#!/bin/sh
printf '\033c\033]0;%s\a' handwritten_digits
base_path="$(dirname "$(realpath "$0")")"
"$base_path/handwritten_digits.x86_64" "$@"
