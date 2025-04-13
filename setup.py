# setup.py
from setuptools import setup, find_packages

setup(
    name="expressai",
    version="0.1.0",
    author="Jaymes Dec",
    description="A creative Python library for expressive AI chat, vision, and voice projects.",
    packages=find_packages(),
    install_requires=[
        "openai>=1.14.0",
        "elevenlabs>=1.1.0",
        "pillow>=10.0.0",
        "ipython>=8.0.0"
    ],
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
