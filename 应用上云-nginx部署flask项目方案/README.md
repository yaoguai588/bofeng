# flask+nginx+uWSGI线上部署项目说明

## 部署结构图

nginx + uWSGI + flask的架构图如下所示：

![image](https://user-images.githubusercontent.com/77235548/217321218-b1745254-510b-407b-b221-fb48f50d6932.png)

## 为什么需要flask+nginx+uWSGI?

虽然flask的开发模式也是可以作为一个web 服务器使用的，但是同一个客户端ip请求同一个服务器ip好像是相互阻塞的。也就是说，我在访问页面A的时候（A正在加载中），然后再去访问页面B，页面B会延迟一会儿才能加载出来。使用如下的flask的命令行可以多开几个进程能够快一些，但是这不能解决本质问题，所以才要用flask+nginx+uWSGI来解决该问题。

```python
python3 app.py runserver -h 0.0.0.0 -p 8080 --processes 10
```

## flask中部署uWSGI

### 安装flask

```bash
pip3 install flask
```

### 安装uWSGI

- 首先安装好相关的依赖：

```bash
yum install python-devel
```

- 有两种安装方式：

```bash
# 1.pip包管理器
pip3 install uWSGI
# 2.编译安装
# pypi 中下载uwsgi的压缩包，
tar zxvf uwsgi-2.0.18.tar.gz
mv uwsgi-2.0.18 /usr/local/uwsgi/ 
cd uwsgi-2.0.18
python3 uwsgiconfig.py --build
python3 setup.py install
# 执行完之后会出现一个绿色的文件uwsgi，这个一个可执行文件
# 为uwsgi添加软连接
ln -s /usr/local/uwsgi/uwsgi-2.0.18/uwsgi /usr/bin/uwsgi
```

uWSGI的配置可以写为4种格式 .ini 、.xml 、.yaml 、.json。但是我们常用的就是.ini，这里以.ini 为例。

### 启动一个本地HTTP服务器

```python
# /PycharmProjects/myflaskproject/foobar.py

def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    return [b"Hello World"]
```

- uWSGI Python 加载器将会搜索的默认函数 application，所以在uWSGI的配置文件中通常要使用callable=应用名，指明文件中的应用名 。

- 接下来我们启动 uWSGI 来运行一个 本地的HTTP 服务器，将程序部署在HTTP端口 9090 上：

```bash
uwsgi --http :9090 --wsgi-file foobar.py
```

- 或者写入配置文件，文件名字自己取，后缀名一般为 .ini ：
  在这种格式的文件中，注释请使用“;”。

```bash
[uwsgi]
http = :5000     #  启动程序时所使用的地址和端口，通常在本地运行flask项目，
chdir = /home/flaskproject/          #  项目目录
wsgi-file = manage.py      # flask程序的启动文件，通常在本地是通过运行  python manage.py runserver 来启动项目的
callable = app      	   #  程序内启用的application变量名
processes = 4     	   #  处理器个数，进程个数
threads = 2     	   #  线程个数
stats = 127.0.0.1:9191     #  获取uwsgi统计信息的服务地址
pidfile = uwsgi.pid        #  保存pid信息，方便停止服务和重启的时候用
daemonize = ./log/uwsgi.log  #  后台运行时记录uwsgi的运行日志
lazy-apps = true             #  当需要连接cassandra时,uwsgi无法启动服务,可以使用该选项设置
master-fifo = /opt/mt-search/web-service/mfifo   # 使用chain-reloading 逐个work重启,服务不中断, 命令是 echo c > mfifo
touch-chain-reload = true
```

uWSGI是python的一个库，安装了这个库之后，我们可以使用命令uwsgi，通过这个命令和一些配置，我们能够产生一个web服务器，产生的web服务器有两种方式。

- **无代理的web服务器**，也就是说flask框架所在的机器就作为一个独立的web服务器直接和客户端进行通信，因为客户端是通过HTTP/HTTPS来通信的，所以这个web服务器必须使用相应的协议，否则无法通信。
- **有代理的Web服务器**，例如nginx。这时flask框架所在的机器不需要直接与客户端通信，只需要和代理服务器通信就行了（这时使用的协议就不限于HTTP/HTTPS了，这就看服务器之间协议的支持情况了）。而对于本文档使用的 uWSGI web 服务器而言，最佳的协议是uwsgi。

1.使用 **--http** 指明了通信协议为http或https。因此这种模式，通过浏览器可以直接与web服务器通信。这种情况并没有使用nginx，仅仅是通过uWSGI+flask。

![image](https://user-images.githubusercontent.com/77235548/217322224-d6091020-5242-4612-b94f-9aa1f0feeb7f.png)

2.而使用 **--socket** 是在如下的这种情况。

![image](https://user-images.githubusercontent.com/77235548/217322256-207ff57a-9687-40d4-aad5-3346ea5f3f1f.png)

这种情况应该是uWSGI web服务器和nginx进行通信，并不是通过http协议或者htttps协议，而是通过其它协议（通常是uwsgi协议)进行的。

整体流程是：

![image](https://user-images.githubusercontent.com/77235548/217322307-9b9abd00-bd92-4719-902d-da3ba2f2a0ab.png)

### 启动一个uWSGI 服务器

假设这是我的flask应用。

```python
# myflaskapp.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "<span style='color:red'>I am app 1</span>"
```

- 在命令行中使用的配置如下：

```python
uwsgi --socket 127.0.0.1:3031 --wsgi-file myflaskapp.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191
```

- 在flask中的.ini配置如下：

```python
[uwsgi]
socket = 127.0.0.1:5000     #  启动程序时所使用的地址和端口，通常在本地运行flask项目，
                            #  Flask地址和端口是127.0.0.1:5000,
                            #  不过在服务器上是通过uwsgi设置端口，通过uwsgi来启动项目，
                            #  也就是说启动了uwsgi，也就启动了项目。
chdir = /home/flaskproject/ #  项目目录
wsgi-file = manage.py      # flask程序的启动文件，通常在本地是通过运行 python manage.py runserver 来启动项目的
callable = app      	   #  程序内启用的application变量名
processes = 4     	   #  处理器个数，进程个数
threads = 2     	   #  线程个数
stats = 127.0.0.1:9191     #  获取uwsgi统计信息的服务地址
pidfile = uwsgi.pid        #  保存pid信息，方便停止服务和重启的时候用
daemonize = ./log/uwsgi.log  #  后台运行时记录uwsgi的运行日志
lazy-apps = true             #  当需要连接cassandra时,uwsgi无法启动服务,可以使用该选项设置
master-fifo = /opt/mt-search/web-service/mfifo   # 使用chain-reloading 逐个work重启,服务不中断, 命令是 echo c > mfifo
touch-chain-reload = true
```

此时因为客户端使用的协议（http/https）和uWSGI 服务器使用的协议并不相同（uwsgi）还无法访问服务器，需要配置中间的 nginx 代理服务器。

## 部署nginx

nginx中的协议支持如下如所示，客户端是下游，nginx之后的web服务器是上游

![image](https://user-images.githubusercontent.com/77235548/217322356-92c48ad8-f03f-4a94-a101-fe83a28d9f5f.png)

### 安装nginx

- 首先安装nginx的依赖

```python
//一键安装
yum -y install gcc zlib zlib-devel pcre-devel openssl openssl-devel
```

- 下载nginx压缩包: 可以通过 nginx 官网 下载，也可以使用 wget 下载：

```python
wget http://nginx.org/download/nginx-1.14.2.tar.gz

```

- 解压:

```python
tar zxvf nginx-1.14.2.tar.gz
```

- 编译和安装:

```python
cd nginx-1.14.2/
./configure
make && make install
```

安装成功的话会在/usr/local/下出现一个新的目录 nginx，根据需要修改此目录下的配置。

### 配置nginx

- 进入nginx的安装目录，如果完全按照上述方法，那么该目录是 `/usr/local/nginx/`

```bash
cd /user/local/nginx/conf/

ll 会发现一个 nginx.conf , 一个nginx.conf.default
# nginx.conf.default是ngnix的默认配置文件，不用修改
# 修改nginx.conf文件中的配置为我们所需要的配置即可
```

- 如果nginx代理的三个服务器都在端口*：80上监听，那么nginx首先决定哪个服务器应该处理请求：

```python
server {
    listen      80; # 监听端口
    server_name example.org www.example.org; # 服务器名称
    ...
}

server {
    listen      80;# 监听端口
    server_name example.net www.example.net;# 服务器名称
    ...
}

server {
    listen      80;# 监听端口
    server_name example.com www.example.com;# 服务器名称
    ...
}
```

nginx是根据请求中的"Host"字段来决定应当将这个客户端的请求转发给哪一个web服务器，这个"Host"的值应当是与某一个server_name 相匹配的。但是， 如果其值与任何服务器的 server_name 都不匹配，或者请求根本不包含"Host"字段，则nginx会将请求转发到此端口的默认服务器。 

在上面的配置中，默认服务器是第一个,这是nginx的标准默认行为。 它也可以使用listen指令中的default_server参数明确设置哪个服务器应该是默认的，如下所示 example.net www.example.net 将是默认的 server_name：

```python
server {
    listen      80 default_server; # 监听端口， 此服务器为默认服务器
    server_name example.net www.example.net; # 服务器名称
    ...
}
```

**请注意，默认服务器是监听端口（listen）的属性，而不是 server_name 的属性。**

如果客户端的请求中没有"Host"字段，那么我们可以定义配置文件，来扔掉这类的客户端请求。

如下的配置中，server_name 设置为一个空字符串，它将匹配没有“Host”头字段的请求，并返回一个特殊的nginx非标准代码444来关闭连接。

```python
server {
    listen      80;
    server_name "";
    return      444;
}
```

- 不同ip地址的服务器：

```python
# 第一个服务器
server {
    listen      192.168.1.1:80; # 监听此ip的80端口
    server_name example.org www.example.org; # 服务器名
    ...
}

# 第二个服务器
server {
    listen      192.168.1.1:80 default_server; # 监听此ip的80端口
    server_name example.net www.example.net; # 服务器名，为此ip，端口的默认服务器
    ...
}

# 第三个服务器
server {
    listen      192.168.1.2:80 default_server; # 监听此ip的80端口
    server_name example.com www.example.com; # 服务器名，为此ip，端口的默认服务器
    ...
}
```

在上面的配置中，nginx首先根据配置中 server 的 listen指令监听请求的ip地址和端口。

然后，在监听此 ip 和端口的 server 中找到与请求中"Host"字段匹配的 server_name ，让这个 server_name 来处理此请求。如果未找到匹配的 server_name ，则由默认服务器处理该请求。

例如，在 192.168.1.1:80 端口上收到的 host 为 www.example.com 请求将由192.168.1.1:80端口的默认服务器处理，即由第二台服务器处理，因为192.168.1.1:80 端口上没有名为 www.example .com 的 server_name。

**在指定的服务器中由哪一个 location 来处理请求呢？**

下面的配置中由3个location，

匹配 location 的过程如下：

- 首先，nginx不管location的顺序，而是从location中找到与请求的url最匹配、最具体的这个location前缀。需要注意的是，/ 根目录能够匹配到所有的请求，也就是说，所有的请求都可以由 / 根目录的这个location来处理。因此，/ 根目录的location是只有没有其他的location匹配这个url的时候，才会由 / 根目录的location来处理该请求。

- 其次， nginx 检查由正则表达式组成的location。一旦找到匹配的location，则停止查找，由此location来处理该请求。

- 然后，如果没有匹配的正则表达式location的话，则由第一步中找到的location前缀来处理该请求。

```python
server {
    listen      80; # 监听本机的80端口
    server_name example.org www.example.org; # 服务器名
    root        /data/www; 

    location / { # 这里的 / 指明的前缀位置为根目录
        index   index.html index.php;
    }

    location ~* \.(gif|jpg|png)$ {
        expires 30d;
    }

    location ~ \.php$ {
        fastcgi_pass  localhost:9000;
        fastcgi_param SCRIPT_FILENAME
                      $document_root$fastcgi_script_name;
        include       fastcgi_params;
    }
}
```

**需要注意的是，只匹配请求url中的非参数部分。**这是因为，参数可以有很多种方式给出，例如：

```bash
/index.php?user=john&page=1
/index.php?page=1&user=john
/index.php?page=1&something+else&user=john # 查询字符串中的内容种类太多了，不好匹
```

举几个例子看看上面的nginx配置是如何处理请求的吧。

- 请求url “/logo.gif” 首先与location 前缀 “/” 匹配，也与正则表达式 “.(gif|jpg|png)” 匹配，因此，它由第二个location处理。 使用指令"root" /data/www 将请求映射到文件/data/www/logo.gif，并将该文件返回给客户端。

- 请求url “/index.php” 首先和lcoation 前缀 "/“匹配，也与正则表达式 “.php$ " 匹配，因此，由第三个location来处理请求。请求被传递给监听localhost：9000的FastCGI服务器。 fastcgi_param指令将FastCGI参数SCRIPT_FILENAME设置为“/data/www/index.php”，FastCGI服务器执行该文件。 变量$ document_root等于root指令的值（/data/www），变量$ fastcgi_script_name等于请求URI （”/index.php”）。

- 请求 “/about.html” 仅与location前缀 “/” 匹配，因此，该请求由此locatoin处理。 使用 “root” 指令（值 /data/www）将请求映射到文件/data/www/about.html，并将文件返回给客户端。

- 请求 “/” 仅与 location前缀 “/” 匹配，因此该请求由此location处理。然后索引指令根据其参数和 “root” 指令的值/data/www查找文件是否存在。 如果文件/data/www/index.html不存在，并且文件/data/www/index.php存在，则指令执行内部重定向到“/index.php”，并且nginx再次搜索位置 如果请求是由客户发送的。 正如我们之前看到的，重定向的请求最终将由FastCGI服务器处理。

```python
http {
    upstream myapp1 {
        server srv1.example.com;
        server srv2.example.com;
        server srv3.example.com;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://myapp1;
        }
    }
}
```

在上面的示例中，在srv1-srv3上运行了3个相同应用程序的实例。 如果没有指明配置负载均衡的方法，则默认为循环方式复杂均衡。 所有请求都代理到服务器组myapp1，nginx应用HTTP负载平衡来分发请求。要为HTTPS而不是HTTP配置负载均衡，只需使用“https”作为协议。

## tips

### uwsgi启动/停止

```python
uwsgi --ini uwsgi.ini # 启动
uwsgi --reload uwsgi.pid  # 重启
uwsgi --stop uwsgi.pid # 停止
```

### nginx启动/停止

```python
nginx  //启动
nginx -s stop/quit //停止
nginx -s reload   //重启加载配置
nginx -t //检查配置文件正确性
```

## 总结

使用flask + nginx + uWSGI线上部署项目并完成负载均衡的过程如上如述，详细解决方案配置文件如 `nginx.conf` 所示。
