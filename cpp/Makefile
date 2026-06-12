PYTHON      := python3
PYBIND11    := $(shell $(PYTHON) -m pybind11 --includes)
EXT_SUFFIX  := $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))")

TARGET      := ms_tts$(EXT_SUFFIX)

CXX         := g++
CXXFLAGS    := -O3 -Wall -std=c++17 -fPIC
LDFLAGS     := -shared \
               -L$(SDKDIR)/lib \
               -Wl,-rpath=$(SDKDIR)/lib

INCLUDES    := $(PYBIND11) \
               -I$(SDKDIR)/include/c_api \
               -I$(SDKDIR)/include/cxx_api

LIBS        := -lMicrosoft.CognitiveServices.Speech.core

SRC         := pybind.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) \
		$(INCLUDES) \
		$(LDFLAGS) \
		$(LIBS) \
		-o $@

copy: $(TARGET)
	cp $(TARGET) ../

install: $(TARGET) copy

clean:
	rm -f $(TARGET)

.PHONY: all copy install clean