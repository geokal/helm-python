"""The Python AsyncIO implementation of the GRPC LcmService server."""

import asyncio
import logging
import re
import grpc
import os
import pathlib
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
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        logging.error("Error: Creating directory. %s ", path)


def delete_dir(path):
    pass


def validate_uuid(uuid):
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


class LcmService(lcmservice_pb2_grpc.LCMServicer):
    async def uploadConfig(self, request_iterator, context):
        data = bytearray()
        logging.info("UploadConfig Method called by client...")
        # try:
        #     request = next(request_iterator)
        # except StopIteration:
        #     raise RuntimeError("Failed to receive UploadConfig request")
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
                filepath = f"{packageFilePath}{os.path.sep}{packageId}.csar"
            data.extend(request.package)
        with open(filepath, "ab") as f:
            f.write(data)
        logging.info("Uploaded package request is successful")
        return lcmservice_pb2.UploadPackageResponse(status="Success!")

    async def instantiate(self, request, context):
        logging.info("Instantiate Method called by client...")
        param = {}
        if request.appInstanceId and validate_uuid(request.appInstanceId):
            logging.debug(
                "Receiving an Instantiate request's appInstanceId [%s]",
                request.appInstanceId,
            )
            instanceId = request.appInstanceId

        elif request.appPackageId and validate_uuid(request.appPackageId):
            logging.debug(
                "Receiving an Instantiate request's appPackageId [%s]",
                request.appPackageId,
            )
            packageId = request.appPackageId

        elif request.hostIp and validate_ipv4(request.hostIp):
            logging.debug(
                "Receiving an Instantiate request's MEC hostIp [%s]",
                request.hostIp,
            )
            hostIp = request.hostIp
        elif request.parameters:
            logging.debug("Receiving an Instantiate request's parameters")
            dict = {"ak", "sk"}
            for item in dict:
                if item in request.parameters:
                    param[item] = request.parameters[item]
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
