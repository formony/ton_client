from setuptools import setup
from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

pfile = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pfile['packages'], r=False)
test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)


setup(
    author='Oleg Gaidukov',
    name='ton_client',
    version='0.5',
    packages=['ton_client'],
    test_suite='testsuite',
    install_requires=requirements,
    # setup_requires=[
    #     'flake8',
    #     'wheel',
    #     'pipenv'
    # ],
    package_data={
        'ton_client': [
            'distlib/darwin/*',
            'distlib/linux/*',
        ]
    },
    zip_safe=True,
    tests_require=test_requirements,
    python_requires='>=3.7'
)
