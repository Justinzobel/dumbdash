Requirements
===
* python3
* python3-flask
* python3-gunicorn
* npm

Install
===
npm install
`./node_modules/.bin/tailwindcss -i ./static/css/input.css -o ./static/css/output.css`

Run
===
`python app.py`

View
===
http://localhost:5000

Usage
====
Add/update a servers info (ram and rootdisksize are in GB):
```
curl --header "Content-Type: application/json" \
        --request POST \
        --data '{"hostname":"myserver","cpus":"8","ram":"16","rootdisksize":"100"}' \
        http://hubip:5000/api/update
```
