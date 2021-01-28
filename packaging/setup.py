import setuptools
import setuptools.command.install
import setuptools.command.develop
import os
import os.path
import re
import pytz
import datetime


with open("../README.rst", "r") as fh:
    long_description = fh.read()

# Use PEP 440 compliant versioning.
#   * Use a pre-release segement to timestamp build - useful for PyPI publishing.
#   * At this time, not distinguishing between production and other builds.
#

# Version is in this format:  __version__ = '0.1.5'
with open("../src/astutus/version.py") as fh:
    version_content = fh.read()

pattern = r"__version__\s*=\s*'([^']+)'"
matches = re.search(pattern, version_content)
major_minor_patch_string = matches.group(1)

utcmoment = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
denvernow = utcmoment.astimezone(pytz.timezone('America/Denver'))
# Don't use dots within timestamp, since we're using timestamp as a number for PEP 440.
# With this abbreviated timestamp, the patch version must be incremented come January 1st,
# so that the overall version number monotonically increases!
timestamp_number = denvernow.strftime("%m%d%H%M")

# For now, take all builds as being final.
version_string = f'{major_minor_patch_string}.{timestamp_number}'


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
        if item == 'wheels':
            items.append(os.path.join(item, 'purpose.txt'))
            continue
        items.append(os.path.join(item, '*'))
    return items


package_data = get_package_data_list('../src/astutus', 'web')
package_data.append("usb/device_configurations.json")
package_data.append("wheels/purpose.txt")


setuptools.setup(
    setup_requires=['wheel'],  # Trying to avoid error in building wheel for treelib, future from tar.gz source
    version=version_string,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    package_dir={'': "../src/"},
    packages=[
        'astutus',
        'astutus.db',
        'astutus.log',
        'astutus.web',
        'astutus.raspi',
        'astutus.sphinx',
        'astutus.usb',
        'astutus.util',
        'astutus.wheels',
    ],
    package_data={
        'astutus': package_data,
    },
    entry_points={
        'console_scripts': [
            'astutus-usb-tree=astutus.usb.tree:main',
            'astutus-web-app=astutus.web.flask_app:run_with_standard_options',
        ]
    }
)
