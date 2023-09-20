FROM conda/miniconda3

RUN sed -i -e 's/deb.debian.org/archive.debian.org/g' \
           -e 's|security.debian.org|archive.debian.org/|g' \
           -e '/stretch-updates/d' /etc/apt/sources.list

COPY ./envs/environment.yml /work/environment.yml

RUN conda env create -f /work/environment.yml

COPY . /work

WORKDIR /work/decision

RUN apt update && apt install -y git && git submodule init && git submodule update --recursive

WORKDIR /work/decision/

CMD [ "bash", "-c", "source activate decision && python decision.py" ]
#CMD [ "bash","-c", "source activate decision && gunicorn --timeout 1000 --workers=1 --threads=1 -b 0.0.0.0:8000 app:server"]
