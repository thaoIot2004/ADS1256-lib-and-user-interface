# Makefile for ADS1256 library
# Name lib
TARGET = libads1256.so 

# Compiler
CC = gcc

# Flags
CFLAGS = -Wall -Wextra -fPIC -I.
LDFLAGS = -shared -lpigpio -lrt -pthread

# Source files
SRCS = ads1256.c
OBJS = $(SRCS:.c=.o)

# Rules
all: $(TARGET)

# Create Dynamic lib
$(TARGET): $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

# Create object file
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Install library (optional)
install: $(TARGET)
	sudo cp $(TARGET) /usr/local/lib/
	sudo cp ads1256.h /usr/local/include/

# Clean build files
clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean install
