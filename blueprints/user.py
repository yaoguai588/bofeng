from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mail import Message
from exts import mail, db
from models import EmailCaptchaModel, UserModel
from datetime import datetime
import string
import random
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm

bp = Blueprint("user", __name__, url_prefix="/user")
'''
    该类用于处理用户页面的请求，主要包括：注册、登录、注册、验证码邮件
'''


# route装饰器映射URL和执行的函数
# 该函数处理验证码生成、发送、更新
@bp.route("/captcha", methods=["POST"])
def get_captcha():
    # 由前端页面得到邮箱地址
    email = request.form.get("email")
    print(email)
    # 由 数字 和 大小写字母 组成的新字符串
    my_string = string.digits + string.ascii_letters
    # 返回一个长度为 4 新列表，新列表存放 mystring 所产生 4 个随机唯一的元素
    captcha = "".join(random.sample(my_string, 4))
    print(captcha)

    if email:
        # 封装了一封电子邮件
        message = Message(
            # 标题
            subject="验证码",
            # 收件人
            recipients=[email],
            # 消息主体
            body=f"博峰论坛提醒您，您的注册验证码为：{captcha},请勿告诉他人！",
        )
        mail.send(message)

        captcha_model = EmailCaptchaModel.query.filter_by(email=email).first()
        # 如果存在则修改数据并更新时间
        if captcha_model:
            captcha_model.captcha = captcha
            captcha_model.create_time = datetime.now()
            db.session.commit()
        # 不存在则实例化添加
        else:
            captcha_model = EmailCaptchaModel(email=email, captcha=captcha)
            db.session.add(captcha_model)
            db.session.commit()
        # 表明该请求被成功地完成，所请求的资源发送到客户端 返回JSON类型Response
        return jsonify({"code": 200})
    else:
        # 表明客户端请求有语法错误
        return jsonify({"code": 400})


# 该函数处理登录校验
@bp.route("/login", methods=["GET", "POST"])
def login():
    # GET方式登录
    if request.method == "GET":
        return render_template("login.html")
    # POST方式登录
    else:
        # 获取页面表单以获得输入数据
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            user = UserModel.query.filter_by(email=email).first()
            # 用户存在且密码校对正确，存储session并跳转首页
            if user and check_password_hash(user.password, password):
                session["user_id"] = user.id
                return redirect("/")
            # 用户不存在或密码校对失败，跳转登录页
            else:
                flash("邮箱密码不匹配！")
                return redirect(url_for("user.login"))
        else:
            flash("邮箱或密码格式错误！")
            return redirect(url_for("user.login"))


# 该函数处理注册校验
@bp.route("/register", methods=["GET", "POST"])
def register():
    # GET方式
    if request.method == "GET":
        return render_template("register.html")
    # POST方式
    else:
        # 获取页面表单以获得输入数据
        form = RegisterForm(request.form)
        if form.validate():
            email = form.email.data
            username = form.username.data
            password = form.password.data
            # 加密密码
            hash_password = generate_password_hash(password)
            user = UserModel(email=email, username=username, password=hash_password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("user.login"))
        else:
            print("validate 失败")
            return redirect(url_for("user.register"))


# 该函数处理用户登出
@bp.route("/logout")
def logout():
    # 清除session会话
    session.clear()
    return redirect(url_for("user.login"))


# 该函数用于邮件发送测试
@bp.route("/mail")
def my_mail():
    message = Message(
        subject="邮箱测试",
        recipients=["298893773@qq.com"],
        body="这是一遍测试邮件",
    )
    mail.send(message)
    return "success!"
