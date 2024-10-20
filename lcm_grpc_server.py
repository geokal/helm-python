"""The implementation of the 'K8s Adapter' as a GRPC server using Python asyncio"""

import asyncio
import logging
import re
import tarfile
import zipfile
import grpc
import os
import pathlib
import pyfiglet as pyg
from helm_client import HelmClient
from kubernetes import client, config
from grpc_reflection.v1alpha import reflection
from protos import lcmservice_pb2
from protos import lcmservice_pb2_grpc

# Declare constants in a separate file called constant.py
K8S_CONFIG_PATH = "k8sconfigs"
APP_PACKAGES_PATH = "packages"

parent_dir = pathlib.Path().absolute()

configPath = os.path.abspath(os.path.join(parent_dir, K8S_CONFIG_PATH))
packagePath = os.path.abspath(os.path.join(parent_dir, APP_PACKAGES_PATH))


def create_dir(path):
    """
    Creates the directory for the specified path
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        logging.error("Error: Creating directory. %s ", path)
        return False
    return True


def delete_dir(path):
    """
    Function to delete/unlink the specified path
    """
    pass


def extract_csar(zip_file):
    """
    Extracts the zip/csar file in the current directory
    """
    zip_file_path = os.path.abspath(zip_file)

    """
    Extract a zip file including any nested zip files
    Delete the zip file(s) after extraction
    """
    with zipfile.ZipFile(zip_file, "r") as zfile:
        ext_path = os.path.join(
            # TODO: change to os.path.dirname(zip_file)
            os.path.dirname(zip_file),
            os.path.splitext(zip_file)[0],
        )
        zfile.extractall(path=ext_path)
    # os.remove(zippedFile)
    # for root, dirs, files in os.walk(ext_path):
    #     for filename in files:
    #         if re.search(r"\.zip$", filename):
    #             fileSpec = os.path.join(root, filename)
    #             extract_csar(fileSpec)
    logging.info(f"Extracted csar in [{ext_path}]")
    return ext_path


def make_k8s_client(kubeconfig: dict) -> client.CoreV1Api:
    """
    Creates a new K8s client using the provided kubeconfig
    """
    api_client = config.new_client_from_config_dict(kubeconfig)
    return client.CoreV1Api(api_client)


def create_namespace(namespace_name):
    """
    Create the given k8s namespace object using the K8s python client
    """
    # config.load_kube_config()
    # v1 = client.CoreV1Api()
    v1 = make_k8s_client(kubeconfig=K8S_CONFIG_PATH)
    body = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace_name))
    try:
        api_response = v1.create_namespace(body=body)
        logging.info(f"Namespace {api_response.metadata.name} created successfully.")
    except client.exceptions.ApiException as e:
        logging.error(f"Error creating namespace: {e}")


def get_helm_artifact_path(host_Ip, package_Id):
    """
    Gets the Chart directory for the specified hostIp and packageId
    """
    PkgPath = f"{packagePath}{os.sep}{package_Id}-{host_Ip}"

    list_PkgPath = [f.path for f in os.scandir(PkgPath) if f.is_dir()]

    app_path = list_PkgPath[0] + "/Artifacts/Deployment/Charts"
    try:
        arti_file_path = get_deploy_artifact(app_path, ".tgz")
    except:
        logging.error("Artifact not available in application package.")
    return arti_file_path


def get_deploy_artifact(directory_path, extension):
    """
    Finds files in a directory with a given file extension.

    Args:
        directory_path (str): The path of the directory to search in.
        extension (str): The file extension to search for (e.g. '.tgz').

    Returns:
        A list of file paths (str) in the directory that have the specified extension.
    """
    if not os.path.exists(directory_path):
        logging.error(f"Directory '{directory_path}' does not exist.")
        return []

    files = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith(extension):
            files.append(os.path.join(directory_path, file_name))
    return files[0]


def validate_uuid(uuid):
    """
    Validates if the input parameter is a valid UUID
    """
    if uuid is None:
        logging.error("uuid parameter required")
        return False
    uuid_pattern = re.compile(
        "[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z",
        re.I,
    )
    match = uuid_pattern.match(uuid)
    return bool(match)


def validate_ipv4(ip):
    """
    Validates if the input parameter is a valid IPv4 address
    """
    if ip is None:
        return False
    octets = ip.split(".")
    if len(octets) != 4:
        logging.error("Invalid ipv4 format")
        return False
    for octet in octets:
        if not octet.isdigit():
            logging.error("Invalid ipv4 format")
            return False
        if int(octet) < 0 or int(octet) > 255:
            logging.error("Invalid ipv4 format")
            return False
    return True


# TODO: Absctract class in a different file
class LcmService(lcmservice_pb2_grpc.LCMServicer):
    async def uploadConfig(self, request_iterator, context):
        data = bytearray()
        logging.info("UploadConfig Method called by client...")

        async for request in request_iterator:
            if request.hostIp:
                logging.info(
                    "Received an UploadConfig request for MEC host with IP [%s]",
                    request.hostIp,
                )
                hostIp = request.hostIp
            if request.configFile:
                logging.info("inside configFile write method for [%s]", hostIp)

                try:
                    if not os.path.exists(configPath):
                        os.makedirs(configPath)
                except OSError:
                    logging.error("Error: Creating directory. " + configPath)
                filepath = f"{configPath}{os.sep}{hostIp}"
            data.extend(request.configFile)
        with open(filepath, "wb") as f:
            f.write(data)
        logging.info("UploadConfig request is successful")
        return lcmservice_pb2.UploadCfgResponse(status="Success!")

    async def uploadPackage(self, request_iterator, context):
        data = bytearray()
        logging.info("UploadPackage Method called by client...")
        packageId = None
        hostIp = None

        async for request in request_iterator:
            if request.appPackageId and validate_uuid(request.appPackageId):
                logging.debug(
                    "Receiving an UploadPackage request's appPackageId [%s]",
                    request.appPackageId,
                )
                packageId = request.appPackageId

            elif request.hostIp and validate_ipv4(request.hostIp):
                logging.debug(
                    "Receiving an UploadPackage request's MEC hostIp [%s]",
                    request.hostIp,
                )
                hostIp = request.hostIp

            elif request.package:
                logging.debug(
                    "Inside UploadPackage write method for host [%s] and appId [%s]",
                    hostIp,
                    packageId,
                )
                create_dir(packagePath)
                packageFilePath = f"{packagePath}{os.path.sep}{packageId}-{hostIp}"
                create_dir(packageFilePath)
                csarFilePath = f"{packageFilePath}{os.path.sep}{packageId}.csar"
            data.extend(request.package)
        with open(csarFilePath, "ab") as f:
            f.write(data)

        try:
            extracted_csar = extract_csar(csarFilePath)
        except Exception as e:
            logging.error(e, exc_info=True)  # log exception info at CRITICAL log level
        logging.debug(extracted_csar)

        logging.info("Uploaded package request is successful")
        return lcmservice_pb2.UploadPackageResponse(status="Success!")

    async def instantiate(self, request, context):
        # https://github.com/grpc/grpc/blob/master/examples/python/helloworld/async_greeter_server_with_graceful_shutdown.py
        logging.info("Instantiate Method called by client...")
        param = {}

        if request.appInstanceId and validate_uuid(request.appInstanceId):
            logging.debug(
                "Receiving an Instantiate request's appInstanceId [%s]",
                request.appInstanceId,
            )
            # instance_Id = request.appInstanceId

        if request.appPackageId and validate_uuid(request.appPackageId):
            logging.debug(
                "Receiving an Instantiate request's appPackageId [%s]",
                request.appPackageId,
            )
            # package_Id = request.appPackageId

        if request.hostIp and validate_ipv4(request.hostIp):
            logging.debug(
                "Receiving an Instantiate request's MEC hostIp [%s]",
                request.hostIp,
            )
            # hostIp = request.hostIp

        if request.parameters:
            logging.debug("Receiving an Instantiate request's parameters")
            dict = {"ak", "sk"}
            for item in dict:
                if item in request.parameters:
                    param[item] = request.parameters[item]

        res = get_helm_artifact_path(request.hostIp, request.appPackageId)
        logging.debug("artifact found in [ %s ]", res)
        # res = "/home/ubuntu/helm-python/packages/e17d23de-e562-4c81-b242-0d3926a2255f-172.25.138.118/e17d23de-e562-4c81-b242-0d3926a2255f/Artifacts/Deployment/Charts/"

        # arti_tarfile = tarfile.open(res, "r:*")
        # logging.debug(arti_tarfile.getnames())
        # TODO: Read the Helm Chart values.yaml and take the namespace parameter from chart's values.yaml ->"appconfig"

        # TODO: Call the create_namespace function

        # TODO: If the namespace is not "default", create a Kubernetes NS object with the appInstId as name

        # TODO: Call helm_client.install_chart()
        helm = HelmClient(hostIp=request.hostIp)

        await helm.install_chart("my-release", res)

        return lcmservice_pb2.InstantiateResponse(status="Success!")


async def serve(address):
    server = grpc.aio.server()
    lcmservice_pb2_grpc.add_LCMServicer_to_server(LcmService(), server)
    SERVICE_NAMES = (
        lcmservice_pb2.DESCRIPTOR.services_by_name["LCM"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port(address)
    figlet_text = pyg.figlet_format("k8s Adapter", font="slant")
    print(figlet_text)
    logging.info("Lcm gRPC Server serving at [%s]" % (address))
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s.%(msecs)03d - %(levelname)s:\t%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )
    asyncio.run(serve("[::]:50051"))
