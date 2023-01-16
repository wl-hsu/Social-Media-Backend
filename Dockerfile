FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN /usr/local/bin/python -m pip install --upgrade pip 
RUN mkdir /back-end-code
WORKDIR /back-end-code
COPY requirements.txt /back-end-code
RUN pip install -r requirements.txt
COPY . /back-end-code
