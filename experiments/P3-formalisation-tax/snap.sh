#!/bin/sh
# Freeze the first-pass authoring of an item (before any differential feedback).
for i in "$@"; do
  d=items/$i; mkdir -p $d/first_pass
  for f in formalisation.ve environment.json bindings.json; do
    [ -f $d/$f ] && [ ! -f $d/first_pass/$f ] && cp $d/$f $d/first_pass/$f
  done
done
