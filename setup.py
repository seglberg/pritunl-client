from setuptools import setup
import os
import pritunl_client

setup(
    name='pritunl_client',
    version=pritunl_client.__version__,
    description='Pritunl openvpn client',
    long_description=open('README.rst').read(),
    author='Zachary Huff',
    author_email='zach.huff.386@gmail.com',
    url='https://github.com/pritunl/pritunl-client',
    download_url='https://github.com/pritunl/pritunl-client/archive/' + \
        '%s.tar.gz' % pritunl_client.__version__,
    keywords='pritunl, openvpn, vpn, management, client',
    packages=['pritunl_client'],
    license=open('LICENSE').read(),
    zip_safe=False,
    data_files=[
        ('img', [
            os.path.join('img', 'logo_dark.svg'),
            os.path.join('img', 'logo_disconnected_dark.svg'),
            os.path.join('img', 'logo_light.svg'),
            os.path.join('img', 'logo_disconnected_light.svg'),
        ]),
    ],
    entry_points={
        'console_scripts': [
            'pritunl_client = pritunl_client.__main__:client'],
    },
    platforms=[
        'Linux',
        'Windows',
        'MacOS',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking',
    ],
)
