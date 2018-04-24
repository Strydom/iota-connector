FROM python

# Creating Application Source Code Directory
RUN mkdir -p /iota_neighbour_watcher/

# Setting Home Directory for containers
WORKDIR /iota_neighbour_watcher/

# Installing python dependencies
COPY requirements.txt /iota_neighbour_watcher/
RUN pip install --no-cache-dir -r requirements.txt

# Copying src code to Container
COPY . /iota_neighbour_watcher/

# Setting Persistent data
VOLUME ["/app-data"]

# Running Python Application
CMD ["python", "watch.py"]