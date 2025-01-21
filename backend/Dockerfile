# Use the official Python 3.11 image based on Debian Bullseye
FROM python:3.11-bullseye

# (Optional) Install OpenJDK 17 if needed
# RUN apt-get update && \
#     apt-get install -y openjdk-17-jdk && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# Set environment variables for Java (if using Java)
# ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
# ENV JVM_PATH=${JAVA_HOME}/lib/server/libjvm.so

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the app
EXPOSE 5000

# Run the application using the Exec Form
CMD ["python", "server.py"]
