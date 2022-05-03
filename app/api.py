from flask import current_app, jsonify, request, Blueprint
from .models import Cluster
from . import db
from libs.cluster import Kubernetes

# 创建蓝图对象
cluster = Blueprint("cluster", __name__)


# 添加集群
@cluster.route("/add", methods=["POST"])
def cluster_add():
    # 获取请求参数
    data = request.json
    print(data)
    name = data.get("name")
    api_host = data.get("api_host")
    token = data.get("token")
    if not all([name, api_host, token]):
        return jsonify({"code": 10004, "msg": "参数不完整"})

    # 查询集群是否已存在
    try:
        cluster_info = Cluster.query.filter_by(name=name).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"code": 10002, "msg": "查询集群失败"})

    if cluster_info is not None:
        return jsonify({"code": 10003, "msg": "集群已存在"})

    # 添加集群
    k8s = Kubernetes(api_host=api_host, token=token)
    health_status = k8s.health_check()

    cluster = Cluster(name=name, api_host=api_host, token=token)
    if not health_status:
        cluster = Cluster(name=name, api_host=api_host, token=token, status="inactive")

    try:
        db.session.add(cluster)
        db.session.commit()
        return jsonify({"code": 200, "msg": "添加集群成功"})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"code": 10002, "msg": "添加集群失败"})

@cluster.route("/list", methods=["GET"])
def cluster_list():
    # 获取请求参数
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 10)

    try:
        cluster_name = request.args.get("cluster_name")
        if cluster_name:
            paginate = Cluster.query.filter_by(name=cluster_name).paginate(page, per_page, error_out=False)
        else:
            paginate = Cluster.query.paginate(int(page), int(per_page), False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"code": 10002, "msg": "查询集群失败"})

    clusters = paginate.items
    total = paginate.total
    data_list = []
    for cluster in clusters:
        data_list.append(cluster.to_dict())

    return jsonify({"code": 200, "msg": "查询集群成功", "data": {"total": total, "items": data_list}})