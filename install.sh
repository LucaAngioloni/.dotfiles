#!/bin/zsh
#
# This script should be run via curl:
#   zsh -c "$(curl -fsSL https://raw.githubusercontent.com/LucaAngioloni/.dotfiles/main/install.sh)"
# or via wget:
#   zsh -c "$(wget -qO- https://raw.githubusercontent.com/LucaAngioloni/.dotfiles/main/install.sh)"
# or via fetch:
#   zsh -c "$(fetch -o - https://raw.githubusercontent.com/LucaAngioloni/.dotfiles/main/install.sh)"
#
# As an alternative, you can first download the install script and run it afterwards:
#   wget https://raw.githubusercontent.com/LucaAngioloni/.dotfiles/main/install.sh
#   zsh install.sh
set -e

# Make sure important variables exist if not already defined
#
# $USER is defined by login(1) which is not always executed (e.g. containers)
# POSIX: https://pubs.opengroup.org/onlinepubs/009695299/utilities/id.html
USER=${USER:-$(id -u -n)}
# $HOME is defined at the time of login, but it could be unset. If it is unset,
# a tilde by itself (~) will not be expanded to the current user's home directory.
# POSIX: https://pubs.opengroup.org/onlinepubs/009696899/basedefs/xbd_chap08.html#tag_08_03
HOME="${HOME:-$(getent passwd $USER 2>/dev/null | cut -d: -f6)}"
# macOS does not have getent, but this works even if $HOME is unset
HOME="${HOME:-$(eval echo ~$USER)}"

PLATFORM='none'

case "$(uname -s)" in
   Darwin)
     PLATFORM='mac'
     ;;

   Linux)
     PLATFORM='linux'
     ;;

   *)
     PLATFORM='other'
     ;;
esac

if [ "$PLATFORM"  = 'other' ]; then
    echo "Cannot install on this platform!"
    exit 1
fi

command_exists() {
  command -v "$@" >/dev/null 2>&1
}

user_can_sudo() {
  # Check if sudo is installed
  command_exists sudo || return 1
  # The following command has 3 parts:
  #
  # 1. Run `sudo` with `-v`. Does the following:
  #    • with privilege: asks for a password immediately.
  #    • without privilege: exits with error code 1 and prints the message:
  #      Sorry, user <username> may not run sudo on <hostname>
  #
  # 2. Pass `-n` to `sudo` to tell it to not ask for a password. If the
  #    password is not required, the command will finish with exit code 0.
  #    If one is required, sudo will exit with error code 1 and print the
  #    message:
  #    sudo: a password is required
  #
  # 3. Check for the words "may not run sudo" in the output to really tell
  #    whether the user has privileges or not. For that we have to make sure
  #    to run `sudo` in the default locale (with `LANG=`) so that the message
  #    stays consistent regardless of the user's locale.
  #
  ! LANG= sudo -n -v 2>&1 | grep -q "may not run sudo"
}

user_can_sudo || {
    echo "You don't have sudo privileges. Please run this script as root."
    exit 2
}

# Load colors
autoload colors; colors

# Adding paths to PATH before installing tools so that I can use them right away
export PATH

export PATH=~/.bin:$PATH
export PATH=~/.local/bin:$PATH

if [ "$PLATFORM"  = 'mac' ]; then
    export PATH=$HOME/bin:/usr/local/bin:$PATH
    export PATH="/usr/local/sbin:$PATH"

    #Ruby
    export PATH="/usr/local/opt/ruby/bin:$PATH"
elif [ "$PLATFORM"  = 'linux' ]; then
    export PATH=~/.gem/bin:$PATH # Ruby gems if installed with snap
fi

# Installing basic tools
if [ "$PLATFORM"  = 'mac' ]; then
    if ! command_exists brew; then
        echo $fg[green]"Installing Homebrew..."$reset_color
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo ""
    fi

    echo $fg[green]"Updating Homebrew Formulae..."$reset_color
    brew update
    echo ""

    # Install with brew even though it's already installed by default on macOS. Brew's version is faster.
    echo $fg[green]"Installing git..."$reset_color
    brew install git
    echo ""
elif [ "$PLATFORM"  = 'linux' ]; then
    echo $fg[green]"Updating Aptic Packages..."$reset_color
    sudo apt-get update -y

    if ! command_exists git; then
        echo $fg[green]"Installing git..."$reset_color
        sudo apt-get install git -y
        echo ""
    fi
fi

# Install Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
echo ""

# Change the default shell to zsh
echo $fg[green]"Changing the default shell to zsh..."$reset_color
chsh -s $(which zsh)
echo ""

source ~/.zshrc

if [ ! -d "$ZSH_CUSTOM/themes/powerlevel10k" ]; then
    echo $fg[green]"Installing Powerlevel10k..."$reset_color
    git clone https://github.com/romkatv/powerlevel10k.git $ZSH_CUSTOM/themes/powerlevel10k
    echo ""
fi

if [ ! -d "$ZSH_CUSTOM/plugins/zsh-completions" ]; then
    echo $fg[green]"Installing zsh-completions..."$reset_color
    git clone https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM:=~/.oh-my-zsh/custom}/plugins/zsh-completions
    echo ""
fi

if [ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
    echo $fg[green]"Installing zsh-autosuggestions..."$reset_color
    git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
    echo ""
fi

if [ ! -d "$ZSH_CUSTOM/plugins/fast-syntax-highlighting" ]; then
    echo $fg[green]"Installing fast-syntax-highlighting..."$reset_color
    git clone https://github.com/zdharma-continuum/fast-syntax-highlighting.git \
    ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/fast-syntax-highlighting
    echo ""
fi

if [ "$PLATFORM"  = 'mac' ]; then
    # Starship install
    # echo $fg[green]"Installing Starship..."$reset_color
    # brew install starship
    # echo ""

    # Install thefuck
    echo $fg[green]"Installing thefuck..."$reset_color
    brew install thefuck
    echo ""

    # Install fd
    echo $fg[green]"Installing fd..."$reset_color
    brew install fd
    echo ""

    # Install tree
    echo $fg[green]"Installing tree..."$reset_color
    brew install tree
    echo ""

    # Install bat
    echo $fg[green]"Installing bat..."$reset_color
    brew install bat
    echo ""

    # Install fzf
    echo $fg[green]"Installing fzf..."$reset_color
    brew install fzf
    # To install useful key bindings and fuzzy completion (run once):
    $(brew --prefix)/opt/fzf/install
    echo ""

    # Install direnv
    echo $fg[green]"Installing direnv..."$reset_color
    brew install direnv
    echo ""

    # Install catimg
    echo $fg[green]"Installing catimg..."$reset_color
    brew install catimg
    echo ""

    # Install stow
    echo $fg[green]"Installing stow..."$reset_color
    brew install stow
    echo ""

    # Install tmux
    echo $fg[green]"Installing tmux..."$reset_color
    brew install tmux
    echo ""

    # Install ruby
    echo $fg[green]"Installing ruby..."$reset_color
    brew install ruby
    echo ""
fi
if [ "$PLATFORM"  = 'linux' ]; then
    mkdir -p ~/.local/bin # For fd and bat

    # Starship install
    # echo $fg[green]"Installing Starship..."$reset_color
    # curl -sS https://starship.rs/install.sh | sh
    # echo ""

    # Install thefuck
    if ! command_exists pip3; then
        echo $fg[green]"Installing pip3..."$reset_color
        sudo apt-get install python3-pip -y
        echo ""
    fi

    echo $fg[green]"Installing thefuck..."$reset_color
    pip3 install thefuck --upgrade
    echo ""

    # Install fd
    echo $fg[green]"Installing fd..."$reset_color
    sudo apt-get install fd-find -y
    ln -s $(which fdfind) ~/.local/bin/fd || true
    echo ""

    # Install tree
    echo $fg[green]"Installing tree..."$reset_color
    sudo apt-get install tree -y
    echo ""

    # Install bat
    echo $fg[green]"Installing bat..."$reset_color
    sudo apt-get install bat -y
    ln -s /usr/bin/batcat ~/.local/bin/bat || true
    echo ""

    # Install fzf
    echo $fg[green]"Installing fzf..."$reset_color
    sudo apt-get install fzf -y
    cat << EOF > ~/.fzf.zsh
# Auto-completion
# ---------------
source /usr/share/doc/fzf/examples/completion.zsh

# Key bindings
# ------------
source /usr/share/doc/fzf/examples/key-bindings.zsh
EOF
    echo ""

    # Install direnv
    echo $fg[green]"Installing direnv..."$reset_color
    sudo apt-get install direnv -y
    echo ""

    # Install catimg
    echo $fg[green]"Installing catimg..."$reset_color
    sudo apt-get install catimg -y
    echo ""

    # Install stow
    echo $fg[green]"Installing stow..."$reset_color
    sudo apt-get install stow -y
    echo ""

    # Install tmux
    echo $fg[green]"Installing tmux..."$reset_color
    sudo apt-get install tmux -y
    echo ""

    # Install ruby
    echo $fg[green]"Installing ruby..."$reset_color
    # Install with snap
    sudo snap install ruby --classic
    echo ""
fi

# Install colorls
echo $fg[green]"Installing colorls..."$reset_color
gem install colorls
echo ""

echo $fg[green]"Installing .dotfiles..."$reset_color
git clone https://github.com/LucaAngioloni/.dotfiles.git ~/.dotfiles
if [ -f ~/.zshrc ]; then
    mv ~/.zshrc ~/.zshrc.bak
fi
if [ -f ~/.zshenv ]; then
    mv ~/.zshenv ~/.zshenv.bak
fi
if [ -f ~/.zprofile ]; then
    mv ~/.zprofile ~/.zprofile.bak
fi
if [ -f ~/.bashrc ]; then
    mv ~/.bashrc ~/.bashrc.bak
fi

# TODO: do the same thing for every file in the .dotfiles folder that we want to backup before stowing

cd ~/.dotfiles
stow --adopt */ # Stow all the folders in the .dotfiles folder
git restore .
echo ""

cd
exec zsh -l