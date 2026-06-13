ollama pull llama3.2:1b

cd /opt
sudo wget "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" -O firefox.tar.xz
sudo tar -xJf firefox.tar.xz
sudo ln -sf /opt/firefox/firefox /usr/local/bin/firefox

sudo apt update
sudo apt install -y \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libasound2t64 \
    libxt6 \
    libx11-xcb1 \
    libxcb-shm0 \
    libxcb-dri3-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    imagemagick

firefox --version