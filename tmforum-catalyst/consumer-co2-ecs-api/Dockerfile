FROM python:3.9
WORKDIR /app
COPY UIStreamlit.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8501
COPY . .
ENV PATH=“${PATH}:/root/.local/bin”
CMD streamlit run app.py
#HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
#ENTRYPOINT ["streamlit", "run", "UIStreamlit.py"]