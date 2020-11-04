FROM python:3
LABEL maintainer alexandrenesovic@gmail.com
WORKDIR /app
COPY ./app .
ARG aws_db_endpoint
ARG aws_db_pass
ARG aws_db_user

ENV aws_db_endpoint=$aws_db_endpoint
ENV aws_db_pass=$aws_db_pass
ENV aws_db_user=$aws_db_user

RUN pip install -r requirements.txt
ENV FLASK_ENV development
EXPOSE 5000
CMD ["python","app.py"]

