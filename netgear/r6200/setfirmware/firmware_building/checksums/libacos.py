#!/usr/bin/env python
# Copyright (c) 2015
# - Zachary Cutlip <uid000()gmail.com>
# 
# See LICENSE for more details.
# 
import sys

"""
reimplementation of calculate_checksum() from
netgear libacos_shared.so
binary MD5: 660c1e24aa32c4e096541e6147c8b56e  libacos_shared.so
"""
class LibAcosChecksum(object):
    
    def __init__(self,data,data_len,checksum_offset=-1):
        self.dword_623A0=0
        self.dword_623A4=0
        fake_checksum="\x00\x00\x00\x00"
        
        self.data=data[0:data_len]
        if(checksum_offset > -1):
            self.data=(self.data[0:checksum_offset]+
                            fake_checksum+
                            self.data[checksum_offset+len(fake_checksum):])
        
        self._update(self.data[0:data_len])
        self._finalize()
        
    
    def _update(self,data):
        size=len(data)
        t0=self.dword_623A0
        a0=self.dword_623A4
        a2=size
        a3=0
        while a3 != a2:
            v1=ord(data[a3])
            a3+=1
            a0=(a0+v1) & 0xffffffff
            t0=(t0+a0) & 0xffffffff
        
        self.dword_623A0=t0
        self.dword_623A4=a0
        
        return 1
    
    def _finalize(self):
        v0=self.dword_623A0
        v1=self.dword_623A4
        
        a0=(v0 & 0xffff)
        v0=(v0>>16 )
        v0=(v0+a0) & 0xffffffff
        
        a2=(v1 & 0xffff)
        v1=(v1>>16)
        v1=(v1+a2) & 0xffffffff
        
        a1=v0>>16
        a1=(a1+v0) & 0xffffffff
        
        a0=v1>>16
        a1=(a1 & 0xffff)
        a0=(a0+v1) & 0xffffffff
        a0=(a0 & 0xffff)
        v0=(a1<<16) & 0xffffffff
        a2=(v0 | a0)
  
        v0=a2
        self.dword_623A4=a0
        self.dword_623A0=a1
        
        self.checksum = v0

if __name__=="__main__":
    firmware=sys.argv[1]
    size=int(sys.argv[2],0)
    data=open(firmware,"rb").read()
    if size > len(data):
        raise Exception("size: %d is longer than data length: %d" % (size,len(data)))
    checksum=LibAcosChecksum(data,size).checksum
    print("Checksum: 0x%08x" % checksum)

