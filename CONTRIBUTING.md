# Contributing to Stock-Analysis-Assistant

Below are the guidelines for contributing to this project.

## Getting Started

### 1. Clone the repository

First, clone the project repository to your local machine:

```bash
git clone https://github.com/mlengineershub/Stock-Analysis-Assistant

cd Stock-Analysis-Assistant
```

### 2. Open the project in VSCode

```bash
code .
```

### Ensure Python is installed

Make sure you have Python 3.10 or above installed (I am working with the 3.11.9). You can check your Python version with:

```bash
python --version
```

### 4. Create a Conda environment (optional)

If you prefer to work in an isolated environment, you can create a Conda environment (this step is optional but recommended):

```bash
conda create --name <name_env> python=3.11.9
conda activate <name_env>
```

### 5. Install the project in editable mode

Once your environment is set up, install the project dependencies in editable mode:

```bash
pip install -e .
pip install -r requirements.txt
```

This will install the required dependencies (numpy and pandas for the moment) and set up the package for development.

## Working on the Project

### 1. Create a new branch

Before starting any work, create a new branch. I have enforced rules on the `main` branch, so no direct commits are allowed. To create a branch, use:

```bash
git checkout -b <your-branch-name>
```

### 2. Implement your changes

You can make your changes in the appropriate files. The structures you will work with are mainly located in the module `src/*.py`. Please note that this module should generally not be modified unless necessary for the task at hand.

### 3. Running Tests

Before submitting your changes, please ensure that all your code is properly tested with unit tests. All test files should be placed in the `tests/` folder and prefixed with `test_` (e.g., `test_*.py`).

To run the tests, use one of the following commands in the terminal:

```bash
# To run a specific test file
python tests/test_yourfile.py

### 4. Commit and push your changes

Once your changes are complete, commit and push them to your branch:

```bash
git add .
git commit -m "Description of your changes"
git push origin <your-branch-name>
```

### 5. Submit a Pull Request

After submitting your PR, please wait for a review. Feedback might be provided, and adjustments could be required before the PR is approved and merged.

## Notes

- Each push triggers a workflow that checks the code’s conformity with Flake8, so please ensure your code is clean, and it’s recommended to install the Flake8 extension in VSCode for real-time linting.
- Each push or pull request will automatically trigger a workflow that runs all unit tests located in the `tests/` folder. Please make sure your tests pass before creating a pull request.
