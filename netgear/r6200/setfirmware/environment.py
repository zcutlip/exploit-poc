# Copyright (c) 2015
# - Zachary Cutlip <uid000()gmail.com>
# 
# See LICENSE for more details.
# 

#IP address or hostname of the target
TARGET="10.12.34.1"
#TCP port upnpd is listening on on target.
UPNP_PORT=5000
#port for HTTP to listen on to serve up stage 2
HTTP_PORT=8080
#port for connect-back server to listen on
#Need to start both servers before throwing exploit
#to ensure there's no problem. Hence, they need
#separate ports.
CONNECTBACK_PORT=8081
#directory to server firmware images out of.
SRVROOT="./srvroot"
#first stage, minimized firmware image.
STAGE1="stage1.chk"
#second stage, full blown, trojanized firmware image.
STAGE2="stage2mtd.bin"

