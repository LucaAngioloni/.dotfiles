PLATFORM='none'

case "$(uname -s)" in
   Darwin)
     PLATFORM='mac'
     ;;

   Linux)
     PLATFORM='linux'
     ;;

   CYGWIN*|MINGW32*|MSYS*|MINGW*)
     PLATFORM='windows'
     ;;

   # Add here more strings to compare
   # See correspondence table at the bottom of this answer

   *)
     PLATFORM='other'
     ;;
esac

# These need to be sourced in order
source ~/.shellconfig/env
source ~/.shellconfig/oh-my-zsh

# Source aliases
for alias_file in ~/.shellconfig/alias/**/*(.); source $alias_file

# Source plugins
for plugin_file in ~/.shellconfig/plugins/**/*(.); source $plugin_file