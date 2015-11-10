# Copyright (c) 2015
# - Zachary Cutlip <uid000()gmail.com>
# 
# See LICENSE for more details.
# 

TRUNK?=.
mtd-src=$(TRUNK)/mtdwriter

mtdwriter:$(mtd-src).tar.gz
	tar zxf $(mtd-src).tar.gz

mtd:mtdwriter
	make -C $(mtd-src) $@
	cp $(mtd-src)/mtd $(TRUNK)/



.rootfs.stamp:rootfs.tar.gz
	tar zxf $<
	touch $@

.wpsd.stamp: wpsd .rootfs.stamp
	install -m 0755 $(TRUNK)/wpsd \
	 $(TRUNK)/rootfs/usr/sbin/wpsd
	
	touch $@

install:mtd .wpsd.stamp
	install -m 0755 $(TRUNK)/mtd $(TRUNK)/rootfs/usr/sbin/mtd

clean:
	-rm mtd
	-rm -rf $(mtd-src)
	-rm -rf $(TRUNK)/rootfs
	-rm -rf .*stamp

bare: clean
	-rm -f $(mtd-src).tar.gz
	-rm -f rootfs.tar.gz
