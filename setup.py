from setuptools import setup, find_packages

setup(
    name="chart_builder",  # The name users will use to pip install
    version="0.1.0",
    description="A library for building customizable charts in Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Brandyn Hamilton",
    author_email="brandynham1120@gmail.com",
    url="https://github.com/yourusername/chart_builder",  # Link to your GitHub repo or documentation
    packages=find_packages(include=["chart_builder", "chart_builder.*"]),  # Include only chart_builder and its submodules
    install_requires=[
        "pandas",
        "numpy",
        "plotly",
        "kaleido",
        "svgwrite",                # Only keep necessary dependencies
        "pyairtable",
        "python-dotenv",
        "google-analytics-data",
        "google-auth-oauthlib",
        "google-api-python-client"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",        # Specify minimum Python version
    include_package_data=True,
    zip_safe=False,
)
