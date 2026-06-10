#sudo apt-get install bash-completion # lowk unnecessary
git clone https://github.com/allesman/Ronkolas.git
cd Ronkolas
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# IMPORTANT: BEFORE UNPLUGGING:
sudo shutdown -h now