import setuptools

with open("../README.rst", "r") as fh:
    long_description = fh.read()


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
        'astutus': [
            'web/static/*',
            # 'web/static/**/*',
            'web/static/_docs/_static/*',
            'web/static/_docs/_static/css/*',
            'web/static/_docs/_static/css/fonts/*',
            'web/static/_docs/_static/fonts/*',
            'web/static/_docs/_static/fonts/Lato/*',
            'web/static/_docs/_static/fonts/Lato/RobotoSlab/*',
            'web/static/_docs/_static/fonts/js/*',
            'web/static/_docs/_static/js/*',
            'web/static/_docs/source/*',
            # 'web/static/_docs/_static/**/*',
            'web/templates/*',
            # 'web/templates/**/*',l
        ]
    }
)
