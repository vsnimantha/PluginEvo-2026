# Setup & Usage Guide

## Downloading the Repository
We noticed that some files cannot be opened by the annonymous repo. Therefore we recommend downloading the repo.
Clone or download this repository to your local machine.  
All **Test_Programs** and **Configs** are included and can be used directly with the **program_repos** and the **PluginSight application** without running the full loop.

---

## Installing Requirements

### Application Requirements
Each application inside **Program Repos** contains a `requirements` folder.  
Install all dependencies listed there before running any tests.

### Python Requirements (if applicable)
To install Python dependencies:

pip install -r requirements.txt

## System Requirements

Install the necessary system packages:

sudo apt update
sudo apt install gcc gcc-plugin-dev

We recommend installing GCC versions 10 through 14 for best compatibility with the plugins and test environment.

Note: This setup has been tested only on Ubuntu 22.04 and Ubuntu 24.04.


## Using Custom Configurations
1. Open the **plugin repository** you want to work with.  
2. Replace its existing configuration file with the config you want to run from this repo.  
3. Adjust the parameters in the configuration file to match your test scenario.

---

## GCC Plugin Setup
The required GCC plugins are located in the **GCC_Plugins** folder.  
Ensure these plugins are correctly set up in your environment before running any tests.
