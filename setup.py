import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="localagent",
    version="0.0.1",
    author="nnpy",
    author_email="prasannatwenty@gmail.com",
    description="opengpt is a open implementation of GPT agents by openai.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/driscollis/arithmetic",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    include_package_data = True,
)