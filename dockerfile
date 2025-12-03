# Dockerfile

# ============================================
# STAGE 1: Use Python as our base image
# ============================================
FROM python:3.10-slim

# ============================================
# STAGE 2: Set up the working directory
# ============================================
# This is like creating a folder inside the container
WORKDIR /app

# ============================================
# STAGE 3: Install system dependencies
# ============================================
# Some Python packages need these to install properly
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# STAGE 4: Copy and install Python dependencies
# ============================================
# We copy requirements.txt first (Docker caching optimization)
COPY requirements.txt .

# Install all Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# STAGE 5: Copy our application code
# ============================================
# Copy everything from current folder to /app in container
COPY . .

# ============================================
# STAGE 6: Download NLTK data (if needed)
# ============================================
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# ============================================
# STAGE 7: Expose the port our API runs on
# ============================================
EXPOSE 5000

# ============================================
# STAGE 8: Set environment variables
# ============================================
ENV FLASK_APP=api/app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# ============================================
# STAGE 9: Command to run when container starts
# ============================================
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]