from setuptools import setup, find_packages

setup(
    name='Stock-Analysis-Assistant',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'sentence-transformers'=='3.3.1',
    ],
    author='AIT SAID Azzedine, DJERFAF Ilyes, KESKES Nazim',
    author_email='ja_aitsaid@esi.dz, ilyes.djerfaf@etu-upsaclay.fr, nazim.keskes@etu-upsaclay.fr',
    description='A project for stock analysis assistance',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/mlengineershub/Stock-Analysis-Assistant',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)