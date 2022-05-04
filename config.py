# 项目需要的配置文件
import pymysql


class Config(object):
    # 数据库通用信息
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '123456'


# 开发环境
class DevelopmentConfig(Config):
    """
    开发环境下的配置
    create database kxs_dev charset utf8 COLLATE utf8_general_ci;
    """
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/kxs_dev'
    DEBUG = True


# 线上环境
class ProductionConfig(Config):
    """
    线上环境下的配置
    create database kxs_pro charset utf8 COLLATE utf8_general_ci;
    """
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/kxs_pro'


config_map = {
    'develop': DevelopmentConfig,
    'product': ProductionConfig
}
