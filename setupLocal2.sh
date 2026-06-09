ollama pull llama3.2:1b

cd /opt
sudo wget "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" -O firefox.tar.bz2
sudo tar xjf firefox.tar.bz2
sudo ln -s /opt/firefox/firefox /usr/local/bin/firefox

firefox --version