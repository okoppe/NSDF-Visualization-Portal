FROM python:3.7
RUN mkdir /app
EXPOSE 5999-6005
WORKDIR /app/
ADD . /app/
RUN pip install -r requirements.txt
RUN chmod +x run.sh
CMD ["./run.sh"]