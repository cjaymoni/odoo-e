FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libpq-dev \
    gcc \
    node-less \
    npm \
    && rm -rf /var/lib/apt/lists/*

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
EXPOSE 8069

# Entrypoint and default command
ENTRYPOINT ["/opt/odoo/entrypoint.sh"]
CMD ["python3", "-m", "odoo", "-c", "odoo.conf"]
