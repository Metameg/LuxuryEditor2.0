import importlib
import subprocess
import pkg_resources

libraries = [
                {"package_name": "streamlit", "version": "1.26.0"},
                {"package_name": "moviepy", "version": "1.0.3"},
                {"package_name": "Pillow", "version": "9.4.0"}
            ]


def check_and_install_library(library_name, desired_version=None):
    try:
        # Try to import the library
        importlib.import_module(library_name)

        # Check the installed version if desired_version is provided
        if desired_version:
            installed_version = pkg_resources.get_distribution(library_name).version
            if installed_version == desired_version:
                print(f"{library_name} version {desired_version} is already installed.")
            else:
                print(f"Installed version of {library_name} is {installed_version}, but {desired_version} is required.")
                print(f"Upgrading {library_name} to version {desired_version}...")
                subprocess.check_call(["pip", "install", f"{library_name}=={desired_version}"])
                print(f"{library_name} has been upgraded to version {desired_version}.")
        else:
            print(f"{library_name} is already installed.")

    except ImportError:
        # If the library is not installed, install it
        print(f"{library_name} is not installed. Installing...")
        try:
            if desired_version:
                subprocess.check_call(["pip", "install", f"{library_name}=={desired_version}"])
                print(f"{library_name} version {desired_version} has been successfully installed.")
            else:
                subprocess.check_call(["pip", "install", library_name])
                print(f"{library_name} has been successfully installed.")
        except Exception as e:
            print(f"Error installing {library_name}: {str(e)}")

for library in libraries:
    check_and_install_library(library["package_name"], library["version"])