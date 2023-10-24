import os
import sys
from pathlib import Path
from typing import Dict, Optional
from zipfile import ZipFile

from slither_core.slither import Slither
from crytic_compile import CryticCompile, InvalidCompilation, is_supported
from solc_select.solc_select import switch_global_version
import join.compile.solc_parse.parser_function as ps


class Join():
    def __init__(self, target: str, **kwargs) -> None:
        self.target_path = os.path.abspath(target)
        self.target_name = []
        self.crytic_compile = []
        self.compilation_units: Dict[str, Slither] = {}

        try:
            if os.path.isdir(self.target_path):
                self.target_list = self.find_all_solidity_files('.sol')
                self.crytic_compile.extend(self.get_crytic_compile_list())
                for crytic, filename in zip(self.crytic_compile, self.target_name):
                    self.compilation_units[filename] = Slither(crytic)

            elif os.path.isfile(self.target_path):
                if self.target_path.endswith('.sol'):
                    version = self.parse(self.target_path)
                    self.select_compile_version(version)
                    self.crytic_compile.append(CryticCompile(self.target_path))

                    self.compilation_units[os.path.basename(
                        self.target_path)] = Slither(self.crytic_compile[0])
                elif self.target_path.endswith('.zip') or is_supported(self.target_path):
                    self.crytic_compile.extend(self.load_from_zip())
                    for crytic, filename in zip(self.crytic_compile, self.target_name):
                        self.compilation_units[filename] = Slither(crytic)
        except InvalidCompilation:
            print('Not supported file type')
            sys.exit(0)

    def find_all_solidity_files(self, extension: str):
        target_list = []
        for root, dirs, files in os.walk(self.target_path):
            for file in files:
                if file.endswith(extension):
                    file_path = os.path.join(root, file)
                    target_list.append(file_path)
        return target_list

    def get_versions(self, file):
        content = ps.get_solidity_source(file)
        sign, version = ps.parse_solidity_version(content)
        return sign, version

    def select_compile_version(self, version: str):
        try:
            if (self.check_installed_version(version)):
                switch_global_version(version, True)
            else:
                ps.install_solc(version)
                switch_global_version(version, True)
        except:
            print('Failed to switch compile versions')

    def parse_all_version_to_dict(self):
        version_list = ps.get_version_list()
        versions = version_list.keys()

        minor_versions_dict = {}
        for version in versions:
            minor_version = version.split('.')[1]
            minor_versions_dict[minor_version] = []

        for version in versions:
            minor_version = version.split('.')[1]
            minor_versions_dict[minor_version].append(version)

        return minor_versions_dict

    def check_installed_version(self, version):
        if "VIRTUAL_ENV" in os.environ:
            HOME_DIR = Path(os.environ["VIRTUAL_ENV"])
        else:
            HOME_DIR = Path.home()
        SOLC_SELECT_DIR = HOME_DIR.joinpath(".solc-select")
        ARTIFACTS_DIR = SOLC_SELECT_DIR.joinpath("artifacts")

        for _, _, files in os.walk(ARTIFACTS_DIR):
            for file in files:
                installed_version = file.split('-')[1]
                if (installed_version == version):
                    return True
        return False

    def parse(self, file_path):
        sign, version = self.get_versions(file_path)
        version_list = ps.get_version_list()

        if len(version) != 1:
            sign, version = ps.compare_version(sign, version)
        sign = sign[0]
        version = version[0]

        index = ps.find_matching_index(version, version_list)

        if sign == '<':
            version = version_list[index - 1]
        elif sign == '>':
            version = version_list[index + 1]
        elif (sign == '^' or sign == '~'):
            version = ps.get_highest_version(version_list, version)
        elif (sign == '=' or sign == '>=' or sign == '<=') or (not sign and version):
            version = version
        else:
            print("incorrect sign")
        return version

    def get_crytic_compile_list(self):
        compilation_units = []
        version = '0.8.0'  # default
        for file in self.target_list:
            try:
                self.target_name.append(os.path.basename(file))
                version = self.parse(file)
                if (len(version) > 0):
                    self.select_compile_version(version)
                compilation_units.append(CryticCompile(file))
            except:
                print('compile error')
        return compilation_units

    def load_from_zip(self):
        compilation_units = []
        target_list = []
        with ZipFile(self.target_path, "r") as file_desc:
            for project in file_desc.namelist():
                if project.endswith('.sol'):
                    target_list.append(os.path.join(
                        os.path.dirname(self.target_path), project))
            for file in target_list:
                self.target_name.append(os.path.basename(file))
                try:
                    version = self.parse(file)
                    if len(version) > 0:
                        self.select_compile_version(version)
                    compilation_units.append(CryticCompile(file))
                    print('compile success')
                except:
                    print('not .sol file')

        return compilation_units
