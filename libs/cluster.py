from kubernetes.client import api_client
from kubernetes.client.api import core_v1_api
from kubernetes import client


class Kubernetes(object):
    def __init__(self, api_host, token):
        self.api_host = api_host
        self.token = token

    def get_api(self):
        configuration = client.Configuration()
        configuration.api_key = {"authorization": "Bearer " + self.token}
        configuration.host = self.api_host
        # 跳过ssl验证
        configuration.verify_ssl = False

        client1 = api_client.ApiClient(configuration=configuration)
        api = core_v1_api.CoreV1Api(client1)
        return api

    def health_check(self):
        api = self.get_api()
        system_pods = []
        try:
            for pod in api.list_namespaced_pod('kube-system').items:
                system_pods.append(pod.metadata.name)
        except Exception as e:
            print(e)
            return False

        if system_pods:
            return True
        else:
            return False
