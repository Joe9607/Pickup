#!/bin/bash
install=$1

if [ "${install}" == "install" ];then
	echo "--------------create virtualenv-----------------"
	rm -fR .pyenv
	virtualenv .pyenv
	echo "--------------pip install requirements----------"
	.pyenv/bin/pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

PYTHON='.pyenv/bin/python'
echo "PYTHON: ", ${PYTHON}

SUPERVISOR='.pyenv/bin/supervisord'
echo "SUPERVISOR: ", ${SUPERVIOSR}

# 生成supervisor配置文件
echo "--------------mahjong build---------------------"
# ${PYTHON} build.pyc --env=test
${PYTHON} build.py --env=test
${SUPERVISOR} -c confs/supervisor.conf
echo "--------------mahjong installed------------------"
