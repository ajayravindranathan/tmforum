FROM python:3.9
WORKDIR /app
COPY UIStreamlit.py /app/
COPY requirements.txt /app/
COPY sqldbchain.py /app/
RUN pip install -r requirements.txt
EXPOSE 8501
COPY . /app/
ENV PATH=“${PATH}:/root/.local/lib/python3.9
CMD ["streamlit", "run", "UIStreamlit.py"]
#HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
#ENTRYPOINT ["streamlit", "run", "UIStreamlit.py"]