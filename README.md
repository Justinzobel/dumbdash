Requirements

python3
python3-flask
python3-gunicorn

Needs npm

npm install
then
./node_modules/.bin/tailwindcss -i ./static/css/input.css -o ./static/css/output.css

Run:
python app.py

Open localhost:5000

Add/update a servers info:
ram and rootdisksize are in GB
curl --header "Content-Type: application/json" \
        --request POST \
        --data '{"hostname":"myserver","cpus":"8","ram":"16","rootdisksize":"100"}' \
        http://hubip:5000/api/update
