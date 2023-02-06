import wtforms
from wtforms.validators import length, email, EqualTo
from models import EmailCaptchaModel, UserModel


# 注册表单
class RegisterForm(wtforms.Form):
    username = wtforms.StringField(validators=[length(min=3, max=20)])
    captcha = wtforms.StringField(validators=[length(min=4, max=4)])
    password = wtforms.StringField(validators=[length(min=6, max=20)])
    password_confirm = wtforms.StringField(validators=[EqualTo("password")])
    email = wtforms.StringField(validators=[email()])

    def validate_captcha(self, field):
        captcha = field.data
        email = self.email.data
        captcha_model = EmailCaptchaModel.query.filter_by(email=email).first()
        if not captcha_model or captcha_model.captcha.lower() != captcha.lower():
            print("邮箱验证码错误")
            raise wtforms.ValidationError("邮箱验证码错误")

    def validate_email(self, field):
        email = field.data
        user_model = UserModel.query.filter_by(email=email).first()
        if user_model:
            print("邮箱已经被注册过")
            raise wtforms.ValidationError("邮箱已经被注册过")


# 登录表单
class LoginForm(wtforms.Form):
    email = wtforms.StringField(validators=[email()])
    password = wtforms.StringField(validators=[length(min=6, max=20)])


# 问答表单
class QuestionForm(wtforms.Form):
    title = wtforms.StringField(validators=[length(min=3, max=150)])
    content = wtforms.StringField(validators=[length(min=4)])


# 评论表单
class AnswerForm(wtforms.Form):
    content = wtforms.StringField(validators=[length(min=1)])
