# Set up the development environment
## Prerequisites
- [Conda/Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- Linux/macOS (some libraries do not have Windows variants)
## Installation
1. Clone the repository
2. Open a terminal and navigate to the repository
3. Create a new conda environment + install the required packages
```bash
conda env create -f environment.yml
```
4. Activate the environment
```bash
conda activate ip_analysis_tool
```
5. Try launching the tool
```bash
python -m ip_analysis_tool/ip_analysis_tool.py
```
6. If the tool launches successfully, you're all set up!
## Building the package
- This is useful for distributing the tool to others, without the hassle of installing Conda and other dependencies, it's a single standalone executable
1. Open a terminal and navigate to the repository
2. Build the package
```bash
pyinstaller ip_analysis_tool.spec
```
3. The executable will be in the `dist` folder