Blink1
=======

A collection of daemons for the ThingM blink(1) connected to a Raspberry Pi, utilizing the `blink1-tool` command-line 
program from https://github.com/todbot/blink1.

## Setup

Install the `blink1-tool` command-line program:

```
sudo apt-get update
sudo apt-get install libusb-1.0-0-dev

git clone https://github.com/todbot/blink1.git

cd blink1/commandline
make
sudo make install
```


Install Daemon Tools:

```
sudo apt-get update
sudo apt-get install daemontools daemontools-run
```

Each subfolder of this repository is a different blink(1) daemon. To setup a daemon, **follow any dependency 
instructions in the README of the daemon's subfolder**, and then:

Make sure the daemon's run script is executable:

```
chmod +x run
```

Symlink the daemon's folder into /etc/service so Daemon Tools knows to start it:

```
cd /etc/service
ln -s /path/to/daemon/folder .
```

After about 5 seconds the daemon should begin to run. You can start/stop it using:

```
# Stop it (the "d" is for "down")
$ svc -d /path/to/daemon/folder

# Start it (the "u" is for "up")
$ svc -u /path/to/daemon/folder
```
