#部署文档

# 项目说明
    1、游戏代码只能以pyc格式文件交付运维，所以只是提供配置文件 ./confs/system.conf 供运维管理，其他配置文件都根据此文件生成
    2、游戏服务端进程由supervisor守护，supervisor配置文件也是由代码生成
    3、游戏服务端需要依赖 zeromq, redis等基础服务
    4、游戏服务端主要是以tornado为核心提供异步长连接服务,以及提供web访问接口

# 配置说明
    system.conf 是配置文件, 主要为游戏服端口配置, 日志队列端口配置，以及redis配置
    文件格式如下
    -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
    [p1]
    server_port = 8051          // 游戏服端口
    logger_port = 8151          // 日志队列端口
    redis_port = 8251           // redis 端口
    redis_host = 127.0.0.1      // redis IP
    redis_password =            // redis 密码
    redis_db = 1                // redis DB
    -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
    supervisor 配置文件全部由此文档配置列表生成，
    每一个配置区块将生成 一个游戏进程配置以及一个对应的日志消费者进程配置
    所有端口都必须是唯一的，否则将导致进程启动失败
    注意：这个配置文件只做这一个配置类型

    web.conf 是游戏服汇报数据给web的配置
    [url]
    ;分配服url
    alloc = http://alloc.poker.xnny.com
    ;战绩服url
    record = http://poker.xnny.com
    如果是IP地址必须加上端口
    
# 部署步骤
    1、因为每一个游戏进程都会对应一个redis进程，所以要先启动对应数目的redis进程
    2、配置confs/system.conf文件
    3、由于是用的相对路径，所以部署前先切换到项目路径中
    4、在项目路径中安装 virtualenv .pyenv [这个是在supervisor文档生成的时候定好的]
    5、pip install -r requirements 安装所有依赖包
    6、.pyenv/bin/python build.pyc 根据confs/system.conf生成supervisor配置文件
    7、与web负责人员确定web.conf配置
    7、.pyenv/bin/supervisord -c confs/supervisor.conf 启动进程
    
# 其他说明
    因为配置比较繁琐所以不建议直接运行 start.sh 
    一般的更新代码先要通知web发起停服操作，等服务器玩家都退出后再重启进程