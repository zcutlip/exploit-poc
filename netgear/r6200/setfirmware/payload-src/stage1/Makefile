# Copyright (c) 2015
# - Zachary Cutlip <uid000()gmail.com>
# 
# See LICENSE for more details.
# 

SRC=./src

MKSQUASHFS=netgear-r6200-mksquashfs
stage1-rootfs.bin:
	make -C $(SRC) install
	$(MKSQUASHFS) $(SRC)/rootfs $@ -noappend -all-root

bare clean:
	-rm -f stage1-rootfs.bin
	make -C $(SRC) $@

