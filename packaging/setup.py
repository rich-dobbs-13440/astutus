import setuptools

with open("../README.rst", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    long_description=long_description,
    long_description_content_type="text/rst",
    package_dir={'': "../src/"},
    packages=['astutus', 'astutus.web', 'astutus.raspi'],
    package_data={
        'astutus': [
            'web/static/**/*',
            'web/static/_docs/_static/*',
            'web/static/_docs/_static/**/*'
        ]
    }
)
