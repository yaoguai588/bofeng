# 数据库的配置
HOSTNAME = '192.168.0.172'
PORT = '3307'
DATABASE = 'forum'
USERNAME = 'root'
PASSWORD = '123456'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)

SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = True

# 秘钥
SECRET_KEY = "SDFASDFASDFASDFASDFASDF"

# 邮箱配置
# 本项目中用的是QQ邮箱
MAIL_SERVER = "smtp.qq.com"
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEBUG = True
MAIL_USERNAME = "2584686736@qq.com"
<<<<<<< HEAD
# 填写自己邮箱的smtp服务授权码
MAIL_PASSWORD = "xxxxxxxxxxxx"
=======
# 填写自己QQ邮箱的 SMTP 授权码
MAIL_PASSWORD = "xxx"
>>>>>>> 8af580f (add nginx)
MAIL_DEFAULT_SENDER = "2584686736@qq.com"
