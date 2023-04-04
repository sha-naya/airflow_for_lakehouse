FROM apache/airflow:2.5.2 
ADD requirements.txt . 
RUN pip install -r requirements.txt \
    #Download the desired package(s)
    && curl -O https://download.microsoft.com/download/1/f/f/1fffb537-26ab-4947-a46a-7a45c27f6f77/msodbcsql18_18.2.1.1-1_amd64.apk
