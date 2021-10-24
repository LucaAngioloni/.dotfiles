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

### Stow

Install [GNU stow](http://www.gnu.org/software/stow/).

Debian:

```bash
sudo apt-get install stow
```

OSX:

```bash
brew install stow
```

To install the dotfiles, first backup and remove all the dotfiles already there (otherwise stow will not work), then:

```bash
stow -R */
stow -D term # the term folder should not be stowed
```

## Sync

Use git
