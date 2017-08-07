CC = gcc
FLAGS =
CFLAGS = -fPIC -g -O2
LDFLAGS = -shared -lm

SRC_ROOT = pyrtools

TARGET = $(SRC_ROOT)/wrapConv.so
SOURCES = $(shell echo $(SRC_ROOT)/src/*.c)
OBJECTS = $(SOURCES:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJECT)
	$(CC) $(FLAGS) $(CFLAGS) $(LDFLAGS) -o $(TARGET) $(SOURCES)

clean:
	rm -f $(TARGET) $(OBJECTS)
