# .dotfiles

My configuration, with installations steps.

## Installation

### Oh My ZSH

Install with this command:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

Set ZSH as default shell

### ZSH Theme

#### Spaceship theme

Clone this repo:

```bash
git clone https://github.com/spaceship-prompt/spaceship-prompt.git "$ZSH_CUSTOM/themes/spaceship-prompt" --depth=1
```

Symlink `spaceship.zsh-theme` to your oh-my-zsh custom themes directory:

```bash
ln -s "$ZSH_CUSTOM/themes/spaceship-prompt/spaceship.zsh-theme" "$ZSH_CUSTOM/themes/spaceship.zsh-theme"
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

Install zsh-syntax-highlighting:

```bash
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
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
```

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

## Sync

Use git to push and pull.

If the changes are on the existing files they should be applied immediately, otherwise if you add new "folders" or files, redo the Stow process.
