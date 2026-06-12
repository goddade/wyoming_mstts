#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "mstts.h"

namespace py = pybind11;

PYBIND11_MODULE(ms_tts, m)
{
    m.doc() = "Microsoft embedded TTS Python bindings using pybind11";

    py::class_<voiceInfo>(m, "VoiceInfo")
            .def(py::init<>())
            .def_readwrite("name", &voiceInfo::name)
            .def_readwrite("gender", &voiceInfo::gender)
            .def_readwrite("language", &voiceInfo::language);

    m.def("get_voices", &getAvailableVoices, 
          "Get available voices from model path",
          py::arg("model_path"));

    py::class_<MsTTS, std::shared_ptr<MsTTS>>(m, "MsTTS")
        .def(py::init<std::string, std::string>())
        .def("synthesis", &MsTTS::synthesis)
        .def("set_speaker", &MsTTS::setSpeaker);
}