# base image
FROM python:3
LABEL maintainer alexandrenesovic@gmail.com
WORKDIR /app
# copy 'app' subfolder content to current directory, i. e. '/app'
COPY ./app .
# run command at build time
RUN pip install -r requirements.txt
ARG aws_db_endpoint
ARG aws_db_user
ARG aws_db_pass
ENV aws_db_endpoint=$aws_db_endpoint
ENV aws_db_pass=$aws_db_pass
ENV aws_db_user=$aws_db_pass
# Container ports
EXPOSE 5000
# Start-up command
CMD ["python","app.py"]

