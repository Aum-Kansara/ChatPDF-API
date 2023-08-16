sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11
ls -l /usr/bin/python3*
python3.11 --version
python3 -m pip install --upgrade pip
pip install --disable-pip-version-check -r requirements.txt