#include "keys.h"
#include <iostream>
#include <pybind11/pybind11.h>
#include <speechapi_cxx.h>
#include <string>
#include <vector>

using namespace Microsoft::CognitiveServices::Speech;
using namespace Microsoft::CognitiveServices::Speech::Audio;

namespace py = pybind11;

class MsTTS {
  std::shared_ptr<EmbeddedSpeechConfig> embeddedConfig;
  std::shared_ptr<SpeechSynthesizer> synthesizer;
  std::shared_ptr<AudioConfig> audioConfig;
  std::shared_ptr<SpeechSynthesisResult> result;

public:
  MsTTS(std::string modelPath, std::string speakerName) {
    embeddedConfig = EmbeddedSpeechConfig::FromPaths({modelPath});
    embeddedConfig->SetSpeechSynthesisOutputFormat(
        SpeechSynthesisOutputFormat::Raw24Khz16BitMonoPcm);
    auto pullStream = AudioOutputStream::CreatePullStream();
    audioConfig = AudioConfig::FromStreamOutput(pullStream);
    embeddedConfig->SetSpeechSynthesisVoice(speakerName, MS_TTS_KEY);
    synthesizer = SpeechSynthesizer::FromConfig(embeddedConfig, audioConfig);
  }
  ~MsTTS() {
    synthesizer.reset();
    embeddedConfig.reset();
    audioConfig.reset();
    result.reset();
  }

  int setSpeaker(std::string speakerName) {
    synthesizer.reset();
    embeddedConfig->SetSpeechSynthesisVoice(speakerName, MS_TTS_KEY);
    synthesizer = SpeechSynthesizer::FromConfig(embeddedConfig, audioConfig);
    return 0;
  }

  py::memoryview synthesis(const std::string &text) {
    result = synthesizer->SpeakTextAsync(text).get();
    if (result->Reason == ResultReason::SynthesizingAudioCompleted) {
      auto audio = result->GetAudioData();
      return py::memoryview::from_memory(
          reinterpret_cast<const void *>(audio->data()), audio->size());

    } else if (result->Reason == ResultReason::Canceled) {
      auto cancellation =
          SpeechSynthesisCancellationDetails::FromResult(result);
      throw std::runtime_error(
          "Synthesis canceled. Reason: " +
          std::to_string((int)cancellation->Reason) +
          (cancellation->Reason == CancellationReason::Error
               ? "\nError Code: " +
                     std::to_string((int)cancellation->ErrorCode) +
                     "\nError Details: " + cancellation->ErrorDetails
               : ""));
    }
    return py::none();
  }
};

struct voiceInfo {
  std::string name;
  std::string gender;
  std::string language;
};

std::vector<voiceInfo> getAvailableVoices(std::string modelPath) {
  std::vector<voiceInfo> voicesList;

  auto cfg = EmbeddedSpeechConfig::FromPaths({modelPath});
  auto syn = SpeechSynthesizer::FromConfig(cfg, nullptr);
  auto voices = syn->GetVoicesAsync("").get();

  if (voices->Reason == ResultReason::VoicesListRetrieved) {
    for (const auto &voice : voices->Voices) {
      voicesList.push_back(voiceInfo{
          voice->Name, static_cast<int>(voice->Gender)==1 ? "Female" : "Male", voice->Locale});
    }
  } else {
    throw std::runtime_error("Failed to retrieve voices list.");
  }
  return voicesList;
}
