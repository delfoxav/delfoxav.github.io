---
layout: post
title: Create a self hosted cloud S3 storage with MinIO
date: 2025-04-05 09:08 +0200
categories: [Projects, Homemade ML]
tags: [MLops, MinIO, data science, machine learning, self-hosted]
---

{% assign image_path = "/assets/images/projects/homemade_ml/self_hosted_minio/" %}

# Create a self hosted cloud S3 storage with MinIO
{% remote_include https://raw.githubusercontent.com/delfoxav/self_hosted_minIO/refs/heads/main/ressources/docker-compose.yml?token={secrets.TOKEN} %}
## Table of Contents


- [Create a self hosted cloud S3 storage with MinIO](#create-a-self-hosted-cloud-s3-storage-withminio)
  - [Table of Contents](#table-of-contents)
  - [Background](#background)
  - [Used Hardware](#used-hardware)
  - [Installing Ubuntu Server](#installing-ubuntu-server)
  - [Preparing the data SSD](#preparing-the-data-ssd)
  - [Install and Deploy MinIO](#install-and-deploy-minio)
    - [TODO show a nice animation of creating a bucket and uploading data from the web UI](#todo-show-a-nice-animation-of-creating-a-bucket-and-uploading-data-from-the-web-ui)
  - [Check and Test our MinIO server](#check-and-test-our-minio-server)
  - [Conclusion](#conclusion)

## Background

Throughout my studies in data sciences I almost never had to really ask myself, how I would store my data. Either I had access to my university clouds and clusters either my models and dataset weren't big enough for requiring any special solution.

However, as my university year are far behind and my personal project kept growing, the need for a more scalable and centralized data storage arose for me.

Obviously, I could rent a some cloud storage and use it in an optimal manner, keep my data on the cloud only for the duration of my projects and spend a few cents for that. But let's face it:
- I want to have full control over my models and data.  
- I tend to forget about my projects for months or even years, so I don't want to pay for storage during downtime.  
- I enjoy those rainy Sundays spent setting up IT projects that I don't necessarily need but find fascinating.  

<div style="text-align: center;">
    <iframe width="560" height="315" 
    src="https://www.youtube.com/embed/77lMCiiMilo" 
    frameborder="0" 
    allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" 
    allowfullscreen></iframe>
    <p><em>Figure 1: Overview of Amazon S3 and its features</em></p>
</div>

Most of the MLops solutions I saw in the last years offered the possibility to store and load data from a S3 bucket. But you might think "What's the point? We wanted to have our data stored locally, no?" And you'll be right, that's where MinIO come in place! MinIO is an object storage solution compatible with Amazon S3 cloud storage service, it's released under GNU License and you can have a self hosted version of it. They even have a docker ready image! So we have it, a self hosted data storage, a reason to get our hands dirty and S3 kind of service.

## Used Hardware

Deploying a MinIO server has some hardware requirements, we could check everything and do the stuff fully properly or simply read what we want and assume it will be fine with our hardware (I am the option B type of guy). Anyway, the most interesting me where the networking,  memory and storage requirements. Quickly put together, with 16 GiB of ram we should be able to manage 1 Ti of storage and the higher the number of disk the lower the number of concurrent requests we can perform. Last but not least, minIO can be limited by the network speed so we should aim for the fastest Bandwidth.

Luckily, one of my old laptop has a Ethernet port and is running on 8 GiB of ram. So let's use this one.

## Installing Ubuntu Server

First of all, we will install a linux distro on the laptop. I don't wanna waste any time here, so we will simply go for a simple Ubuntu installation. I will install Ubuntu server. At the time of the writing of this story, the last version of Ubuntu server is 24.04.2 LTS. So let's download the iso and create an installation drive using Balena Etcher.

Once the iso downloaded and Etcher installed, simply connect a non important USB flash drive(creating an installation drive will overwrite all the data on your USB), and flash it with the downloaded iso.

<div style="text-align: center;">
    <div style="text-align: center;">
        <img src="{{ image_path }}etcher.png" alt="Etcher ready to flash USB drive">
        <p><em>Figure 2: Etcher is ready to flash my USB drive</em></p>
    </div>
</div>

if you want a step by step well done and up-to-date tutorial on how to install Ubuntu, I invite you to check the official tutorial.

While installing, make sure to enable the Ethernet interface and to have an ip address (write down the ip address) and hold the installation for now.

<div style="text-align: center;">
    <div style="text-align: center;">
        <img src="{{ image_path }}ubuntu_ethernet_config.png" alt="Configure your ethernet interface and write down your IP">
        <p><em>Figure 3: Configure your ethernet interface and write down your IP (source: <a href="https://ubuntu.com/tutorials/install-ubuntu-server" target="_blank">Install Ubuntu Server | Ubuntu</a>)</em></p>
    </div>
</div>

We will create some SSH keys on our working machines, push the public key to github and use them to connect to the laptop.

Now, open a terminal and run:

```bash
ssh-keygen
```

The terminal will ask you where you want to store the generated key, put the full path which should be something like "C:\Users\<your_username>/.ssh/<key_name> per default on Windows. In fact you could save your key wherever you want by changing where openSSH checks for keys, but let's save them in the usual .ssh folder so we don't have to deal with that.

Once the key generated, we want to push the public key on our github account. Go to the folder where your key is created, open the .pub key with your notepad and copy the content of the file.

Then, go to your github account to >settings>keys click on New ssh key select a title for the key, past the content of your .pub key and confirm by clicking on Add ssh key. 

You should then be bring back to your key list and see the new added key.

<div style="text-align: center;">
    <div style="text-align: center;">
        <img src="{{ image_path }}ssh_key_github.png" alt="Generated SSH key">
        <p><em>Figure 4: A newly added key on my github account</em></p>
    </div>
</div>

Keep going with the ubuntu installation and you should reach a point where you can enable the OpenSSH service and grab your keys from github. Enter your github username, and it should find the new created key (you can check the sha). Once the key on the laptop, we can keep going with the installation of ubuntu. I'll let you install it as you want, simply install docker (while you can) and it should be good.

<div style="text-align: center;">
    <img src="{{ image_path }}openSSH_ubuntu_config.png" alt="Enable OpenSSH service during Ubuntu installation">
    <p><em>Figure 5: enable OpenSSH and import your pub key from github (source: <a href="https://docs.isarsoft.com/administration/install-ubuntu/#ssh-setup" target="_blank">Install Ubuntu Server - Isarsoft Perception Documentation</a>)</em></p>
</div>

Once done with the installation, you will see a prompt asking you if you want to reboot the system. Do it and remove the usb stick. The laptop should restart and be accessible over ssh.

Now we will connect to the laptop. On your working machine, open a new terminal and type:

```bash
ssh <your_username>@<the_laptop_ip> -i ~/.ssh/<key_name>
```

You could also use any SSH client you prefer, such as [PuTTY](https://www.putty.org/), [MobaXterm](https://mobaxterm.mobatek.net/), or the [VS Code Remote - SSH extension](https://code.visualstudio.com/docs/remote/ssh-tutorial). However, since I don't plan to connect to this server frequently, I'll keep things simple and use a terminal.

First, I want to be able to close the lid of my laptop. So let’s edit the logind.conf.

To allow the laptop to keep running even when the lid is closed, we need to modify the `logind.conf` file. Open the file using the following command:

```bash
sudo nano /etc/systemd/logind.conf
```

Uncomment and edit the following lines to ignore the lid switch actions:

```plaintext
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
```

Save the file and restart the `systemd-logind` service to apply the changes:

```bash
sudo systemctl restart systemd-logind
```

Now, the laptop should continue running even when the lid is closed.

## Preparing the data SSD

MinIO supports 3 deployment types:

- Single-Node Single-Drive (SNSD or “Standalone”)
- Single-Node Multi-Drive (SNMD or “Standalone Multi-Drive”)
- Multi-Node Multi-Drive (MNMD or “Distributed”)

For my use case, I will use the SNSD type and store everything on a single ssd for now. As I am not confident in running more than 1 drive with 8 GiB of ram.

Let’s prepare our ssd drive. According to MinIO documentation we should format it as XFS. To do so, we need to find the drive. Run a *lsblk* command on the laptop before and after connecting the ssd to know where it connects.

<div style="text-align: center;">
    <img src="{{ image_path }}lsblk_example.png" alt="output of lsblk command">
    <p><em>Figure 6: Here my 1.8T ssd is connected as sdb </em></p>
</div>

We format the ssd as xfs and give it a label:

```bash
sudo mkfs.xfs -f /dev/sdb -L MINIODRIVE1
```

Now let's check that we have a XFS drive by mounting it:

```bash
sudo mkdir -p /mnt/ssd #create a mounting point
sudo mount /dev/sdb /mnt/ssd #mount the ssd
df -Th #check the mounted devices
```
In my case, the sdb drive is indeed formatted in xfs:
<div style="text-align: center;">
    <img src="{{ image_path }}drive_list_example.png" alt="List of my drives">
    <p><em>Figure 7: We got a XFS drive </em></p>
</div>

We can umount the drive and edit our fstab to mount it at a consistent path.

```bash
sudo umount /dev/sdb
sudo nano /etc/fstab
```

Be really careful when editing your fstab. But overall you can add each of your drive as shown in minIO documentation:

```bash
$ nano /etc/fstab

# <file system>        <mount point>    <type>  <options>         <dump>  <pass>
LABEL=MINIODRIVE1      /mnt/drive-1     xfs     defaults,noatime  0       2
```

MinIO recommends to disable XFS Retry On Error and provides a script for that. Let's create a file for the script:

```bash
sudo mkdir /opt/minio #creates the opt/minio folder
sudo nano /opt/minio/xfs-retry-settings.sh #creates and write in the xfs-retry-settings.sh file
```

and paste the script provided by MinIO:

```bash
#!/bin/bash

for i in $(df -h | grep /mnt/drive-1 | awk '{ print $1 }'); do
      mountPath="$(df -h | grep $i | awk '{ print $6 }')"
      deviceName="$(basename $i)"
      echo "Modifying xfs max_retries and retry_timeout_seconds for drive $i mounted at $mountPath"
      echo 0 > /sys/fs/xfs/$deviceName/error/metadata/EIO/max_retries
      echo 0 > /sys/fs/xfs/$deviceName/error/metadata/ENOSPC/max_retries
      echo 0 > /sys/fs/xfs/$deviceName/error/metadata/default/max_retries
done
exit 0
```

We can add the script to cron (I like to use nano as my editor). Run the following command to open a cron tab:

```bash
crontab -e 
```

and past the following at the end of the file:

```bash
@reboot /opt/minio/xfs-retry-settings.sh
```

We can make sure that everything went well by rebooting the laptop:

```bash
sudo reboot
```

SSH again to the laptop and (if your fstab isn't broken) you should be able to connect. You can also df -Th again and make sure that the ssd is correctly mounted.



## Install and Deploy MinIO

Now we can install and deploy the docker version of MinIO. As always, most of the information are available on MinIO website.

First we need to create a docker user group and add our user to it:

```bash
sudo groupadd docker
sudo usermod -aG docker <your_user_name>
```

you might need to reboot afterwards.
Now, let's create a folder to store our docker compose and write it:

```bash
mkdir -p ~/docker/minio && cd ~/docker/minio
nano docker-compose.yml
```

Here's the compose file:

```yaml
version: '3.8'

services:
  minio:
    image: minio/minio
    container_name: minio
    ports:
      - "9000:9000" 
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: "your_minio_root_user"
      MINIO_ROOT_PASSWORD: "your_minio_root_password"
    volumes:
      - ~/mnt/drive-1:/data
    command: server /data --console-address ":9001"
    restart: always
```

once the compose file written, we can start the minio service:
    
```bash
docker-compose up -d
```

If everything went well, you should be able to access the minIO UI from your browser just try to connect to <your_server_ip>:9001 and you will see the login page of minIO.


<div style="text-align: center;">
    <img src="{{ image_path }}/minio_login.jpg" alt="The login page of minIO">
    <p><em>Figure 8: The login page of minIO </em></p>
</div>

That should be already good, but let's keep going by creating a new user, a bucket and connect to it using python.

First we login with our root user and password.

Then on the left panel, you can click on Identity > Users > and create a new user. For our use case, we simply need the read/write policies.

We could create a bucket from the web UI and upload data from here as well. However, as a "data scientist" I am more into making everything with python. So I'll let you explore the web UI by yourself if you feel so.

### TODO show a nice animation of creating a bucket and uploading data from the web UI

## Check and Test our MinIO server

MinIO has a python sdk. Install it on your working machine with:
```bash
pip3 install minio
```

Then we can write a quick python script to connect to the minIO server, create a bucket and upload some data.

We will need an access key to the MinIO server. Connect again to the web UI with your newly created user and go to "Access Keys" on the left panel. From there, you can create a new access key. You don't really need to customize the setup if you don't feel so, simply click on "create" to generate the access key.

You will get a pop up showing your access and secret key. Copy those and put them somewhere safe or simply download the provided json file.

We will create a new bucket and upload the iris_data set to it as a csv. We can grab the iris_data from scikit-learn, so let's install it:

```bash
pip install scikit-learn
pip install pandas
```

The following script should then deal with everything else:

```python
# Import the required libraries
from minio import Minio
from minio.error import S3Error
from sklearn.datasets import load_iris
import pandas as pd

# --- Replace with your own MinIO server and credentials ---
MINIO_URL = "your_minio_url:port"
ACCESS_KEY = "your_access_key"
SECRET_KEY = "your_secret_key"

# create a MinIO client with the MinIO server information
client = Minio(MINIO_URL,
               access_key=ACCESS_KEY,
               secret_key=SECRET_KEY,
                   secure=False  # Set to False if not using SSL
)

# Create bucket.
client.make_bucket("toybucket")

# Load the Iris dataset
iris = load_iris()

# Convert it to a pandas DataFrame
df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
df['target'] = iris.target

# Save the DataFrame as a CSV file
df.to_csv('iris_dataset.csv', index=False)

# File to upload
file_path = "iris_dataset.csv"  # Path to the dataset file you created
bucket_name = "toybucket"  
object_name = "iris_dataset.csv"  # The name to give the file in the bucket

# Upload the file to the MinIO bucket
try:
    client.fput_object(bucket_name, object_name, file_path)
    print(f"File '{file_path}' uploaded to bucket '{bucket_name}' as '{object_name}'.")
except S3Error as e:
    print(f"Error: {e}")
```

And that's it!
Go back on the minIO web UI and check for the created bucket. You should see the toybucket with 1 object in it.


<div style="text-align: center;">
    <img src="{{ image_path }}toy_bucket.jpg" alt="A new bucket on my minio server">
    <p><em>Figure 9: my toybucket with the iris_data set inside </em></p>
</div>


## Conclusion

obviously the overall goal wasn't to simply push some iris_data on a 2TB SSD, but it could be a good solution for something like a homemade MLops server ;)

You can find all the code used in this story here:
