# Old bash configuration when I started programming.

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

if [ "$PLATFORM"  = 'mac' ]; then
    # This is needed because MacOS automatically sources /etc/zprofile
    # where the command /usr/libexec/path_helper is called.
    # This overrides the PATH set in zshenv and changes the order of the paths.
    # This script fixes that resorting the paths like intended.
    source ~/.shellconfig/fix-path-mac
fi

eval "$(starship init bash)"

# Source aliases
for alias_file in ~/.shellconfig/alias/*; do
source "$alias_file"
done

# Source plugins
for plugin_file in ~/.shellconfig/plugins/*; do
source "$plugin_file"
done

# Source functions
for function_file in ~/.functions/*; do
source "$function_file"
done