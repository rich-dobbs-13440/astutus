import setuptools
import setuptools.command.install
import setuptools.command.develop
import os
import os.path


class PostDevelopCommand(setuptools.command.develop.develop):
    """Post-installation for development mode."""
    def run(self):
        setuptools.command.develop.develop.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION


class PostInstallCommand(setuptools.command.install.install):
    """Post-installation for installation mode."""
    def run(self):
        # Note:  The command will be run in the context of the installed package
        #        such as a virtual environment.  So imports must be done
        #        within the function itself.
        import os
        import os.path
        import shutil
        import astutus.usb
        # Create the user's data directory if needed
        setuptools.command.install.install.run(self)
        user_data_dir = os.path.expanduser('~/.astutus')
        os.makedirs(user_data_dir, exist_ok=True)
        # Move the device configurations to the user's directory
        # so that the user can customize them as needed.
        source_path = os.path.join(astutus.usb.__path__, 'device_configurations.json')
        destin_path = os.path.join(user_data_dir, 'device_configurations.json')
        shutil.copyfile(source_path, destin_path)


with open("../README.rst", "r") as fh:
    long_description = fh.read()


# Create list for package data manually, since wildcard are not universally supported
# and are poorly documented at this time. Might be redundant with some setuptools
# functionality, but it works.
def get_package_data_list(root_dir, dirname):
    items = []
    for dirpath, _, _ in os.walk(os.path.join(root_dir, dirname)):
        item = os.path.relpath(dirpath, root_dir)
        if item == dirname:
            # Don't want the data directory itself, only subdirectories
            continue
        if '__pycache__' in item:
            continue
        items.append(os.path.join(item, '*'))
    return items


package_data = get_package_data_list('../src/astutus', 'web')
package_data.append("usb/device_configurations.json")


setuptools.setup(
    long_description=long_description,
    long_description_content_type="text/rst",
    package_dir={'': "../src/"},
    packages=[
        'astutus',
        'astutus.db',
        'astutus.log',
        'astutus.web',
        'astutus.raspi',
        'astutus.usb',
        'astutus.util',
    ],
    package_data={
        'astutus': package_data,
    },
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    entry_points={
        'console_scripts': ['astutus-usb-tree=astutus.usb.tree:main']
    }
)
