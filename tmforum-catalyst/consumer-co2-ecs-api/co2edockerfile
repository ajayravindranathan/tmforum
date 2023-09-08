FROM python:3.9
COPY ConsumerCO2eFunction.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python", "ConsumerCO2eFunction.py"]