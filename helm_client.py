import os
from pathlib import Path
from pyhelm3 import Client
from kubernetes import client, config
import asyncio
import logging

K8S_CONFIG_PATH = "k8sconfigs"

base_dir = os.getcwd()
kubeConfigPath = os.path.abspath(os.path.join(base_dir, K8S_CONFIG_PATH))

if not os.path.exists(kubeConfigPath):
    logging.error("K8s config dir does not exist")


# TODO: Create a factory for the Helm client
class HelmClient:
    # Specify the kubeconfig file to use
    # client = Client(executable = "/path/to/helm")
    def __init__(self, hostIp):
        self.hostIp = hostIp
        kubeconfig = kubeConfigPath + "/" + hostIp
        if not os.path.exists(kubeconfig):
            logging.error("K8s config for this MEC host does not exist")

        self.client = Client(kubeconfig=os.path.abspath(kubeconfig))

    # List the deployed releases
    async def list_releases(self):
        releases = await self.client.list_releases(all=True, all_namespaces=True)
        for release in releases:
            revision = await release.current_revision()
            logging.debug(
                "[%s] [%s] [%s] [%s]",
                release.name,
                release.namespace,
                revision.revision,
                str(revision.status),
            )

    # Install or upgrade a release
    async def install_chart(self, releasename, chart_ref):
        chart = await self.client.get_chart(chart_ref=chart_ref)
        revision = await self.client.install_or_upgrade_release(
            release_name=releasename,
            chart=chart,
            atomic=False,
            cleanup_on_fail=True,
            wait=False,
        )
        logging.debug(
            "[%s] [%s] [%s] [%s]",
            revision.release.name,
            revision.release.namespace,
            revision.revision,
            str(revision.status),
        )

    # Uninstall a release
    #   Via the revision
    async def uninstall_chart(self, releasename, namespace):
        revision = await self.client.get_current_revision(
            releasename, namespace=namespace
        )
        await revision.release.uninstall()

    async def deploy_chart(self, appPkgRecord, appInsId):
        pass

    async def unDeploy_chart(self):
        pass


#   Or directly by name
# await client.uninstall_release("cert-manager", namespace = "cert-manager", wait = True)
if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s.%(msecs)03d - %(levelname)s:\t%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )
    hostIp = "172.30.16.2"
    #kubeconfig = kubeConfigPath + "/" + hostIp
    helm = HelmClient(hostIp)
    asyncio.run(helm.list_releases())
    asyncio.run(helm.install_chart("my-nginx", "nginx", "https://charts.bitnami.com/bitnami"))

    # asyncio.run(helm.uninstall_chart(releasename="my-nginx", namespace="default"))
