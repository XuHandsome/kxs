from flask import current_app, jsonify, request, Blueprint
from .models import Cluster
from . import db
import json
from libs.k8s_client import Kubernetes

# 创建蓝图对象
cluster = Blueprint("cluster", __name__)
namespace = Blueprint("namespace", __name__)


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

    # 检查集群状态
    k8s = Kubernetes(api_host=api_host, token=token)
    health_status = k8s.health_check()
    if health_status:
        status = "active"
    else:
        status = "inactive"

    if cluster_info is not None:
        if cluster_info.status != 'deleted':
            return jsonify({"code": 10003, "msg": "集群已存在"})
        else:
            cluster_info.status = status
            try:
                db.session.commit()
                return jsonify({"code": 200, "msg": "集群已上线成功"})
            except Exception as e:
                current_app.logger.error(e)
                return jsonify({"code": 10002, "msg": "集群上线失败"})

    # 添加集群
    cluster_info = Cluster(name=name, api_host=api_host, token=token, status=status)
    try:
        db.session.add(cluster_info)
        db.session.commit()
        return jsonify({"code": 200, "msg": "添加集群成功"})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"code": 10002, "msg": "添加集群失败"})


@cluster.route("/delete", methods=["DELETE"])
def cluster_delete():
    cluster_id = request.args.get("id")
    if not cluster_id:
        return jsonify({"code": 10004, "msg": "参数不完整"})

    # 查询集群是否存在
    try:
        cluster_info = Cluster.query.filter_by(id=cluster_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"code": 10002, "msg": "查询集群失败"})

    if cluster_info is None:
        return jsonify({"code": 10003, "msg": "集群不存在"})

    # 删除集群(逻辑删除，更新status为deleted)
    cluster_info.status = "deleted"
    try:
        db.session.commit()
        return jsonify({"code": 200, "msg": "删除集群成功"})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"code": 10002, "msg": "删除集群失败"})


@cluster.route("/update", methods=["POST"])
def cluster_update():
    # 获取请求参数
    data = request.json
    cluster_id = data.get("id")
    name = data.get("name")
    api_host = data.get("api_host")
    token = data.get("token")
    if not all([cluster_id, name, api_host, token]):
        return jsonify({"code": 10004, "msg": "参数不完整"})

    # 查询集群是否存在
    try:
        cluster_info = Cluster.query.filter_by(id=cluster_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"code": 10002, "msg": "查询集群失败"})

    if cluster_info is None:
        return jsonify({"code": 10003, "msg": "集群不存在"})

    # 更新集群
    cluster_info.name = name
    cluster_info.api_host = api_host
    cluster_info.token = token

    k8s = Kubernetes(api_host=api_host, token=token)
    health_status = k8s.health_check()
    if health_status:
        cluster_info.status = 'active'
    else:
        cluster_info.status = 'inactive'

    try:
        db.session.commit()
        return jsonify({"code": 200, "msg": "更新集群成功"})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"code": 10002, "msg": "更新集群失败"})


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
    for c in clusters:
        data_list.append(c.to_dict())

    return jsonify({"code": 200, "msg": "查询集群成功", "data": {"total": total, "items": data_list}})


@namespace.route("/add", methods=["POST"])
def namespace_add():
    data = request.json
    cluster_id = data.get("cluster_id")
    namespace_name = data.get("namespace")

    if not cluster_id:
        return jsonify({"code": 10004, "msg": "参数不完整"})

    # 查询集群是否存在
    try:
        cluster_info = Cluster.query.filter_by(id=cluster_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"code": 10002, "msg": "查询集群失败"})

    if cluster_info is None:
        return jsonify({"code": 10009, "msg": "集群不存在"})

    if cluster_info.status == "deleted":
        return jsonify({"code": 10009, "msg": "集群已下线"})
    elif cluster_info.status == "inactive":
        return jsonify({"code": 10009, "msg": "集群连接失败"})

    api_host = cluster_info.api_host
    token = cluster_info.token
    k8s = Kubernetes(api_host=api_host, token=token)
    create_ns = k8s.create_namespace(namespace_name)
    try:
        create_ns_status = create_ns.status.to_dict()
        return jsonify({"code": 200, "msg": "创建命名空间成功", "k8s_response": create_ns_status})
    except Exception as e:
        create_ns_status = json.loads(create_ns.body).get('message')
        return jsonify({"code": 10002, "msg": "创建命名空间失败", "k8s_response": create_ns_status})


@namespace.route("/delete", methods=["DELETE"])
def namespace_delete():
    data = request.json
    cluster_id = data.get("cluster_id")
    namespace_name = data.get("namespace")

    if not cluster_id:
        return jsonify({"code": 10004, "msg": "参数不完整"})

    # 查询集群是否存在
    try:
        cluster_info = Cluster.query.filter_by(id=cluster_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"code": 10002, "msg": "查询集群失败"})

    if cluster_info is None:
        return jsonify({"code": 10009, "msg": "集群不存在"})

    if cluster_info.status == "deleted":
        return jsonify({"code": 10009, "msg": "集群已下线"})
    elif cluster_info.status == "inactive":
        return jsonify({"code": 10009, "msg": "集群连接失败"})

    api_host = cluster_info.api_host
    token = cluster_info.token
    k8s = Kubernetes(api_host=api_host, token=token)
    delete_ns = k8s.delete_namespace(namespace_name)
    try:
        delete_ns_status = eval(delete_ns.status)
        return jsonify({"code": 200, "msg": "删除命名空间成功", "k8s_response": delete_ns_status})
    except Exception as e:
        delete_ns_status = json.loads(delete_ns.body).get('message')
        return jsonify({"code": 10002, "msg": "删除命名空间失败", "k8s_response": delete_ns_status})


@namespace.route("/list", methods=["GET"])
def namespace_list():
    data = request.json
    cluster_id = data.get("cluster_id")

    if not cluster_id:
        return jsonify({"code": 10004, "msg": "参数不完整"})

    # 查询集群是否存在
    try:
        cluster_info = Cluster.query.filter_by(id=cluster_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"code": 10002, "msg": "查询集群失败"})

    if cluster_info is None:
        return jsonify({"code": 10009, "msg": "集群不存在"})

    if cluster_info.status == "deleted":
        return jsonify({"code": 10009, "msg": "集群已下线"})
    elif cluster_info.status == "inactive":
        return jsonify({"code": 10009, "msg": "集群连接失败"})

    cluster_name = cluster_info.name
    api_host = cluster_info.api_host
    token = cluster_info.token
    k8s = Kubernetes(api_host=api_host, token=token)

    return jsonify({"code": 200, "msg": "查询namespace成功", "cluster_name": cluster_name,"namespace_list": k8s.get_namespace_list()})
