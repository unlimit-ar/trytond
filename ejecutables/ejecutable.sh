#!/bin/sh
export PYENV_ROOT="/home/mimismo/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
export TRYTOND_CONFIG="/home/mimismo/trytond/trytond.conf"
eval "$(pyenv init -)"

cd /home/mimismo/trytond
pyenv activate tryton64
exec gunicorn trytond-app -c /home/mimismo/trytond/gunicorn.conf.py
