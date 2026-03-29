"""Setup script for Diffron package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="diffron",
    version="0.1.0",
    author="Diffron Contributors",
    author_email="diffron@example.com",
    description="Git commit message and PR description generator using Lemonade",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/diffron/diffron",
    packages=find_packages(exclude=["tests", "hooks"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.0.0",
        "psutil>=5.9.0",
    ],
    extras_require={
        "git": ["gitpython>=3.1.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "diffron-install-hooks=diffron.cli:install_hooks_cli",
            "diffron-uninstall-hooks=diffron.cli:uninstall_hooks_cli",
            "diffron-pr=diffron.cli:pr_description_cli",
            "diffron-status=diffron.cli:status_cli",
        ],
    },
    include_package_data=True,
    package_data={
        "diffron": ["py.typed"],
    },
)
