from kubernetes import client, config


class KubernetesClientFactory:
    @staticmethod
    def get_client(hostIp):
        # TODO: add the hostIp parameter in order to find the accosiated k8s_config file
        config_file = "/path/to/kube/k8sconfigs/" + hostIp + ".yaml"
        # TODO: Check if above file exist
        k8s_config = config.load_kube_config(config_file=config_file)
        api_client = config.new_client_from_config_dict(k8s_config)
        return client.CoreV1Api(api_client)


if __name__ == "__main__":
    api = KubernetesClientFactory.get_client("192.168.2.1")
    namespaces = api.list_namespace()
    print(
        f"Current namespaces: {[namespace.metadata.name for namespace in namespaces.items]}"
    )
