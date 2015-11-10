# Copyright (c) 2015
# - Zachary Cutlip <uid000()gmail.com>
# 
# See LICENSE for more details.
# 

STAGE1_DIR=$(PWD)/stage1
STAGE2_DIR=$(PWD)/stage2
STAGE1_ROOTFS=$(STAGE1_DIR)/stage1-rootfs.bin
STAGE2_ROOTFS=$(STAGE2_DIR)/stage2-rootfs.bin
BUILD_FW_DIR=$(PWD)/../firmware_building
STAGE1_IMAGE=stage1.chk
STAGE2_IMAGE=stage2.chk
STAGE2_MTD=stage2mtd.bin
MTD1_SIZE=15728640

all:stage1 stage2
	
stage1:$(STAGE1_IMAGE)
stage2:$(STAGE2_MTD)


$(STAGE1_IMAGE):$(STAGE1_ROOTFS) kernel-lzma.bin
	../firmware_building/build_janky_fw.py $@ kernel-lzma.bin $<

$(STAGE2_IMAGE):$(STAGE2_ROOTFS) kernel-lzma.bin
	$(BUILD_FW_DIR)/buildfw.py $@ kernel-lzma.bin $<

$(STAGE2_MTD): $(STAGE2_IMAGE)
	$(BUILD_FW_DIR)/make_mtd.py $< $@ $(MTD1_SIZE)

$(STAGE1_ROOTFS):
	make -C $(STAGE1_DIR)

$(STAGE2_ROOTFS):
	make -C $(STAGE2_DIR)

bare clean:
	make -C $(STAGE1_DIR) $@
	make -C $(STAGE2_DIR) $@
	-rm $(STAGE1_IMAGE)
	-rm $(STAGE2_IMAGE)
	-rm $(STAGE2_MTD)

