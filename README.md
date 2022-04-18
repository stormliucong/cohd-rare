## OARD (An acronym form of ["oh alright"](https://www.urbandictionary.com/define.php?term=oard)): an **O**pen real-world based **A**nnotation for **R**are **D**iseases and its associated phenotypes


This is a Flask app to serve the backend API of OARD. Currently it is hosted on the 
[NCATS AWS server (https://rare.cohd.io/)](https://rare.cohd.io/). This repo currenly only have the Flask API part. The fron end React web app is hosted in another [repo](https://github.com/stormliucong/oard-react). We expect to merge two repos in the near future.

# Columbia Open Health Data API (COHD)
The architecture of this web API is largely adopted from an exisitng project called [COHD](https://github.com/WengLab-InformaticsResearch/cohd_api)
## Installation

To install
```sh
pip -r requirement.txt
```

## Running the Application

The API is served using FLASK:

```
FLASK_APP=cohd.py flask run
```

## Deploying and running OARD on AWS

OARD is served on an AWS EC2 instance using Nginx and uWSGI. For consistency, use the approach in the following [blog post](http://vladikk.com/2013/09/12/serving-flask-with-nginx-on-ubuntu/)

Caveats:

- If using virtualenv, you either have to have the virtualenv directory in the same location as the cohd.py application, or specify the location of the virtualenv using the `uWSGI -H` parameter.

# nsides back-end (drug effect database population)
Please see [here](https://github.com/tatonetti-lab/nsides/tree/master/condor)

# nsides middleware (on-demand job submission)
Please see [here](https://github.com/tatonetti-lab/nsides/tree/master/job_api)

# On the EC2 server:
- `/var/cohd-rare/` has the code
- `/var/cohd-rare/cohd/cohd.ini` – uwsgi configuration for running the app
- `/var/cohd-rare/cohd/cohd_flask.conf` – flask configuration
- `/var/cohd-rare/cohd/database.cnf` – mysql database configuration file. Currently using the main cohd database. Should be changed when you have the new database up
- `/var/cohd-rare/cohd/venv` – virtualenv location
- `/var/log/uwsgi/cohd-rare.log` – log file
- `/etc/system/system/cohd-rare.service` – system configuration (already set to automatically start on boot)
- `sudo systemctl <start|stop|restart> cohd-rare`
restart after python code changes to app
- `/etc/nginx/sites-available/cohd-rare` – nginx configuration
- `sudo systemctl restart nginx` - restart nginx
- If you make changes
Test configuration changes without applying: `sudo nginx -t`
Apply configuration changes: `sudo service nginx reload`
