FROM python:3.4

COPY dist/cops-utils-*.tar.gz /

RUN pip install /cops-utils-*.tar.gz

CMD dockercompose2marathon