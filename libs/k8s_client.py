from kubernetes import client, watch
from kubernetes.client.rest import ApiException


class Kubernetes(object):
    def __init__(self, api_host, token):
        self.api_host = api_host
        self.token = token

    def get_configuration(self):
        configuration = client.Configuration()
        configuration.api_key = {"authorization": "Bearer " + self.token}
        configuration.host = self.api_host
        # 跳过ssl验证
        configuration.verify_ssl = False

        return configuration

    def health_check(self):
        configuration = self.get_configuration()
        with client.ApiClient(configuration) as api_client:
            api_instance = client.CoreV1Api(api_client)
            system_pods = []
            try:
                for pod in api_instance.list_namespaced_pod('kube-system').items:
                    system_pods.append(pod.metadata.name)
            except ApiException as e:
                print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
                return False

            if system_pods:
                return True
            else:
                return False

    def get_namespace_list(self):
        ns_list = []
        configuration = self.get_configuration()
        with client.ApiClient(configuration) as api_client:
            api_instance = client.CoreV1Api(api_client)
            try:
                for ns in api_instance.list_namespace().items:
                    ns_list.append(ns.metadata.name)
            except ApiException as e:
                print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)

        return ns_list

    def create_namespace(self, ns_name):
        configuration = self.get_configuration()
        with client.ApiClient(configuration) as api_client:
            api_instance = client.CoreV1Api(api_client)
            body = client.V1Namespace(metadata=client.V1ObjectMeta(name=ns_name))
            try:
                api_response = api_instance.create_namespace(body)
            except ApiException as e:
                print("Exception when calling CoreV1Api->create_namespace: %s\n" % e)
                api_response = e

        return api_response

    def delete_namespace(self, ns_name):
        configuration = self.get_configuration()
        with client.ApiClient(configuration) as api_client:
            api_instance = client.CoreV1Api(api_client)
            body = client.V1DeleteOptions()
            body.api_version = "v1"
            body.grace_period_seconds = 0

            try:
                api_response = api_instance.delete_namespace(ns_name, body=body)
            except ApiException as e:
                print("Exception when calling CoreV1Api->delete_namespace: %s\n" % e)
                api_response = e

        return api_response
