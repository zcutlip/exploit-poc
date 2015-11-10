#!/usr/bin/env python

from firmware_headers.ambit_header import AmbitHeaderFromFile
from bowcaster.common.support import Logging
import os
import sys
import struct

class R6200Mtd1(object):
    MTD_ERASE_SIZE=0x10000
    def __init__(self,ambit_fw_file,mtd_file,mtd_size,logger=None):
        if not logger:
            logger=Logging(max_level=Logging.DEBUG)
        self.logger=logger
        self.mtd_size=mtd_size
        self.mtd_file=mtd_file
        self.__initialize_mtd_file()
        self.__write_trx_image(ambit_fw_file)
        
    def __initialize_mtd_file(self):
        logger=self.logger
        logger.LOG_INFO("Initializing mtd file: %s" % self.mtd_file)
        remaining=self.mtd_size
        mtd=open(self.mtd_file,"wb")
        while remaining:
            write_size=remaining
            if self.MTD_ERASE_SIZE < remaining:
                write_size=self.MTD_ERASE_SIZE
            #logger.LOG_DEBUG("Writing %d" % write_size)
            mtd.write("\xff"*write_size)
            remaining = remaining - write_size
        mtd.close()
        logger.LOG_DEBUG("Done initializing %s" % self.mtd_file)
    
    def __mtd_erase_block(self,mtd_fh):
        #write a block of 0s
        self.logger.LOG_DEBUG("Erasing 0x%0x block of %s" % (self.MTD_ERASE_SIZE,self.mtd_file))
        mtd_fh.write("\x00"*self.MTD_ERASE_SIZE)
        #rewind to the start of the block we just wrote
        mtd_fh.seek(-1*self.MTD_ERASE_SIZE,os.SEEK_CUR)
    
    def __mtd_write_data(self,mtd_fh,data):
        logger=self.logger
        logger.LOG_INFO("Writing data to %s" % self.mtd_file)
        remaining=len(data)
        while remaining:
            write_size=remaining
            self.__mtd_erase_block(mtd_fh)
            if self.MTD_ERASE_SIZE < remaining:
                write_size=self.MTD_ERASE_SIZE
            data_to_write=data[:write_size]
            data=data[write_size:]
            mtd_fh.write(data_to_write)
            remaining=remaining - write_size
        logger.LOG_INFO("Done writing data to %s" % self.mtd_file)
    
    def __write_trx_image(self,ambit_fw_file):
        logger=self.logger
        logger.LOG_DEBUG("Writing TRX image to %s" % self.mtd_file)
        ambit_header=AmbitHeaderFromFile(ambit_fw_file,logger=logger)
        
        #Need room for TRX image + 4-byte trx image size + 4-byte checksum
        if (self.mtd_size - 8) < ambit_header.trx_img_size:
            raise Exception("TRX image is too large for mtd size of: %d" % self.mtd_size)
        
        ambit_fw=open(ambit_fw_file,"rb")
        ambit_fw.seek(ambit_header.trx_img_off)
        trx_data=ambit_fw.read()
        
        mtd_fh=open(self.mtd_file,"r+b")
        self.__mtd_write_data(mtd_fh,trx_data)
        logger.LOG_DEBUG("Done writing TRX image.")
        mtd_fh.seek(-8,os.SEEK_END)
        logger.LOG_DEBUG("Writing footer to %s" % self.mtd_file)
        logger.LOG_DEBUG("Writing trx image size.")
        mtd_fh.write(ambit_header.packed_trx_img_size())
        logger.LOG_DEBUG("Writing trx checksum.")
        mtd_fh.write(ambit_header.packed_trx_checksum())
        
        mtd_fh.close()
        logger.LOG_INFO("Done writing TRX image to %s" % self.mtd_file)

def main():
    ambit_fw_file=sys.argv[1]
    mtd_file=sys.argv[2]
    mtd_size=int(sys.argv[3])
    logger=Logging(max_level=Logging.DEBUG)
    mtd=R6200Mtd1(ambit_fw_file,mtd_file,mtd_size,logger=logger)

if __name__ == "__main__":
    main()