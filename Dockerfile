FROM python:3.8

ARG user=user
ARG group=user
ARG uid=1000
ARG gid=1000

RUN groupadd -g ${gid} ${group} \
	&& useradd -m -u ${uid} -g ${group} ${user} \
	&& mkdir /code \
	&& chown -R ${user}:${group} /code

ADD requirements.txt /tmp
RUN pip install --no-cache-dir -U pip \
	&& pip install --no-cache-dir -r /tmp/requirements.txt \
	&& rm /tmp/requirements.txt

WORKDIR /code
USER ${user}
