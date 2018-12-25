#!/bin/bash
echo "--------------mahjong build---------------------"
pwd
echo "--------------create virtualenv-----------------"
rm -fR .pyenv
virtualenv .pyenv
echo "--------------pip install requirements----------"
.pyenv/bin/pip install -r requirements.txt -i http://source.supernanogame.com:81/pypi/simple --trusted-host source.supernanogame.com

PYTHON='.pyenv/bin/python'
echo "PYTHON: ", ${PYTHON}
SUPERVISOR='.pyenv/bin/supervisord'
echo "SUPERVISOR: ", ${SUPERVIOSR}

# 生成supervisor配置文件
${PYTHON} build.pyc --env=test
${SUPERVISOR} -c confs/supervisor.conf
echo "--------------mahjong installed------------------"