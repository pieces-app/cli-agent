from setuptools import setup, find_packages

setup(
    name='pieces',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'aenum==3.1.15',
        'certifi==2023.11.17',
        'charset-normalizer==3.3.2',
        'pydantic==1.10.13',
        'pyperclip==1.8.2',
        'requests==2.31.0',
        'typing-extensions==4.9.0',
        'urllib3==2.0.7',
        'websocket-client==1.7.0',
        'pieces-os-client==1.2.2',
        'openapi_client'
    ],
    entry_points={
        'console_scripts': [
            'pieces=app:main'  # Adjust the method to your main function
        ]
    },
)
