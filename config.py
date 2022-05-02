# 项目需要的配置文件
import redis
import pymysql


class Config(object):
    # 数据库通用信息
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '123456'

    # flask-session通用配置
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True  # 对cookie中session_id进行隐藏处理 加密混淆
    PERMANENT_SESSION_LIFETIME = 20  # session数据的有效期，单位秒


# 开发环境
class DevelopmentConfig(Config):
    """
    开发环境下的配置
    create database caiji_dev charset utf8 COLLATE utf8_general_ci;
    """
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/caiji_dev'
    SESSION_REDIS = redis.Redis(host='127.0.0.1', port=6379, db=2)
    DEBUG = True


# 线上环境
class ProductionConfig(Config):
    """
    线上环境下的配置
    create database caiji_pro charset utf8 COLLATE utf8_general_ci;
    """
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/caiji_pro'
    SESSION_REDIS = redis.Redis(host='127.0.0.1', port=6379, db=3)


config_map = {
    'develop': DevelopmentConfig,
    'product': ProductionConfig
}
