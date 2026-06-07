from setuptools import find_packages, setup
from typing import List

def get_requirements() -> List[str]:
    try:
        with open('requirements.txt','r') as file:
            requirements_list = [
                line.strip() for line in file.readlines()
                if line.strip() and line.strip() !='-e .'
            ]
            return requirements_list
    except FileNotFoundError:
        print("requirements.txt file not found . make sure exists !")
        return[]

setup(
    name="doctor-appointment-agentic",
    version="0.0.1",
    author="Shree Joshi",
    author_email="Shreejoshi1805@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
    python_requires=">=3.10",  # Ensure compatible Python versi

    )
