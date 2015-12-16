# Allow conans to import ConanFile from here
# to allow refactors
from machinehub.model.conan_file import ConanFile
from machinehub.model.options import Options
from machinehub.model.settings import Settings
from machinehub.client.cmake import CMake
from machinehub.client.gcc import GCC
from machinehub.util.files import load
import os

version_file = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.txt"))
__version__ = load(version_file)
