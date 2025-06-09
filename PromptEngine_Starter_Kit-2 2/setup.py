from setuptools import setup, find_packages

setup(
    name="prompt_engine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["typer[all]", "pydantic"],
    entry_points={
        "console_scripts": [
            "prompt-engine=prompt_engine.cli:app",
        ],
    },
)
