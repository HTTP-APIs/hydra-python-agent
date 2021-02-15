# How to  run the docs locally

1. <b>(Skip this step if you have already installed hydra-python-agent)</b> <br>
&nbsp;i) Install requirements (It is *recommended* to use a virtual environment)<br>
&nbsp;In the hydra-python-agent folder:<br>
&nbsp;```pip install -r requirements.txt```<br>
&nbsp;ii) Install hydra-python-agent<br>
&nbsp;In the hydra-python-agent folder:<br>
&nbsp;```python setup.py install```<br><br>
2. Build the docs<br>
&nbsp;```cd docs```<br>
&nbsp;```sphinx-build -b html ./source/ ./build/html/```<br>
HTML files are generated in the build/html folder which can be used to check the pages.
<br><br>
<b>In order to make a clean build:</b><br>
&nbsp;```make clean```<br>
&nbsp;```sphinx-build -b html ./source/ ./build/html/```

