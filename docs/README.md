# How to  run the docs locally

1. <b>(Skip this step if you have already installed hydrus)</b> <br>
&nbsp;i) Clone the hydrus repository: ```git clone https://github.com/HTTP-APIs/hydrus.git```<br>
&nbsp;ii) Install requirements (It is *recommended* to use a virtual environment)<br>
&nbsp;```cd hydrus```<br>
&nbsp;```pip install -r requirements.txt```<br>
&nbsp;iii) Install hydrus<br>
&nbsp;```python setup.py install```<br>
2. Build the docs<br>
&nbsp;```cd docs```<br>
&nbsp;```sphinx-build -b html ./source/ ./build/html/```<br>
HTML files are generated in the build/html folder which can be used to check the pages.
<br><br>
<b>In order to make a clean build:<br>
&nbsp;```make clean```<br>
&nbsp;```sphinx-build -b html ./source/ ./build/html/```

