FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./trained_models/model.pth /code/trained_models/model.pth
COPY ./Model.py /code/Model.py
COPY ./predict.py /code/predict.py


CMD ["python", "predict.py"]
