from flask import Flask, g, session
import config
from exts import db, mail
from blueprints import qa_bp, user_bp
from flask_migrate import Migrate
from models import UserModel

# 传入__name__初始化一个Flask实例
app = Flask(__name__)
# 通过模块对象加载项目配置
app.config.from_object(config)

db.init_app(app)
mail.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(qa_bp)
app.register_blueprint(user_bp)


# 在所有请求之前会执行的函数
@app.before_request
def before_request():
    user_id = session.get("user_id")
    if user_id:
        try:
            user = UserModel.query.get(user_id)
            # 给g绑定一个user属性，这个属性就是user这个变量
            # setattr(g, "user", user)
            g.user = user
        except:
            g.user = None


# 请求来了 -> before_request -> 视图函数 -> 摄图函数中返回模板 -> context_processor
# 渲染的所有的模板都会执行这个函数
@app.context_processor
def context_processor():
    if hasattr(g, "user"):
        return {"user": g.user}
    else:
        return {}


if __name__ == '__main__':
    app.run()

'''
    1. before_request：
    *在请求之前执行的
    *是在视图函数执行之前执行的
    *这个函数只是一个装饰器，他可以把需要设置为钩子函数的代码放到视图函数执行之前来执行

    2. context_processor：
    *上下文处理器应该返回一个字典。字典中的`key`会被模板中当成变量来渲染。
    *上下文处理器中返回的字典，在所有页面中都是可用的。
    *被这个装饰器修饰的钩子函数，必须要返回一个字典，即使为空也要返回。
'''