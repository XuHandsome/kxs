from . import db


# Cluster表
class Cluster(db.Model):
    __tablename__ = "kxs_cluster"
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(128), nullable=False, unique=True)  # 集群名称
    api_host = db.Column(db.String(32), nullable=False)  # 集群api地址
    token = db.Column(db.Text(65536), nullable=False)  # 集群token
    status = db.Column(db.Enum('active', 'inactive', 'deleted'), default='active')  # 集群状态

    def __repr__(self):
        return "<Cluster %r>" % self.name

    def to_dict(self):
        """将对象转换为字典数据"""
        cluster_dict = {
            "id": self.id,
            "name": self.name,
            "api_host": self.api_host,
            "token": self.token,
            "status": self.status
        }
        return cluster_dict
