from flask import session, jsonify, request, Blueprint
from .models import User, Admin, db

# 创建一个蓝图对象
user = Blueprint("user", __name__)  # 用户蓝图对象
admin = Blueprint("admin", __name__)  # 管理员蓝图对象


# 用户初始页面
@user.route('/index', methods=['GET'])
def hello_world():
    return 'Hello 用户!'


# 用户注册
@user.route('/register', methods=['POST'])
def user_register():
    try:
        my_json = request.get_json()
        print(my_json)
        username = my_json.get('username')
        password = my_json.get('password')
        if not all([username, password]):
            return jsonify({'code': 4000, 'msg': '参数不完整'})

        user = User(username=username, password=password)

        # 添加到数据库
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '注册成功', username: username})
        except Exception as e:
            print(e)
            return jsonify({'code': 4001, 'msg': '数据库创建用户失败'})
    except Exception as e:
        print(e)
        return jsonify({'code': 4002, 'msg': '注册失败，请查看是否正确访问'})


# 用户登录
@user.route('/login', methods=['POST'])
def user_login():
    get_data = request.get_json()
    username = get_data.get('username')
    password = get_data.get('password')
    if not all([username, password]):
        return jsonify({'code': 4000, 'msg': '参数不完整'})

    user = User.query.filter_by(username=username).first()

    # 如果用户存在且密码对
    if user and user.password == password:

        # 如果验证通过，保存登录状态在session中
        session['user_username'] = username
        return jsonify({'code': 200, 'msg': '登录成功', "username": username})
    else:
        return jsonify({'code': 4001, 'msg': '用户名或密码错误'})


# 检查登录状态
@user.route('/session', methods=['GET'])
def user_check_session():
    username = session.get("user_username")
    if username is not None:
        # 操作逻辑 数据库查询一系列操作
        # 数据库里面把头像、等级、金币数量查询出来
        return jsonify({'code': 200, "username": username})
    else:
        return jsonify({'code': 4000, 'msg': '没有登录'})


# 登出
@user.route('/logout', methods=['DELETE'])
def user_logout():
    username = session.get("user_username")
    if username is None:
        return jsonify({'code': 4000, 'msg': '你还没有登录'})
    # 清理用户session
    session.pop('user_username', None)
    return jsonify({'code': 200, 'msg': '成功退出登录！'})


# 用户初始页面
@admin.route('/index', methods=['GET'])
def hello_world():
    return 'Hello 管理员!'


# 管理员注册
@admin.route('/register', methods=['POST'])
def admin_register():
    try:
        my_json = request.get_json()
        print(my_json)
        username = my_json.get('username')
        password = my_json.get('password')
        if not all([username, password]):
            return jsonify({'code': 4000, 'msg': '参数不完整'})

        admin = Admin(username=username, password=password)

        # 添加到数据库
        try:
            db.session.add(admin)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '注册成功', "username": username})
        except Exception as e:
            print(e)
            return jsonify({'code': 4001, 'msg': '数据库创建用户失败'})
    except Exception as e:
        print(e)
        return jsonify({'code': 4002, 'msg': '注册失败，请查看是否正确访问'})


# 管理员登录
@admin.route('/login', methods=['POST'])
def admin_login():
    get_data = request.get_json()
    username = get_data.get('username')
    password = get_data.get('password')
    if not all([username, password]):
        return jsonify({'code': 4000, 'msg': '参数不完整'})

    admin = Admin.query.filter_by(username=username).first()

    # 如果用户存在且密码对
    if admin and admin.password == password:

        # 如果验证通过，保存登录状态在session中
        session['admin_username'] = username
        return jsonify({'code': 200, 'msg': '登录成功', "username": username})
    else:
        return jsonify({'code': 4001, 'msg': '用户名或密码错误'})


# 检查管理员登录状态
@admin.route('/session', methods=['GET'])
def admin_check_session():
    username = session.get("admin_username")
    if username is not None:
        # 操作逻辑 数据库查询一系列操作
        # 数据库里面把头像、等级、金币数量查询出来
        return jsonify({'code': 200, "username": username})
    else:
        return jsonify({'code': 4000, 'msg': '没有登录'})


# 管理员登出
@admin.route('/logout', methods=['DELETE'])
def admin_logout():
    username = session.get("admin_username")
    if username is None:
        return jsonify({'code': 4000, 'msg': '你还没有登录'})

    # 清理管理员session
    session.pop('admin_username', None)
    return jsonify({'code': 200, 'msg': '成功退出登录！'})
