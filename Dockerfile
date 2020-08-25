FROM python:3.8

# create and set working directory
RUN mkdir /opt/project
WORKDIR /opt/project



# Install system dependencies
RUN apt-get update
#&& apt-get install -y --no-install-recommends \
#        tzdata \
#        python3-setuptools \
#        python3-pip \
#        python3-dev \
#        python3-venv \
#        git \
#        && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/*


# install environment dependencies
COPY src/ ./
COPY ./requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r ./requirements.txt

CMD ["bash"]
