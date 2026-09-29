#!/usr/bin/env bash
# Turn a git branch name into a Cloudflare Worker Preview name: lowercase letters, digits and
# dashes, starting with a letter, at most 30 characters. The name ends up in a DNS label
# (<preview-name>-<worker-name>.<account>.workers.dev, max 63 chars), so branch names like
# "Feature/Add_X" can't be used as they are.
#
# A short hash of the original name is appended when the slug had to be shortened, or when
# characters were dropped (non-ASCII names, e.g. Chinese branch names, would otherwise all
# collapse into the same slug). Names that only differ in punctuation or case (feature/x vs
# feature-x) still share a preview; that is rare enough to accept.
#
# usage: preview-name.sh <branch-name>
set -euo pipefail
export LC_ALL=C

ref="${1:?usage: preview-name.sh <branch-name>}"
max=30
needs_hash=0

slug="$(printf '%s' "$ref" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
if [ -z "$slug" ]; then
  slug="branch"
  needs_hash=1
fi
if printf '%s' "$ref" | grep -q '[^ -~]'; then
  needs_hash=1
fi
case "$slug" in
  [a-z]*) ;;
  *) slug="b-$slug" ;;
esac
if [ "${#slug}" -gt "$max" ]; then
  needs_hash=1
fi

if [ "$needs_hash" -eq 1 ]; then
  hash="$(printf '%s' "$ref" | sha1sum | cut -c1-6)"
  head="$(printf '%s' "${slug:0:$((max - 7))}" | sed -E 's/-+$//')"
  slug="$head-$hash"
fi

printf '%s\n' "$slug"
