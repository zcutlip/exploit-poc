TARGET=reverse-tcp

OBJS=$(TARGET).o

%.o:%.c
	$(CC) $(CFLAGS) -c $< -o $@

$(TARGET): $(TARGET).o
	$(CC) $(LDFLAGS) $^ -o $@ 

clean:
	-rm -f *.o
	-rm -f $(TARGET)