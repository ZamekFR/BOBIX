from setuptools import setup, find_packages

setup(
    name='mypackage',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # tutaj możesz umieścić wymagane zależności, np.
        # 'numpy',
    ],
    author='CITREL',
    author_email='franciszek.zamosny@gmail.com',
    description='BOBIX CAD by CITREL LOGS',
    url='https://github.com/ZamekFR/BOBIX',  # opcjonalnie
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
