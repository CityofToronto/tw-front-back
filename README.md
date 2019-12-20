# tw-front-back

This is the repo for Toronto Water's Structured Asset Management System's Backend

First Time Running the Server:
1. Prerequisite
   - Set up a Ubuntu 18.04 LTS vm
   - Create a duckdns account and get your account token
   - Edit the `docker-compose.yml` file to use the account token
   - Create an entry in Duckdns linking the ip address of the VM with the subdomain (tw-webapp)
2. Install Docker + Docker Compose
   - https://docs.docker.com/v17.09/engine/installation/linux/docker-ce/ubuntu/
   - https://docs.docker.com/compose/install/
   - Optional. Run these commands to install docker + docker compose (docker compose version might be out of date)
```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
3. Clone the repo

`git clone https://github.com/CityofToronto/tw-front-back.git`

4. Go into repo directory

`cd tw-front-back`

5. Start the server via docker-compose

`sudo docker-compose up -d`

6. Replace the default nginx config file 

`sudo cp /home/YOURUSERNAME/tw-front-back/nginx/nginx.conf.template /home/appdata/letsencrypt/nginx/site-confs/default`

7. Restart nginx to reload the new config

`sudo docker-compose restart nginx`

8. Initialize the database and configure hasura by visiting:

https://django.tw-webapp.duckdns.org/djangoAPI/init-all

9. Retrive the latest web client release by visiting:

https://django.tw-webapp.duckdns.org/djangoAPI/update-app

10. Optional: A specific release of the web client can be retrived by specifying the release tag

https://django.tw-webapp.duckdns.org/djangoAPI/get-app?tag=2019.11.07-18.27.313213

Updating The Server
1. `git pull`
2. `sudo docker-compose restart`

Reseting the Server
1. `sudo docker-compose down -v`
2. `sudo docker-compose up -d`

Remove all Docker files
`sudo docker system prune -a`
