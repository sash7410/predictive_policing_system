# setup.py

from setuptools import setup, find_packages

# Read README.md if it exists
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A weather service using Kafka and OpenMeteo API"

setup(
    name="weather_service_v1",
    version="0.1.0",
    description="A weather service using Kafka and OpenMeteo API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        'kafka-python>=2.0.2',
        'python-dotenv>=1.0.0',
        'requests>=2.31.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'pylint>=2.17.0',
            'mypy>=1.5.0',
        ],
    },
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'weather-producer=scripts.start_producer:main',
            'weather-consumer=scripts.start_consumer:main',
        ],
    },
)