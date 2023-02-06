from flask import Blueprint, render_template, request, redirect, flash, url_for, g
from decorators import login_required
from exts import db
from forms import QuestionForm, AnswerForm
from models import QuestionModel, AnswerModel
from sqlalchemy import or_

bp = Blueprint("qa", __name__, url_prefix="/")
'''
    该类用于处理问答页面请求，主要包括：搜索、详情、发布、评论
'''


# route装饰器映射URL和执行的函数
# 搜索内容
@bp.route("/search")
def search():
    q = request.args.get("q")
    # filter是直接使用字段名称
    # filter_by是使用模型.字段名称
    questions = QuestionModel.query.filter(
        or_(QuestionModel.title.contains(q), QuestionModel.content.contains(q))).order_by(db.text("-create_time"))
    return render_template("index.html", questions=questions)


# 问答详情
@bp.route("/question/<int:question_id>")
def question_detail(question_id):
    question = QuestionModel.query.get(question_id)
    return render_template("detail.html", question=question)


# 问答主页
@bp.route("/")
def index():
    questions = QuestionModel.query.order_by(db.text("-create_time")).all()
    return render_template("index.html", questions=questions)


# 发布问答
@bp.route("/question/public", methods=["GET", "POST"])
@login_required
def public_question():
    if request.method == "GET":
        return render_template("public_question.html")
    else:
        form = QuestionForm(request.form)
        if form.validate():
            title = form.title.data
            content = form.content.data
            question = QuestionModel(title=title, content=content, author=g.user)
            db.session.add(question)
            db.session.commit()
            return redirect("/")
        else:
            flash("标题或者内容格式错误！！")
            return redirect(url_for("qa.public_question"))


# 评论视图函数
@bp.route("/answer/<int:question_id>", methods=["GET", "POST"])
@login_required
def answer(question_id):
    form = AnswerForm(request.form)
    if form.validate():
        content = form.content.data
        answer_model = AnswerModel(content=content, author=g.user, question_id=question_id)
        db.session.add(answer_model)
        db.session.commit()
        return redirect(url_for("qa.question_detail", question_id=question_id))
    else:
        flash("表单验证失败！！")
        return redirect(url_for("qa.question_detail", question_id=question_id))
