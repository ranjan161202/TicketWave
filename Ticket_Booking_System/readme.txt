## Points to Note
The complete WebApp runs only on Linux system.
Please download the Mail Hog application (Fake SMTP server) for your system, not be linux version. 
One can run the full WebApp in WSL and run the MailHog server in Windows.

## How to use
Before we could use the web app, we need to setup the environment and servers for it.
1) <b>Setting up the Flask server :</b>   
   - In a new Linux terminal tab, start the Flask server by typing 

             python3 main.py

2) <b> Setting up Redis server : </b>    
    - In a new Linux terminal tab, start the redis server by typing 

          redis-server
    
3) <b> Setting up Celery Worker and Celery Beat : </b>
    - In a new Linux terminal tab, start the Celery Workers and Beat together by typing 
    
          Celery -A celery_task.celery worker -l info -B    

------------------
## Test user
The application can be tested using a test user if you don't wish to register. Below are the credentials for the same

```python
For admin:
username = admin'  # Case sensitive
password = 'admin'  .

For user:
username = 'raghav42513'  # Case sensitive
password = 'user'  

```