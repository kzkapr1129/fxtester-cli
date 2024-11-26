#!/bin/zsh

baseDir="./taskfiles/env/darwin"

[[ -r $baseDir/anyenv/init.sh ]] && sh $baseDir/anyenv/init.sh

exit 0