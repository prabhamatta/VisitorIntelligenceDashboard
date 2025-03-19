Visitor Intelligence Dashboard
==============================	

Given a set of visitor weblogs for a website for a few weeks, this is a web application prototype solution\
for sales reps. The solution empowers the sales rep with the best possible insights about the visitors \
that can be easily searchable by various attributes.

Live application at http://prabhamatta.com:8888/

![alt text](https://github.com/prabhamatta/VisitorIntelligenceDashboard/blob/main/static/images/Visitors%20Intelligence%20Dashboard%20UI.png?raw=true)

### Web Application Components
 * Server side: Flask web server
 * Client side: HTML, Javascript and CSS
 * Product Deployment: DigitalOcean 

### Functional Specifications
* Pre-processing of Data: 
  + Parse User Agent to retrieve Browser, Operating System and Device 
  + Cleanup and compile Paths accessed 
  + Extract Domain name/Business from Referral URL 
  + Get unique browsers, os, device, domains, pages, etc to be populated in the filter options 
* Use dropdowns instead of text input for filters to prevent user-input errors 
* Display Alert messages for errors as well as successful upload of the file, filters processing errors 

## Install required packages (see requirements.txt file):
* Install python3
* pip install flask
* pip install user_agents


## Setup Instructions
Create the following project structure:

├── app.py

├── static/
│   └── style.css
│   └── script.js


├── templates/
    └── index.html


## Run the application
python app.py

## Access the application
Open your web browser  
Go to http://127.0.0.1:8888/
