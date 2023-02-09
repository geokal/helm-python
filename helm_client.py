import os
from pathlib import Path
from pyhelm3 import Client
import asyncio
import logging

K8S_CONFIG_PATH = "k8sconfigs"

parent_dir = Path().absolute()
Path.cwd()
kubeConfigPath = os.path.abspath(os.path.join(parent_dir, K8S_CONFIG_PATH))

if os.path.exists(kubeConfigPath):
    print("Success")


class HelmClient(object):
    # Specify the kubeconfig file to use
    # client = Client(executable = "/path/to/helm")
    def __init__(self, kubeconfig, hostIp):
        self.kubeconfig = kubeconfig
        self.hostIp = hostIp
        self.client = Client()

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
    async def install_chart(self, releasename, chartname, repo, version):
        chart = await self.client.get_chart(chartname, repo=repo, version=version)
        revision = await self.client.install_or_upgrade_release(
            release_name=releasename, chart=chart, atomic=True, wait=True
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
    async def uninstall_chart(self, releasename):
        revision = await self.client.get_current_revision(
            releasename, namespace="default"
        )
        await revision.release.uninstall(wait=True)


#   Or directly by name
# await client.uninstall_release("cert-manager", namespace = "cert-manager", wait = True)
if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s.%(msecs)03d - %(levelname)s:\t%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )
    hostIp = "172.23.18.56"
    kubeconfig = f"{kubeConfigPath}{os.sep}{hostIp}.yaml"
    helm = HelmClient(kubeconfig, hostIp)
    # asyncio.run(
    #     helm.install_chart(
    #         "my-release", "nginx", "https://charts.bitnami.com/bitnami", "13.2.23"
    #     )
    # )
    asyncio.run(helm.list_releases())
    # asyncio.run(helm.uninstall_chart("my-release"))
