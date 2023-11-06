import re
import os
import requests
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union

if "VIRTUAL_ENV" in os.environ:
    HOME_DIR = Path(os.environ["VIRTUAL_ENV"])
else:
    HOME_DIR = Path.home()
    
SOLC_PARSER_DIR = HOME_DIR.joinpath(".solc-select")
SOLC_BINARIES_DIR = SOLC_PARSER_DIR.joinpath("artifacts")

class SolcParser:
    def __init__(self, target:str):
        self._target = target
        self._file_name= os.path.basename(target)
        self._file_contents = None
        self._release_version_list = self.release_version_list()
        
        self._version_list = self.version_list
        self._intalled_solc_versions = List[str]
        self._current_solc_version = Union[str, None]
        
        self._solc_binary_path = None
        self._solc_binary_version= None


    #######################################
    ############# Information #############
    #######################################
    @property
    def file_contents(self) -> str:
        with open(self._target, 'r') as f:
            self._file_contents = f.read()
        return self._file_contents
    
    def release_version_list(self) -> Dict[str, str]:
        url = f"https://binaries.soliditylang.org/macosx-amd64/list.json"
        list_json = requests.get(url).content
        self._release_version_list = json.loads(list_json)["releases"]
        return self._release_version_list
    
    @property
    def version_list(self) -> List[str]:
        self._version_list = list(self._release_version_list.keys())
        return self._version_list


    @property
    def intalled_solc_versions(self) -> List[str]:
        self._intalled_solc_versions = [str(p.name).replace("solc-", "") for p in SOLC_BINARIES_DIR.iterdir() if p.is_dir()]
        return self._intalled_solc_versions

    @property
    def current_solc_version(self) -> Optional[str]:
        if os.path.exists(f"{SOLC_PARSER_DIR}/global-version"):
            with open(f"{SOLC_PARSER_DIR}/global-version", "r", encoding="utf-8") as f:
                self._current_solc_version = f.read()
                return self._current_solc_version
        else:
            return None

    @property
    def solc_binary_path(self) -> str:
        self._solc_binary_path = subprocess.check_output(["which", "solc"], encoding='utf-8').strip()
        return self._solc_binary_path

    
    #########################################
    ############# Parse version #############
    #########################################
    def parse_version_in_file_contents(self):
        pattern = r".*pragma solidity.*"
        pragma_lines = re.findall(pattern, self.file_contents)
        version = []
        sign = []
        for pragma_match in pragma_lines:
            condition_pattern = r"(\^|=|~|>=|<=|>|<)?\s*([0-9]+\.[0-9]+(\.[0-9]+)?)"
            condition_matches = re.findall(condition_pattern, pragma_match)
            for condition_match in condition_matches:
                sign.append(condition_match[0].strip()
                            if condition_match[0] else "")
                version.append(condition_match[1].strip())
        return sign, version


    ########################################
    ############ Check version #############
    ########################################
    def check_version(self, version) -> bool:
        for v in version:
            if v not in self._version_list:
                return False
            else:
                return True

    # def check_installed_version(version):
    #     for _, _, files in os.walk(SOLC_BINARIES_DIR):
    #         for file in files:
    #             installed_version = file.split('-')[1]
    #             if (installed_version == version):
    #                 return True
    #     return False

    ###############################################
    ############# Select solc version #############
    ###############################################
    def find_matching_index(self, versions):
        for i, v in enumerate(self._version_list):
            if versions == v:
                return i
        return None

    def compare_version(self, sign_list):
        min_version = min(self._version_list)
        min_index = self._version_list.index(min_version)
        return list([sign_list[min_index]]), list([min_version])

    def get_highest_version(self, target_version, target_index):
        matching_versions = []
        target_major_minor = '.'.join(target_version.split('.')[:2])
        for v in self._version_list:
            if v.startswith(target_major_minor):
                matching_versions.append(v)
        target_index = matching_versions.index(target_version)
        
        if target_version == matching_versions[0]:
            return matching_versions[target_index]
        else:
            return matching_versions[target_index -1]

    #########################################################
    ############# Install/Uninstall/Switch solc #############
    #########################################################
    def install_solc(self):
        artifact_file_dir = SOLC_BINARIES_DIR.joinpath(f"solc-{self._solc_binary_version}")
        if os.path.exists(artifact_file_dir):
            # print(f"'{self._solc_binary_version}' is already installed.")
            return False
        
        artifacts = self._release_version_list
        url = f"https://binaries.soliditylang.org/macosx-amd64/" + \
            artifacts.get(self._solc_binary_version)
        Path.mkdir(artifact_file_dir, parents=True, exist_ok=True)
        print(f"Installing solc '{self._solc_binary_version}'...")

        response = requests.get(url)
        with open(artifact_file_dir.joinpath(f"solc-{self._solc_binary_version}"), "wb") as file:
            file.write(response.content)

        self._solc_binary_path = artifact_file_dir.joinpath(f"solc-{self._solc_binary_version}")
        os.chmod(self._solc_binary_path, 0o775)
        print(f"Version '{self._solc_binary_version}' installed.")
        return True

    def uninstall_solc(self):
        artifact_file_dir = SOLC_BINARIES_DIR.joinpath(f"solc-{self._solc_binary_version}")
        if os.path.exists(artifact_file_dir):
            print(f"Uninstalling solc '{self._solc_binary_version}'...")
            shutil.rmtree(artifact_file_dir)
            print(f"Version '{self._solc_binary_version}' uninstalled.")
            if self._solc_binary_version == self.current_solc_version():
                os.remove(f"{SOLC_PARSER_DIR}/global-version")
                print(
                    f"Version '{self._solc_binary_version}' was the global version. Switching to version.")
        else:
            print(
                f"'{self._solc_binary_version}' is not installed. Use 'solc-parser --list' to see all available versions.")
            return

    def switch_global_version(self, always_install: bool) -> None:
        if self._solc_binary_version in self.intalled_solc_versions:
            with open(f"{SOLC_PARSER_DIR}/global-version", "w", encoding="utf-8") as f:
                f.write(self._solc_binary_version)
            print("Switched global version to", self._solc_binary_version)
        elif self._solc_binary_version in self._version_list:
            if always_install:
                self.install_solc()
                self.switch_global_version(always_install)
            else:
                raise argparse.ArgumentTypeError(
                    f"'{self._solc_binary_version}' must be installed prior to use.")
        else:
            raise argparse.ArgumentTypeError(f"Unknown version '{self._solc_binary_version}'")
   
    def run_parser(self):
        sign, version = self.parse_version_in_file_contents()
        
        if self.check_version(version) == False:
            print("incorrect version")
            return
        
        if len(version) != 1:
            sign, version = self.compare_version(sign, version)

        sign = sign[0]
        version = version[0]
        index = self.find_matching_index(version)

        if sign == '<':
            solc_version = self._version_list[index - 1]
        elif sign == '>':
            solc_version = self._version_list[index + 1]
        elif (sign == '^' or sign == '~'):
            solc_version = self.get_highest_version(version, index)
        elif (sign == '=' or sign == '>=' or sign == '<=') or (not sign and version):
            solc_version = version
        else:
            print("incorrect sign")
            return
        
        self._solc_binary_version = solc_version
        flag= self.install_solc()
        self.switch_global_version(flag)