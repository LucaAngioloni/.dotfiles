# shellcheck disable=SC2148

[ -z "$ZPROF" ] || zmodload zsh/zprof

export MY_LS_COMMAND="colorls"

setopt APPEND_HISTORY # append to the history file instead of overwriting it
# setopt INC_APPEND_HISTORY SHARE_HISTORY  # adds history incrementally and share it across sessions
setopt HIST_IGNORE_ALL_DUPS  # don't record dupes in history
setopt HIST_REDUCE_BLANKS # remove leading/trailing blanks from history lines
setopt HIST_IGNORE_SPACE # ignore commands that start with a space

# These need to be sourced in order
if [ "$PLATFORM"  = 'mac' ]; then
    # This is needed because MacOS automatically sources /etc/zprofile
    # where the command /usr/libexec/path_helper is called.
    # This overrides the PATH set in zshenv and changes the order of the paths.
    # This script fixes that resorting the paths like intended.
    source ~/.shellconfig/fix-path-mac
fi

source ~/.shellconfig/oh-my-zsh

# Set word splitting to be more like bash, i.e. split on spaces and newlines
# https://github.com/ohmyzsh/ohmyzsh/wiki/FAQ#kill-word-or-backward-kill-word-do--dont-delete-a-symbol-wordchars
# export WORDCHARS='*?_-.[]~=/&;!#$%^(){}<>'
# export WORDCHARS='*?_-[]~=/&;!#$%^(){}<>'
export WORDCHARS='*?_-[]~&;!#$%^(){}<>"'\'

# Source aliases
for alias_file in ~/.shellconfig/alias/***/*; source "$alias_file"

# Source plugins
for plugin_file in ~/.shellconfig/plugins/***/*; source "$plugin_file"

# Autoload functions
fpath=(~/.functions $fpath)
autoload -Uz ~/.functions/*(.:t)

for function_folder in ~/.functions/*(/); do
    fpath=($function_folder $fpath);
    autoload -Uz $function_folder/*(.:t);
done;

[ -z "$ZPROF" ] || zprof