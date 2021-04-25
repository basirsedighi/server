FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
RUN pip3 install -r server/requirements.txt
RUN pip3 install server/cvb-1.2-cp35.cp36.cp37.cp38-none-win_amd64.whl
COPY  ./server /server