import setuptools
import setuptools.command.install
import setuptools.command.develop
import os
import os.path


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
    long_description_content_type="text/x-rst",
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
    entry_points={
        'console_scripts': ['astutus-usb-tree=astutus.usb.tree:main']
    }
)
