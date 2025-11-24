FROM mysql:8.0.44-debian

ENV MYSQL_ROOT_PASSWORD=root
ENV MYSQL_DATABASE=yoda

COPY init.sql /docker-entrypoint-initdb.d/
