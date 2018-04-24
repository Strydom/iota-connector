FROM python

# Creating Application Source Code Directory
RUN mkdir -p /iota-connector/

# Setting Home Directory for containers
WORKDIR /iota-connector/

# Installing python dependencies
COPY requirements.txt /iota-connector/
RUN pip install --no-cache-dir -r requirements.txt

# Copying src code to Container
COPY watch.py /iota-connector/

# Running Python Application
CMD ["python", "watch.py"]