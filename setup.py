from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="filum-pain-point-agent",
    version="1.0.0",
    author="Filum.ai Team",
    author_email="support@filum.ai",
    description="AI Agent that analyzes customer pain points and recommends solutions from the Filum.ai platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/filum-ai/pain-point-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Customer Service",
        "Topic :: Office/Business :: Customer Service",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.6.0",
            "flake8>=3.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "filum-agent=src.cli:main",
        ],
    },
)
