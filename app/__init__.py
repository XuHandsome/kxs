from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from config import config_map

db = SQLAlchemy()  # 先生成一个没有参数的实例化数据库


def create_app(env_name):
    """
    返回一个实例化好并且配置好数据连接的一个app
    env_name: 选择环境，可以是develop product
    """
    app = Flask(__name__)
    config_class = config_map.get(env_name)
    app.config.from_object(config_class)  # 从类中读取需要的信息（config.py）

    db.init_app(app)  # 实例化数据库

    # session存到redis中
    # 利用flask-session，将session存到redis中
    Session(app)

    # 注册蓝图
    from .api import cluster

    app.register_blueprint(cluster, url_prefix="/cluster")
    return app
