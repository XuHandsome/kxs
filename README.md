## kxs

### 接口清单

#### Cluster
- [x]   cluster/add
- [ ]   cluster/access 
- [x]   cluster/list
- [ ]   ...

#### Pod
- [ ]   pod/list
- [ ]   ...


### 接口错误代码
| 错误代码  | 说明        |
|:------|:----------|
| 10002 | 数据库连接失败   |
| 10004 | 传参不完整     |
| 10009 | k8s集群连接失败 |


### k8s获取token

```bash
# 获取集群名称
kubectl config view -o jsonpath='{"Cluster name\tServer\n"}{range .clusters[*]}{.name}{"\t"}{.cluster.server}{"\n"}{end}'
export CLUSTER_NAME="kubernetes"
# 创建scret，绑定cluster-admin权限
kubectl create serviceaccount kxs -n kube-system
kubectl create clusterrolebinding kxs --clusterrole=cluster-admin --serviceaccount=kube-system:kxs
APISERVER=$(kubectl config view -o jsonpath="{.clusters[?(@.name==\"$CLUSTER_NAME\")].cluster.server}")
kubectl describe secrets -n kube-system $(kubectl -n kube-system get secret | awk '/kxs/{print $1}')
TOKEN="eyJhbGciOiJSUzI1NiIsImtpZCI6IjR2V3lPWXUxa1I5Znl4c1NaMExfR3czaWFUdnAyMk54U2lMUk1nZnVOcWsifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJreHMtdG9rZW4tcWJwc2QiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoia3hzIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiYThlZTI3NTMtYTQ3ZC00OGFkLTgzZDItNjk0NjQ4M2U5OGIyIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmt4cyJ9.KdrM8Dnb3q8HTlOHEihsdk71pA-etVbO6QDdAf1zXxuV6zK2Dnl4c2SvoHvamd-jnwOYugbADKdrUmOAq7tX4-dZvtpFIkfteMiSsX-vdDYSddrpqTgon4aIayb8gutGTaYDPdi8MkogWAxFm6YF8F59WXPeNId00iBBdqv_s4KeEuDtFS74B3UeUFLTGkbpe5QdEMsimWkkCLwqD0H7srd7R7vS75NvfgYqOnBJl2aYmCwHQ4INQVeDM7n2U6-d8k5ncRidRKYpp5SzsJgYx58nmE4OucdXupm3RIkcUq_d1gFcGCWlOO4saacV-PHSm3m5XdnpZO42-SJKQlxg6Q"
# 测试请求
curl -X GET $APISERVER/api --header "Authorization: Bearer $TOKEN" --insecure
```