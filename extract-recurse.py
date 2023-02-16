import os
import sys
import zipfile, re, os


def extract_nested_zip(zippedFile):
    """Extract a zip file including any nested zip files
    Delete the zip file(s) after extraction
    """
    with zipfile.ZipFile(zippedFile, "r") as zfile:
        ext_path = os.path.join(
            os.path.dirname(zippedFile), os.path.splitext(zippedFile)[0]
        )
        zfile.extractall(path=ext_path)
    # os.remove(zippedFile)
    # for root, dirs, files in os.walk(ext_path):
    #     for filename in files:
    #         if re.search(r"\.zip$", filename):
    #             fileSpec = os.path.join(root, filename)
    #             extract_nested_zip(fileSpec)


csar_file = (
    os.getcwd()
    + "/packages/5c54bf29-1b47-4c2b-a7e5-50cbd7049fd9-192.168.2.1/5c54bf29-1b47-4c2b-a7e5-50cbd7049fd9.csar"
)
extract_nested_zip(csar_file)
