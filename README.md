# 博峰论坛
基于flask框架搭建的互动问答论坛，该项目还提供了应用上云—使用nginx部署flask项目方案并完成动静分离与负载均衡(ip_hash)。
# 项目结构
![image](https://user-images.githubusercontent.com/77235548/217037449-a67ed7fd-cc44-4974-a8ac-5cfb8336121c.png)

以下对各个文件的作用进行解释。

## 包
### blueprints包
Blueprint 是一个存储操作方法的容器，这些操作在这个Blueprint 被注册到一个应用之后就可以被调用，Flask 可以通过Blueprint来组织URL以及处理请求。

![image](https://user-images.githubusercontent.com/77235548/217038262-62edaacb-acc6-48af-86a6-63428d2a598b.png)
- qa.py：该类用于处理问答页面请求，主要包括：搜索、详情、发布、评论
- user.py： 该类用于处理用户页面的请求，主要包括：注册、登录、注册、验证码邮件
- init.py
```python
from .qa import bp as qa_bp
from .user import bp as user_bp
```
### migrations包
flask-migrate 是基于 Alembic 进行的一个封装，并集成到 Flask 中，而所有的迁移操作其实都是 Alembic 做的，他能跟踪模型的变化，并将变化映射到数据库中。

![image](https://user-images.githubusercontent.com/77235548/217039019-37265535-ecc5-4efd-a48b-d5b28b8e7633.png)

### static包
静态文件,顾名思义,就是那些不会被改变的文件,比如图片,CSS 文件和JavaScript 源码文件。默认情况下,Flask 在程序根目录中名为 static 的子目录中寻找静态文件。

![image](https://user-images.githubusercontent.com/77235548/217039418-50f56e72-ca75-468e-a3f1-a1803cf67870.png)

### templates包
用于存放前端页面的模板文件。

![image](https://user-images.githubusercontent.com/77235548/217039989-f7cf5a49-c8d3-428e-a807-766451c79c0b.png)

## 文件
![image](https://user-images.githubusercontent.com/77235548/217040324-64997edb-94be-4c58-a8b3-b797688582d3.png)

### app.py文件
这个是主`app`文件，运行文件。并且因为`db`被放到另外一个文件中，所以使用`db.init_app(app)`的方式来绑定数据库。

### config.py文件

常量文件，用来存放数据库配置和邮箱配置。

### decorators.py文件
修饰器文件，使评论和问答需登录才能发布

### exts.py文件

把`db`变量和`mail`变量放到一个单独的文件，而不是放在主`app`文件。
这样做的目的是为了在大型项目中如果`db`被多个模型文件引用的话，会造成`from your_app import db`这样的方式，但是往往也在`your_app.py`中也会引入模型文件定义的类，这就造成了循环引用。所以最好的办法是把它放在不依赖其他模块的独立文件中。

```python
# ext.py
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()
```

### forms.py文件
表单文件，用来对注册表单、登录表单、问答表单、评论表单进行规范化限制。

### models.py文件

模型文件，用来存放所有的模型，并且注意，因为这里使用的是`flask-script`的方式进行模型和表的映射，因此不需要使用`db.create_all()`的方式创建数据库。
