"""
Setup script for nacos-py package.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nacos-py",
    version="0.1.0",
    author="Mars",
    author_email="",
    description="Python client for Alibaba Nacos - Service Discovery and Configuration Management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marsbot-ai/nacos-py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="nacos service-discovery configuration-management microservices",
    project_urls={
        "Bug Reports": "https://github.com/marsbot-ai/nacos-py/issues",
        "Source": "https://github.com/marsbot-ai/nacos-py",
    },
)
