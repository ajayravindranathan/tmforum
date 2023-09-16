FROM python:3.9
COPY UIStreamlit.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["streamlit run", "UIStreamlit.py"]