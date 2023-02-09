from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DeletePackageRequest(_message.Message):
    __slots__ = ["appPackageId", "hostIp"]
    APPPACKAGEID_FIELD_NUMBER: _ClassVar[int]
    HOSTIP_FIELD_NUMBER: _ClassVar[int]
    appPackageId: str
    hostIp: str
    def __init__(self, hostIp: _Optional[str] = ..., appPackageId: _Optional[str] = ...) -> None: ...

class DeletePackageResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class InstantiateRequest(_message.Message):
    __slots__ = ["appInstanceId", "appPackageId", "hostIp", "parameters"]
    class ParametersEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    APPINSTANCEID_FIELD_NUMBER: _ClassVar[int]
    APPPACKAGEID_FIELD_NUMBER: _ClassVar[int]
    HOSTIP_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    appInstanceId: str
    appPackageId: str
    hostIp: str
    parameters: _containers.ScalarMap[str, str]
    def __init__(self, appInstanceId: _Optional[str] = ..., appPackageId: _Optional[str] = ..., hostIp: _Optional[str] = ..., parameters: _Optional[_Mapping[str, str]] = ...) -> None: ...

class InstantiateResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class RemoveCfgRequest(_message.Message):
    __slots__ = ["hostIp"]
    HOSTIP_FIELD_NUMBER: _ClassVar[int]
    hostIp: str
    def __init__(self, hostIp: _Optional[str] = ...) -> None: ...

class RemoveCfgResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class TerminateRequest(_message.Message):
    __slots__ = ["appInstanceId", "hostIp"]
    APPINSTANCEID_FIELD_NUMBER: _ClassVar[int]
    HOSTIP_FIELD_NUMBER: _ClassVar[int]
    appInstanceId: str
    hostIp: str
    def __init__(self, appInstanceId: _Optional[str] = ..., hostIp: _Optional[str] = ...) -> None: ...

class TerminateResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class UploadCfgRequest(_message.Message):
    __slots__ = ["configFile", "hostIp"]
    CONFIGFILE_FIELD_NUMBER: _ClassVar[int]
    HOSTIP_FIELD_NUMBER: _ClassVar[int]
    configFile: bytes
    hostIp: str
    def __init__(self, hostIp: _Optional[str] = ..., configFile: _Optional[bytes] = ...) -> None: ...

class UploadCfgResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class UploadPackageRequest(_message.Message):
    __slots__ = ["appPackageId", "hostIp", "package"]
    APPPACKAGEID_FIELD_NUMBER: _ClassVar[int]
    HOSTIP_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_FIELD_NUMBER: _ClassVar[int]
    appPackageId: str
    hostIp: str
    package: bytes
    def __init__(self, appPackageId: _Optional[str] = ..., hostIp: _Optional[str] = ..., package: _Optional[bytes] = ...) -> None: ...

class UploadPackageResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...
