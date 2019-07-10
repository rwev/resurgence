from setuptools import setup

setup(name='setup',
      version='0.1.0',
      description='Restart a process when files are changed',
      author='rwev',
      author_email='rwev@protonmail.ch',
      url='https://github.com/rwev/resurgence',
      packages=['resurge'],
      entry_points={
            'console_scripts': ('resurgence = resurge.resurgence')
      },      install_requires=['psutil'],
      license='GNU GPL 3.0'
      )
