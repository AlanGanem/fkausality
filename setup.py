from pkg_resources import parse_version
from configparser import ConfigParser
import setuptools
assert parse_version(setuptools.__version__)>=parse_version('36.2')
from os import path


def get_requirements():
    """
    Return requirements  and dependency links as list.

   
    THANKS TO Gonzalo Ordiard at https://stackoverflow.com/questions/32688688/how-to-write-setup-py-to-include-a-git-repository-as-a-dependency
    """
    required = []
    dependency_links = []

    loc = path.abspath(path.dirname(__file__))

    with open(loc + '/requirements.txt') as f:
        requirements = f.read().splitlines()

    # Do not add to required lines pointing to Git repositories
    EGG_MARK = '#egg='
    for line in requirements:
        if line.startswith('-e git:') or line.startswith('-e git+') or \
                line.startswith('git:') or line.startswith('git+'):
            line = line.lstrip('-e ')  # in case that is using "-e"
            if EGG_MARK in line:
                package_name = line[line.find(EGG_MARK) + len(EGG_MARK):]
                repository = line[:line.find(EGG_MARK)]
                required.append('%s @ %s' % (package_name, repository))
                dependency_links.append(line)
            else:
                print('Dependency to a git repository should have the format:')
                print('git+ssh://git@github.com/xxxxx/xxxxxx#egg=package_name')
                print('got:')
                print(f'{line}')
        else:
            required.append(line)
    return required, dependency_links

if __name__ == '__main__':
    # note: all settings are in settings.ini; edit there, not here
    config = ConfigParser(delimiters=['='])
    config.read('settings.ini')
    cfg = config['DEFAULT']

    cfg_keys = 'version description keywords author author_email'.split()
    expected = cfg_keys + "lib_name user branch license status min_python audience language".split()
    for o in expected: assert o in cfg, "missing expected setting: {}".format(o)
    setup_cfg = {o:cfg[o] for o in cfg_keys}

    licenses = {
        'apache2': ('Apache Software License 2.0','OSI Approved :: Apache Software License'),
    }
    statuses = [ '1 - Planning', '2 - Pre-Alpha', '3 - Alpha',
        '4 - Beta', '5 - Production/Stable', '6 - Mature', '7 - Inactive' ]
    py_versions = '2.0 2.1 2.2 2.3 2.4 2.5 2.6 2.7 3.0 3.1 3.2 3.3 3.4 3.5 3.6 3.7 3.8'.split()

    #requirements = cfg.get('requirements','').split()
    requirements, dependency_links = get_requirements()    
    lic = licenses[cfg['license']]
    min_python = cfg['min_python']

    setuptools.setup(
        name = cfg['lib_name'],
        license = lic[0],
        classifiers = [
            'Development Status :: ' + statuses[int(cfg['status'])],
            'Intended Audience :: ' + cfg['audience'].title(),
            'License :: ' + lic[1],
            'Natural Language :: ' + cfg['language'].title(),
        ] + ['Programming Language :: Python :: '+o for o in py_versions[py_versions.index(min_python):]],
        url = cfg['git_url'],
        packages = setuptools.find_packages(),
        include_package_data = True,
        install_requires = requirements,
        dependency_links = cfg.get('dep_links','').split() + dependency_links,
        python_requires  = '>=' + cfg['min_python'],
        long_description = open('README.md').read(),
        long_description_content_type = 'text/markdown',
        zip_safe = False,
        entry_points = { 'console_scripts': cfg.get('console_scripts','').split() },
        **setup_cfg)

