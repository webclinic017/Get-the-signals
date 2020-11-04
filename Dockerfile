FROM python:3
LABEL maintainer alexandrenesovic@gmail.com
WORKDIR /app
COPY ./app .
RUN pip install -r requirements.txt
RUN cat script.sh >> ~/.bashrc
RUN source ~/.bashrc
ENV FLASK_ENV development
EXPOSE 5000
CMD ["python","app.py"]

