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
   # See correspondence table at the bottom of this answer

   *)
     PLATFORM='other'
     ;;
esac

source ~/.shellconfig/env