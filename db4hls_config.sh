# Create folder project structure
mkdir syn_report_zip
mkdir syn
mkdir tcl_scripts
mkdir venv

# Create virtual environment and install required modules
virtualenv -p python3 ./venv
#python3.7 -m venv venv
source ./venv/bin/activate
./venv/bin/pip install -r requirements.txt 
