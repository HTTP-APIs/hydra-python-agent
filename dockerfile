FROM python:3

MAINTAINER Sandeep Chauhan <sandeepsajan0@gmail.com>


COPY ./requirements.txt /home/requirements.txt
RUN pip install -r /home/requirements.txt

COPY ./hydra_redis /home/app/hydra_redis
ENV PYTHONPATH $PYTHONPATH:/home/app/

ENTRYPOINT ["python", "/home/app/hydra_redis/querying_mechanism.py"]
