FROM python:3.11-slim

# Install system dependencies

RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build dependencies
    build-essential \
    gcc \
    g++ \
    # PostgreSQL client
    postgresql-client \
    # Python dependencies
    python3-dev \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    # Fonts and rendering
    fonts-noto-cjk \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    libtiff5-dev \
    zlib1g-dev \
    liblcms2-dev \
    # Wkhtmltopdf dependencies
    fontconfig \
    xfonts-base \
    xfonts-75dpi \
    xfonts-utils \
    xvfb \
    libxrender1 \
    libxext6 \
    # Node.js and npm for rtlcss and less
    npm \
    nodejs \
    # Other utilities
    curl \
    wget \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf with architecture detection
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "arm64" ]; then \
        wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_arm64.deb -O wkhtmltox.deb; \
    else \
        wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb -O wkhtmltox.deb; \
    fi && \
    apt-get update && \
    apt-get install -y --no-install-recommends ./wkhtmltox.deb && \
    rm wkhtmltox.deb && \
    rm -rf /var/lib/apt/lists/*
    
RUN npm install -g rtlcss less less-plugin-clean-css

# Set work directory
WORKDIR /opt/odoo

# Copy source code
COPY . /opt/odoo

# Copy entrypoint and wait-for-psql script
COPY entrypoint.sh /opt/odoo/entrypoint.sh
COPY wait-for-psql.py /opt/odoo/wait-for-psql.py
RUN chmod +x /opt/odoo/entrypoint.sh

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose Odoo port
EXPOSE 8069 8072

# Entrypoint and default command
ENTRYPOINT ["/opt/odoo/entrypoint.sh"]
CMD ["python3", "-m", "odoo", "-c", "odoo.conf"]
