FROM python:latest
WORKDIR /src_ml
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#ADD requirements.txt requirements.txt
#RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./ machine_learning
ENTRYPOINT ["uvicorn", "machine_learning.MLController:app", "--host", "0.0.0.0", "--port", "8080"]