FROM python:3.6

ADD simple_tor_crawler.py /

RUN pip install -r requirements.txt
CMD ["python3", "./simple_tor_crawler.py"]
