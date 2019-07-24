"""
Description
===========

This module contains MULTIPLY File Ref Creators. The purpose of these is to extract file refs to an existing file.
"""

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

from abc import ABCMeta, abstractmethod
from multiply_core.util import FileRef
from multiply_core.variables import get_registered_variables
from typing import Optional
from datetime import datetime
import xml.etree.ElementTree as eT


class FileRefCreator(metaclass=ABCMeta):

    @abstractmethod
    def name(self) -> str:
        """The name of the data type supported by this creator."""

    @abstractmethod
    def create_file_ref(self, path: str) -> FileRef:
        """Creates a file ref to this file"""


class AWSS2L2FileRefCreator(FileRefCreator):

    def name(self) -> str:
        return 'AWS_S2_L2'

    def create_file_ref(self, path: str) -> FileRef:
        time = self._extract_time_from_metadata_file(path)
        return FileRef(path, time, time, 'application/x-directory')

    @staticmethod
    def _get_xml_root(xml_file_name: str):
        tree = eT.parse(xml_file_name)
        return tree.getroot()

    def _extract_time_from_metadata_file(self, filename: str) -> str:
        """Parses the XML metadata file to extract the sensing time."""
        root = self._get_xml_root(filename + '/metadata.xml')
        for child in root:
            for x in child.findall("SENSING_TIME"):
                time = x.text.replace('T', ' ').replace('Z', '')
                time = time[:time.rfind('.')]
                return time


class S2L2FileRefCreator(FileRefCreator):

    def name(self) -> str:
        return 'S2_L2'

    def create_file_ref(self, path: str) -> FileRef:
        time = self._extract_time_from_metadata_file(path)
        return FileRef(path, time, time, 'application/x-directory')

    @staticmethod
    def _get_xml_root(xml_file_name: str):
        tree = eT.parse(xml_file_name)
        return tree.getroot()

    def _extract_time_from_metadata_file(self, filename: str) -> str:
        """Parses the XML metadata file to extract the sensing time."""
        root = self._get_xml_root(filename + '/MTD_TL.xml')
        for child in root:
            for x in child.findall("SENSING_TIME"):
                time = x.text.replace('T', ' ').replace('Z', '')
                time = time[:time.rfind('.')]
                return time


class VariableFileRefCreator(FileRefCreator):

    def __init__(self, variable_name: str):
        self._name = variable_name

    def name(self) -> str:
        return self._name

    def create_file_ref(self, path: str) -> FileRef:
        end_of_path = path.split('/')[-1]
        date_part = end_of_path.split('_')[-1].split('.tif')[0]
        time = datetime.strptime(date_part, "A%Y%j")
        time = datetime.strftime(time, '%Y-%m-%d')
        return FileRef(path, time, time, 'image/tiff')


class FileRefCreation(object):

    def __init__(self):
        self.FILE_REF_CREATORS = []
        self.add_file_ref_creator(AWSS2L2FileRefCreator())
        self.add_file_ref_creator(S2L2FileRefCreator())
        variables = get_registered_variables()
        for variable in variables:
            self.add_file_ref_creator(VariableFileRefCreator(variable.short_name))

    def add_file_ref_creator(self, file_ref_creator: FileRefCreator):
        self.FILE_REF_CREATORS.append(file_ref_creator)

    def get_file_ref(self, data_type: str, path: str) -> Optional[FileRef]:
        for file_ref_creator in self.FILE_REF_CREATORS:
            if file_ref_creator.name() == data_type:
                return file_ref_creator.create_file_ref(path)
