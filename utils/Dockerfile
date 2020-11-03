# base image
FROM python:3
LABEL maintainer alexandrenesovic@gmail.com
WORKDIR /app
# copy 'app' subfolder content to current directory, i. e. '/app'
COPY ./app .
# run command at build time
RUN pip install -r requirements.txt
ENV FLASK_ENV development
# Container ports
EXPOSE 5000
# Start-up command
CMD ["python","app.py"]

