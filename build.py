# coding: utf-8

import os
import compileall
from ConfigParser import ConfigParser

root = os.getcwd()
compileall.compile_dir(root, ddir=".", force=1, quiet=1)
#print root


def supervisor():
    conf_d = os.path.join(os.path.join(root, "confs"), "conf.d")
    # 先删除之前生成的配置文件
    if os.path.exists(conf_d):
        for i in os.listdir(conf_d):
            os.remove(os.path.join(conf_d, i))
    # 生成supervisor conf文件
    conf = ConfigParser()
    # 生成主配置文件
    section_unix_http_server = "unix_http_server"
    conf.add_section(section_unix_http_server)
    conf.set(section_unix_http_server, "file", os.path.join(root, "mahjong.sock"))
    conf.set(section_unix_http_server, "username", "mahjong")
    conf.set(section_unix_http_server, "password", "supernano2016")

    section_supervisord = "supervisord"
    conf.add_section(section_supervisord)
    conf.set(section_supervisord, "logfile", os.path.join(root, "log/supervisor.log"))
    conf.set(section_supervisord, "logfile_maxbytes", "100MB")
    conf.set(section_supervisord, "logfile_backups", "30")
    conf.set(section_supervisord, "loglevel", "INFO")
    conf.set(section_supervisord, "pidfile", "mahjong.pid")
    conf.set(section_supervisord, "directory", root)

    section_supervisorctl = "supervisorctl"
    conf.add_section(section_supervisorctl)
    conf.set(section_supervisorctl, "serverurl", "unix://" + os.path.join(root, "mahjong.sock"))
    conf.set(section_supervisorctl, "username", "mahjong")
    conf.set(section_supervisorctl, "password", "supernano2016")

    section_rpc = "rpcinterface:supervisor"
    conf.add_section(section_rpc)
    conf.set(section_rpc, "supervisor.rpcinterface_factory", "supervisor.rpcinterface:make_main_rpcinterface")

    section_include = "include"
    conf.add_section(section_include)
    conf.set(section_include, "files", os.path.join(root, "confs/conf.d/*.conf"))

    conf_path = os.path.join(os.path.join(root, "confs"), "supervisor.conf")
    with open(conf_path, "wb") as fp:
        conf.write(fp)

    conf_system = ConfigParser()
    conf_system.read(os.path.join(os.path.join(root, "confs"), "system.conf"))
    for s in conf_system.sections():
        kwargs = dict(conf_system.items(s))

        section = "program:server_{0}".format(s)
        conf = ConfigParser()
        conf.add_section(section)
        conf.set(section, "command", ".pyenv/bin/python server.pyc --server_port={server_port} "
                                     "--logger_port={logger_port} --redis_host={redis_host} "
                                     "--redis_port={redis_port} --redis_password={redis_password} "
                                     "--redis_db={redis_db}".format(**kwargs))
        conf.set(section, "process_name", "%(program_name)s")
        conf.set(section, "autostart", "true")
        conf.set(section, "startsecs", 5)
        conf.set(section, "startretries", 5)
        conf.set(section, "autorestart", "true")
        conf.set(section, "redirect_stderr", "true")
        conf.set(section, "stdout_logfile", os.path.join(root, "log/%(program_name)s.out"))
        conf.set(section, "stdout_logfile_maxbytes", "50MB")
        conf.set(section, "stdout_logfile_backups", 5)
        conf.set(section, "stderr_logfile", os.path.join(root, "log/%(program_name)s.err"))
        conf.set(section, "stderr_logfile_maxbytes", "50MB")
        conf.set(section, "stderr_logfile_backups", 5)

        section = "program:logger_{0}".format(s)
        conf.add_section(section)
        conf.set(section, "command", ".pyenv/bin/python logger.pyc --logger_port={logger_port} "
                                     "--redis_host={redis_host} --redis_port={redis_port} "
                                     "--redis_password={redis_password} --redis_db={redis_db}".format(**kwargs))
        conf.set(section, "process_name", "%(program_name)s")
        conf.set(section, "autostart", "true")
        conf.set(section, "startsecs", 5)
        conf.set(section, "startretries", 5)
        conf.set(section, "autorestart", "true")
        conf.set(section, "redirect_stderr", "true")
        conf.set(section, "stdout_logfile", os.path.join(root, "log/%(program_name)s.out"))
        conf.set(section, "stdout_logfile_maxbytes", "50MB")
        conf.set(section, "stdout_logfile_backups", 5)
        conf.set(section, "stderr_logfile", os.path.join(root, "log/%(program_name)s.err"))
        conf.set(section, "stderr_logfile_maxbytes", "50MB")
        conf.set(section, "stderr_logfile_backups", 5)

        conf_path = os.path.join(os.path.join(root, "confs"), "conf.d")
        if not os.path.exists(conf_path):
            os.mkdir(conf_path)
        with open(os.path.join(conf_path, "svr_{0}.conf".format(s)), "wb") as fp:
            conf.write(fp)


if __name__ == '__main__':
    # pack()
    supervisor()
    print("build finished")
