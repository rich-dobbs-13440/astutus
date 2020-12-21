import setuptools


setuptools.setup(
    package_dir={'': "../src/"},
    # packages=setuptools.find_packages(),
    packages=['astutus', 'astutus.web'],
    package_data={
        'astutus': [
            'web/static/**/*',
            'web/static/_docs/_static/*',
            'web/static/_docs/_static/**/*'
        ]
    }
)
