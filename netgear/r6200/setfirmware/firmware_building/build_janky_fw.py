#!/usr/bin/env python
# Copyright (c) 2015
# - Zachary Cutlip <uid000()gmail.com>
# 
# See LICENSE for more details.
# 

from firmware_headers import trx
from firmware_headers.janky_ambit_header import JankyAmbitHeader
from bowcaster.common.support import Logging
import sys

class JankyFirmwareImage(object):
    """
    Class to generate a janky Netgear R6200 firmware image to be jankily parsed 
    by upnpd using the SetFirmware SOAP action. The image will be composed from
    one or more file parts such as a kernel and filesystem. Proprietary 58-byte
    header + TRX header are generated, and all parts glued together.
    """
    
    def __init__(self,input_files,logger=None):
        """
        Params
        ------
        input_files:    List of files to concatenate and prepend headers to
        logger:         Optional. A Bowcaster Logging object. If a logger is not 
                        provided, one will be instantiated.
        """
        if not logger:
            logger=Logging(max_level=Logging.DEBUG)
        self.logger=logger
        
        trx_img=trx.TrxImage(input_files,trx.LittleEndian,logger=logger)
        header=JankyAmbitHeader(str(trx_img),logger=logger)
        
        self.trx_img=trx_img
        self.header=header
    
    def find_offset(self,value):
        return self.header.find_offset(value)
    
    def __str__(self):
        return str(self.header)+str(self.trx_img)


def main(input_files,output_file,find_str=None):
    logger=Logging(max_level=Logging.DEBUG)

    logger.LOG_DEBUG("Building firmware from input files: %s" % str(input_files))
    
    fwimage=JankyFirmwareImage(input_files)

    if find_str:
        find=find_str
        if find_str.startswith("0x"):
            find=int(find_str,0)
            logger.LOG_DEBUG("Finding offset of 0x%08x" % find)
        else:
            logger.LOG_DEBUG("Finding offset of %s" % find)

        offset=fwimage.find_offset(find)
        logger.LOG_INFO("Offset: %s" % offset)
    else:
        logger.LOG_INFO("Writing firmware to %s\n" % output_file)
        out=open(output_file,"wb")
        out.write(str(fwimage))
        out.close()

def usage():
    print "Usage: build_janky_fw.py {output file | find= } [input file 1 [input file 2,...]]"
    print ""
    print "Generate a Netgear R6200 firmware image from individual parts."
    print "Concatenate one or more firmware components (kernel, filesystem, etc.)"
    print "and prepend a proprietary 58 byte header and a TRX header."
    print ""
    print "Arguments:"
    print "  output file   \tFinal firmware image file"
    print "  find=<pattern>\tLocate the offset of <pattern> in the stand-in"
    print "                \t58-byte header."
    print "                \t<pattern> may be a string or integer. If an integer,"
    print "                \tit must be specified in hexadecimal,"
    print "                \tprepended with \"0x\", and big endian encoded."
    print "  input file 1 [2,...]"
    print "                \tInput files to concatenate."
    print ""
    print "Examples:"
    print "  buildfw.py firmware.chk kernel.lzma squashfs.bin"
    print "  buildfw.py find=0x62374162 kernel.lzma squashfs.bin"
    print "  buildfw.py find=b7Ab kernel.lzma squashfs.bin"

if __name__ == "__main__":
    find=None
    filename=None
    if len(sys.argv) < 2:
        usage()
        exit(1)
        
    if sys.argv[1].startswith("find="):
        find=sys.argv[1].split("=",1)[1]
    else:
        filename=sys.argv[1]

    parts=sys.argv[2:]
    main(parts,filename,find_str=find)
