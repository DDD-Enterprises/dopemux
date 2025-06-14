# Base
PROMPT='%F{117}➜%f %F{80}%~%f '

# Git
ZSH_THEME_GIT_PROMPT_PREFIX="%F{81}git:(%f"
ZSH_THEME_GIT_PROMPT_SUFFIX="%F{81})%f"
ZSH_THEME_GIT_PROMPT_DIRTY="%F{204}*%f"
ZSH_THEME_GIT_PROMPT_CLEAN=""

# Python virtualenv
virtualenv_info() {
  [ -n "$VIRTUAL_ENV" ] && echo "%F{111}(`basename $VIRTUAL_ENV`)%f "
}
RPROMPT='$(virtualenv_info)%F{139}%D{%H:%M}%f'
