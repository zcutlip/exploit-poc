#!/usr/bin/env python
# Copyright (c) 2015
# - Zachary Cutlip <uid000()gmail.com>
# 
# See LICENSE for more details.
# 

from bowcaster.common.support import LittleEndian
from bowcaster.common.support import BigEndian
from bowcaster.development import OverflowBuffer
from bowcaster.development import SectionCreator
from bowcaster.common.support import Logging
from checksums.libacos import LibAcosChecksum
import re
import struct

class AmbitHeaderException(Exception):
    pass

class AmbitHeader(object):
    """
    Class to generate a stand-in for the 58 byte unidentified header
    at the beginning of Netgear R6200 firmware images.
    """
    
    #Magic gets checked with strcmp()
    #so must be null terminated,
    #but following field is big endian, with a high byte of 0.
    MAGIC="*#$^"
    MAGIC_OFF=0
    
    #observed size in real-world examples.
    #this may be variable
    #Hard code for now. This can be made configurable later.
    HEADER_SIZE=58
    HEADER_SIZE_OFF=4
    
    #Byte at offset 8 is unused.
    VERSION_STRING_OFF=9
    VERSION_STRING="V100.101.102.103_104.105.106"
        
    #Location of checksum of partition 1
    PART_1_CHECKSUM_OFF=16
    
    #Locations of sizes of partitions 1 & 2
    PART_1_SIZE_OFF=24
    PART_2_SIZE=0   #partition 2 unused
    PART_2_SIZE_OFF=28
    
    #location of checksum of partition 1+2
    PART_1_2_CHECKSUM_OFF=32
    
    #checksum of the header itself,
    HEADER_CHECKSUM_OFF=36
    
    #This is the board ID extracted from NVRAM.
    #Hard code for now. We can make this configurable later.
    BOARD_ID="U12H192T00_NETGEAR"
    BOARD_ID_OFF=40

    def __init__(self,image_data,logger=None):
        """
        Params
        ------
        image_data: The actual data of the firmware image this header should
                    describe and be prepended to.
        logger:     Optional. A Bowcaster Logging object. If a logger is not 
                    provided, one will be instantiated.
        """
        if not logger:
            logger=Logging(max_level=Logging.DEBUG)
        self.logger=logger
        
        logger.LOG_DEBUG("Creating ambit header.")

        self.size=self.HEADER_SIZE
        
        logger.LOG_INFO("Calculating checksum of TRX image.")
        self.trx_image_checksum=self.__checksum(image_data)
        logger.LOG_DEBUG("Calculated TRX image checksum: 0x%08x" % self.trx_image_checksum)
        self.trx_image_sz=len(image_data)
        
        self.version=self.__calc_version_string(self.VERSION_STRING)
        logger.LOG_INFO("Building header without checksum.")
        header=self.__build_header()
        logger.LOG_INFO("Calculating header checksum.")
        chksum=self.__checksum(header)
        logger.LOG_DEBUG("Calculated header checksum: 0x%08x" % chksum)
        logger.LOG_INFO("Building header with checksum.")
        header=self.__build_header(checksum=chksum)
        self.header=header

    
    def __build_header(self,checksum=0):
        
        logger=self.logger
        
        SC=SectionCreator(BigEndian,logger=logger)
        SC.string_section(self.MAGIC_OFF,self.MAGIC,
                            description="Magic bytes for ambit header.")
        SC.gadget_section(self.HEADER_SIZE_OFF,self.size,"Size field representing length of ambit header.")
        #Set header checksum
        SC.gadget_section(self.HEADER_CHECKSUM_OFF,checksum)
        
        #Set board ID
        SC.string_section(self.BOARD_ID_OFF,self.BOARD_ID,
                            description="Board ID string.")
                            
        #Partition 1 size:
        SC.gadget_section(self.PART_1_SIZE_OFF,
                            self.trx_image_sz,
                            description="Size of the TRX image. including TRX header, kernel, and filesystem.")
        SC.gadget_section(self.PART_2_SIZE_OFF,
                            self.PART_2_SIZE,
                            description="Size 0 for unused second partition.")
        
        SC.gadget_section(self.PART_1_CHECKSUM_OFF,
                          self.trx_image_checksum,
                          description="Checksum of the TRX image.")
        SC.gadget_section(self.PART_1_2_CHECKSUM_OFF,
                          self.trx_image_checksum,
                          description="Checksum of the TRX image. Partition 2 is unused.")
        
        SC.string_section(self.VERSION_STRING_OFF,self.version,description="Packed version string.")
        
        buf=OverflowBuffer(BigEndian,self.size,
                            overflow_sections=SC.section_list,
                            logger=logger)
        return buf
    
    def __checksum(self,header):
        data=str(header)
        size=len(data)
        chksum=LibAcosChecksum(data,size)
        return chksum.checksum

    def __calc_version_string(self,version_string):
        version_regex="V(\d+?)\.(\d+?)\.(\d+?)\.(\d+?)_(\d+?)\.(\d+?)\.(\d+)"
        logger=self.logger
        logger.LOG_DEBUG("Calculating version bytes from string: %s" % version_string)
        parts=re.match(version_regex,version_string).groups()
        if len(parts) != 7:
            raise AmbitHeaderException("Invalid version string: %s" % version_string)
        version_bytes=""
        for part in parts:
            version_bytes+=struct.pack("B",int(part))
        
        return version_bytes
        
    def __str__(self):
        return str(self.header)
    
    def find_offset(self,value):
        """
        Find the offset of the given value in the Bowcaster OverflowBuffer string.
        
        Params
        ------
        value:  The value whose offset should be found. May be a string or
                integer. If an integer is provided, it will be converted to
                a packed binary string with the same endianness as the
                underlying OverflowBuffer object.
        """
        return self.header.find_offset(value)


class AmbitHeaderFromFile(AmbitHeader):
    def __init__(self,ambit_fw_file,logger=None):
        if not logger:
            logger=Logging(max_level=Logging.DEBUG)
        self.logger=logger
        self.__parse_ambit(ambit_fw_file)
    
    def __parse_ambit(self,ambit_fw_file):
        """
        only do partial parse because right now I only need the trx checksum.
        """
        logger=self.logger
        infile=open(ambit_fw_file,"rb")
        
        #Validate "*#$^" ambit sig
        infile.seek(self.MAGIC_OFF)
        magic=infile.read(4)
        if magic != self.MAGIC:
            raise Excception("Ambit magic doesn't match.")
        self.magic=magic
        
        #Get location of TRX image
        infile.seek(self.HEADER_SIZE_OFF)
        trx_img_off=infile.read(4)
        trx_img_off=struct.unpack(">L",trx_img_off)[0]
        self.trx_img_off=trx_img_off
        logger.LOG_DEBUG("Got TRX image offset: %d" % trx_img_off)
        
        #Get size of TRX image
        infile.seek(self.PART_1_SIZE_OFF)
        trx_img_size=infile.read(4)
        trx_img_size=struct.unpack(">L",trx_img_size)[0]
        self.trx_img_size=trx_img_size
        logger.LOG_DEBUG("Got TRX image size: %d" % trx_img_size)
        
        #Get checksum for TRX image
        infile.seek(self.PART_1_CHECKSUM_OFF)
        trx_checksum=infile.read(4)
        trx_checksum=struct.unpack(">L",trx_checksum)[0]
        self.trx_checksum=trx_checksum
        logger.LOG_DEBUG("Got TRX checksum 0x%0x" % trx_checksum)
        
        
    def packed_trx_img_size(self):
        return struct.pack("<L",self.trx_img_size)
    
    def packed_trx_checksum(self):
        return struct.pack("<L",self.trx_checksum)
