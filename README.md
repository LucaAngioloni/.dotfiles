# .dotfiles

My configuration, with installations steps.

## Dependencies

Theese dotfiles only work on Unix systems.

You need to have **zsh** installed!

## Installation

Install using the [install script](install.sh):

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/LucaAngioloni/.dotfiles/main/install.sh)"
```

This will install all the dependencies, tools and dotfiles.

Note: the script will ask for your password to install some dependencies.

Note: still experimental!

## Sync

Use git to push and pull.

If the changes are on the existing files they should be applied immediately, otherwise if you add new "folders" or files, redo the Stow process.

### NEW! Use sup (Shell UPdate)

Use the `sup` command in the terminal to update the dotfiles and update all the dependencies and tools installed above.

## Manual installation

### Brew

On a Mac, install brew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Git

#### OSX

```bash
brew install git
```

#### Debian

```bash
sudo apt-get install git
```

### Oh My ZSH

Install with this command:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

Set ZSH as default shell

### ZSH Theme

To select which theme to use change `ZSH_THEME` in `shell/.shellconfig/oh-my-zsh`.
You can just install the one you need.

My current favourite is: **Powelevel10k**

#### Powelevel10k

Clone this repo:

```bash
git clone https://github.com/romkatv/powerlevel10k.git $ZSH_CUSTOM/themes/powerlevel10k
```

#### Spaceship

Clone this repo:

```bash
git clone https://github.com/spaceship-prompt/spaceship-prompt.git "$ZSH_CUSTOM/themes/spaceship-prompt" --depth=1
```

Symlink `spaceship.zsh-theme` to your oh-my-zsh custom themes directory:

```bash
ln -s "$ZSH_CUSTOM/themes/spaceship-prompt/spaceship.zsh-theme" "$ZSH_CUSTOM/themes/spaceship.zsh-theme"
```

#### Starship

Install Starship:

```bash
# MacOS
brew install starship

# Debian
curl -sS https://starship.rs/install.sh | sh
# Run this command again to update
```

### ZSH plugins

Install zsh-completions:

```bash
git clone https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM:=~/.oh-my-zsh/custom}/plugins/zsh-completions
```

Install zsh-autosuggestions:

```bash
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
```

<!-- Install zsh-syntax-highlighting:

```bash
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
``` -->

Install fast-syntax-highlighting:

```bash
git clone https://github.com/zdharma-continuum/fast-syntax-highlighting.git \
  ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/fast-syntax-highlighting
```

Choose a theme with `fast-theme {theme-name}`.

List all themes with `fast-theme -l`.

Run `fast-theme -t {theme-name}` option to obtain a snippet.

I use `default` but I am not super happy with it.

### Tmux

#### OSX

```bash
brew install tmux
```

#### Debian

```bash
sudo apt-get install tmux
```s

### Ruby (mainly for colorls)

#### OSX

```bash
brew install ruby
```

#### Debian

```bash
sudo snap install ruby --classic
```

### Color LS

Requires ruby.

Install gem:

```bash
gem install colorls
```

### The Fuck

#### OSX

```bash
brew install thefuck
```

#### Debian

Requires Python.

```bash
pip3 install thefuck --user
```

### fd

#### OSX

```bash
brew install fd
```

#### Debian

```bash
sudo apt install fd-find

# If fd is not available in PATH (because it is called fdfind)
ln -s $(which fdfind) ~/.local/bin/fd
```

or refer to the [documentation](https://github.com/sharkdp/fd#installation)

### Tree

#### OSX

```bash
brew install tree
```

#### Debian

```bash
sudo apt-get install tree
```

### Bat

#### OSX

```bash
brew install bat
```

#### Debian

```bash
sudo apt-get install bat

# If bat is not available and it is instead batcat
mkdir -p ~/.local/bin
ln -s /usr/bin/batcat ~/.local/bin/bat
```

or refer to the [documentation](https://github.com/sharkdp/bat#installation)

### FZF

#### OSX

```bash
brew install fzf

# To install useful key bindings and fuzzy completion (run once):
$(brew --prefix)/opt/fzf/install
```

##### Uninstall

```bash
$(brew --prefix)/opt/fzf/uninstall

brew uninstall fzf
```

#### Debian

```bash
sudo apt-get install fzf
```

Add `~/.fzf.zsh` with this:

```bash
# Auto-completion
# ---------------
source /usr/share/doc/fzf/examples/completion.zsh

# Key bindings
# ------------
source /usr/share/doc/fzf/examples/key-bindings.zsh
```

### Direnv

#### OSX

```bash
brew install direnv
```

##### Uninstall

```bash
brew uninstall direnv
```

#### Debian

```bash
sudo apt-get install direnv
```

### Catimg

#### OSX

```bash
brew install catimg
```

#### Debian

```bash
sudo apt-get install catimg
```

### Stow

Install [GNU stow](http://www.gnu.org/software/stow/).

#### Debian

```bash
sudo apt-get install stow
```

#### OSX

```bash
brew install stow
```

### Install dotfiles in your system

To install the dotfiles, first backup and remove all the dotfiles already there (otherwise stow will not work), then:

```bash
stow -R */
```

## iTerm 2

On Mac use iTerm2. Themes and configurations are in the `term` folder.

In iTerm2 go to *Preferences* and then *General* and click on *Load preferences from a custom folder or URL* and select the `com.googlecode.iterm2.plist` file.

### Speedup

Installing **git** with brew instead of using the **Apple git** seems to speed things a little.

Also accepting the terms of the xcodebuild licence seems to help: `sudo xcodebuild -license accept`.

To make startup faster set in the *General* tab of *Profile* in *Command*:

**Command**: `/usr/local/bin/zsh -i`

This should completely skip the login phase.

#### Old config

To make startup faster set in the *General* tab of *Profile* in *Command*:

**Command**: `login -fq lucaangioloni /usr/local/bin/zsh -il`

This serves 2 purposes:

- Start zsh in **interactive** and **login** mode with `-il`.
- Do not show last login information with `-q` (same effect as `.hushlogin` but it seems faster because it does not even go to search the logs to find the last login event. (? check this info)).

## Optional tools

### Notable Python packages

```bash
pip install \
autopep8 \
black \
cookiecutter \
flake8 \
get-files-list \
httpie \
ipython \
jupyterlab \
matplotlib \
numpy \
opencv-python \
pandas \
Pillow \
pip-tools \
pyinstaller \
requests \
rich \
scikit-learn \
scipy \
tqdm \
virtualenv
```

### Notable NPM packages

```bash
npm install -g \
share-cli \
trash-cli \
tldr \
firebase-tools \
yarn \
prettier \
eslint \
jsdoc \
browser-sync \
npm-check-updates \
speed-test \
http-server-with-auth
```

### Show images in terminal

Repo: https://github.com/hackerb9/lsix
change configuration in the lsix script:

```bash
# The following defaults may be overridden if autodetection succeeds.
numcolors=16     # Default number of colors in the palette.
background=white # Default montage background.
foreground=black # Default text color.
width=1200	 # Default width of screen in pixels.

# Feel free to edit these defaults to your liking.
tilesize=300	       # Width and height of each tile in the montage.
tilewidth=$tilesize    # (or specify separately, if you prefer)
tileheight=$tilesize

# If you get questionmarks for Unicode filenames, try using a different font.
# You can list fonts available using `convert -list font`.
#fontfamily=Droid-Sans-Fallback		# Great Asian font coverage
#fontfamily=Dejavu-Sans			# Wide coverage, comes with GNU/Linux
#fontfamily=Mincho			# Wide coverage, comes with MS Windows

# Default font size is based on width of each tile in montage.
fontsize=$((tilewidth/10))
#fontsize=16		     # (or set the point size directly, if you prefer)

timeout=0.25		    # How long to wait for terminal to respond
			    # to a control sequence (in seconds).
```
