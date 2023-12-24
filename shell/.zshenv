# shellcheck disable=SC2148

# Skip the not really helping Ubuntu global compinit
skip_global_compinit=1
# Speed up.

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

   *)
     PLATFORM='other'
     ;;
esac

# Source envs
for env_file in ~/.shellconfig/envs/***/*; source "$env_file"