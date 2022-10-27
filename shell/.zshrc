# These need to be sourced in order
source ~/.shellconfig/oh-my-zsh

# Source aliases
for alias_file in ~/.shellconfig/alias/**/*; source $alias_file

# Source plugins
for plugin_file in ~/.shellconfig/plugins/**/*; source $plugin_file
