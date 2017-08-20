# Docker container for attaskcreator
FROM python:latest
LABEL maintainer="fredericmhenry@gmail.com" 
ARG vers

RUN echo ${vers}
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN wget https://github.com/rickh94/attaskcreator/archive/v${vers}.tar.gz
RUN tar -xvf v${vers}.tar.gz
RUN cd attaskcreator-${vers} && python setup.py install && pip install pytest && pytest
#RUN mkdir /config
#RUN mkdir /logs
#RUN useradd -U

#USER attaskcreator
CMD attaskcreator -p /config
