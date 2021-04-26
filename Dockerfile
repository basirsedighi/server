FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
#RUN pip3 install cvb-1.2-cp35.cp36.cp37.cp38-none-win_amd64.whl
COPY  ./server /server