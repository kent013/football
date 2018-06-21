# README
## TL;DR
This is experimental system to learn about current Natural Language (especially Japanese) libraries.

This repository contains following scripts.
1. Scrape football articles from RSSs with Scrapy (python)
2. Extract contents (main body text and primary image from HTML)
3. Tokenize (using Janome for Japanese, NLTK for English)
4. Calculate similarity (using gensim Doc2Vec)
5. Website (using PHP)

The site deployed is https://the-football-spot.com/

## Instance Configuration

### Change Hostname

```bash
sudo hostname [instance alias in servers.json]
```

### Install Linux Packages
```bash
sudo yum install git php71 php71-pdo php71-mysqlnd mysql gcc bzip2-devel readline-devel openssl-devel sqlite-devel mysql57 mysql57-devel gcc gcc-c++ libxml2-devel
```
#### mysql57 workaround

```bash
# work around http://mhag.hatenablog.com/entry/2017/10/25/145313
sudo vi /etc/ld.so.conf.d/mysql57-x86_64.conf
# change 56 -> 57
sudo ldconfig
```

### Install python
Install pyenv
```bash
curl -sL https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
```

and then edit .bashrc

```bash
vi .bashrc
```

paste below
```bash
HISTTIMEFORMAT='%y/%m/%d %H:%M:%S '
HISTSIZE=100000

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

CRAWLER_SEPARATION_COUNT=6
CRAWLER_NOTIFY=0
```

apply settings
```bash
source .bashrc
```

Now you can use pyenv, install python

```bash
pyenv install 3.5.4
pyenv global 3.5.4
pyenv rehash
```

### Install PIP/packages

```bash
curl -skL https://bootstrap.pypa.io/get-pip.py | python

pip install scrapy sqlalchemy slackweb python-dateutil feedparser mysqlclient extractcontent3 numpy Cython extractcontent Pillow diskcache BeautifulSoup4 nltk
pip install dragnet
```

### Clone repository
Put SSH key which submitted to repos to the server (football_deploy).

```bash
chmod 600 ~/.ssh/football_deploy
```

And edit SSH config file

```bash
vi .ssh/config
```

as below

```bash
Host github.com
  User git
  Port 22
  Hostname github.com
  IdentityFile ~/.ssh/football_deploy
```

then configure permissions
```bash
chmod 600 .ssh/config
```

Then create dir for the repos and clone the repos.

```bash
sudo mkdir /var/repos
sudo chown ec2-user.ec2-user /var/repos
cd /var/repos/
git clone git@github.com:kent013/football.git
cd
ln -s /var/repos/football/ football
```

### Modify DATABASE settings

```bash
cp football/football/settings-dist.py football/football/settings.py
vi football/football/settings.py
```

### Test settings through crawler

```bash
cd ~/football
scrapy crawl all
```

### Create crawler log dir

```bash
sudo mkdir /var/log/crawler/
sudo chown ec2-user.ec2-user /var/log/crawler/
```
