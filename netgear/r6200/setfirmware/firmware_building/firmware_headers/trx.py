#!/usr/bin/env python
# Copyright (c) 2015
# - Zachary Cutlip <uid000()gmail.com>
# 
# See LICENSE for more details.
# 

import sys
import binascii
from checksums.crc32 import CRC32
from bowcaster.common.support import pretty_string
from bowcaster.common import Logging
from bowcaster.common.support import LittleEndian
from bowcaster.common.support import BigEndian
from bowcaster.development import SectionCreator
from bowcaster.development import OverflowBuffer
import struct

class TrxHeaderException(Exception):
    pass

class TrxHeader(object):
    TRX_MAGIC='HDR0'
    TRX_MAGIC_OFFSET=0
        
    TRX_HEADER_SIZE=28
    TRX_SIZE_OFFSET=4
    
    TRX_CRC32_OFFSET=8
    
    TRX_FLAGS=0
    TRX_VERSION=1
    TRX_FLAGS_OFFSET=12
    
    TRX_PART_1_OFFSET=16
    TRX_PART_2_OFFSET=20
    TRX_PART_3_OFFSET=24
    
    def __init__(self,input_files,endianness,logger=None):
        
        if not logger:
            logger=Logging(max_level=Logging.DEBUG)
        
        cls=self.__class__
        self.endianness=endianness
        
        if len(input_files) < 1 or len(input_files) > 3:
            raise TrxHeaderException("Must have at least one input file and not more than 3.")
        
        partitions=[]
        total_size=cls.TRX_HEADER_SIZE
        offsets=[0,0,0]
        i=0
        for file in input_files:
            data=open(file,"rb").read()
            offsets[i]=total_size
            total_size+=len(data)
            partitions.append(data)
            i+=1
        
        sc=SectionCreator(self.endianness)
        
        sc.string_section(cls.TRX_MAGIC_OFFSET,cls.TRX_MAGIC,description="TRX magic bytes.")
        
        sc.gadget_section(cls.TRX_SIZE_OFFSET,total_size,description="Total size of trx+data.")
        
        version_flags=self._make_version_flags(cls.TRX_FLAGS,cls.TRX_VERSION)
        sc.string_section(cls.TRX_FLAGS_OFFSET,version_flags,description="TRX flags & version.")
        
        partition_offset=offsets[0]
        sc.gadget_section(cls.TRX_PART_1_OFFSET,partition_offset,description="Offset of partition 1.")
        
        partition_offset=offsets[1]
        sc.gadget_section(cls.TRX_PART_2_OFFSET,partition_offset,description="Offset of partition 2.")
        
        partition_offset=offsets[2]
        sc.gadget_section(cls.TRX_PART_3_OFFSET,partition_offset,description="Offset of partition 3.")
        
        pre_checksum_header=OverflowBuffer(self.endianness,cls.TRX_HEADER_SIZE,sc.section_list)
        
        data=str(pre_checksum_header)
        data=data[cls.TRX_FLAGS_OFFSET:]
        data+="".join(partitions)
        
        crc=CRC32(data).crc
        
        logger.LOG_DEBUG("TRX crc32: 0x%08x" % crc)
                
        sc.gadget_section(cls.TRX_CRC32_OFFSET,crc,description="crc32 of header+data.")
        
        trx_header=OverflowBuffer(self.endianness,cls.TRX_HEADER_SIZE,sc.section_list)
        
        self.trx_header=str(trx_header)
    
    def _make_version_flags(self,flags,version):
        if self.endianness==LittleEndian:
            fmt="<HH"
        elif self.endiannes==BigEndian:
            fmt=">HH"
        else:
            raise TrxHeaderException("Invalid endianness.")
        
        version_flags=struct.pack(fmt,flags,version)
        
        return version_flags
    
    def __str__(self):
        return self.trx_header

class TrxImage(object):
    """Class to build a TRX Firmware image from kernel and filesystem."""
    def __init__(self,input_files,endianness,logger=None):
        if not logger:
            logger=Logging(max_level=Logging.DEBUG)            
        
        trx_header=TrxHeader(input_files,endianness,logger=logger)
        
        firmware_data=str(trx_header)
        
        for file in input_files:
            firmware_data+=open(file,"rb").read()
        
        self.firmware_data=firmware_data
    
    def __str__(self):
        return self.firmware_data
        
    
if __name__ == "__main__":
    
    filenames=[]
    for arg in sys.argv[1:-1]:
        filenames.append(arg)
    
    trx_header=TrxHeader(filenames,LittleEndian)
    
    open(sys.argv[-1],"wb").write(str(trx_header))
