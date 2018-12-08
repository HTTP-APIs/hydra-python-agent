FROM python:3

MAINTAINER Sandeep Chauhan <sandeepsajan0@gmail.com>


COPY ./requirements.txt /home/requirements.txt
RUN pip install -r /home/requirements.txt

COPY ./hydra_agent /home/app/hydra_agent
ENV PYTHONPATH $PYTHONPATH:/home/app/

ENTRYPOINT ["python", "/home/app/hydra_agent/querying_mechanism.py"]



