import sounddevice as sd

print("=" * 60)
print("  AUDIO DEVICES ON THIS SYSTEM")
print("=" * 60)

devices = sd.query_devices()
print("\n--- INPUT DEVICES (Microphones) ---")
for i, d in enumerate(devices):
    if d["max_input_channels"] > 0:
        default = " <<< DEFAULT" if i == sd.default.device[0] else ""
        print(f"  [{i}] {d['name']} (channels: {d['max_input_channels']}){default}")

print("\n--- OUTPUT DEVICES (Speakers) ---")
for i, d in enumerate(devices):
    if d["max_output_channels"] > 0:
        default = " <<< DEFAULT" if i == sd.default.device[1] else ""
        print(f"  [{i}] {d['name']} (channels: {d['max_output_channels']}){default}")

print(f"\nDefault Input Device ID: {sd.default.device[0]}")
print(f"Default Output Device ID: {sd.default.device[1]}")

# Quick recording test
print("\n--- QUICK RECORDING TEST (2 seconds) ---")
try:
    import numpy as np
    recording = sd.rec(int(2 * 16000), samplerate=16000, channels=1, dtype="float32")
    print("Recording for 2 seconds... speak now!")
    sd.wait()
    peak = np.max(np.abs(recording))
    rms = np.sqrt(np.mean(recording ** 2))
    print(f"Peak level: {peak:.4f}")
    print(f"RMS level:  {rms:.4f}")
    if peak < 0.001:
        print("WARNING: No audio detected! Your microphone may not be working.")
    elif peak < 0.01:
        print("WARNING: Very low audio level. Check microphone volume.")
    else:
        print("Audio captured successfully!")
except Exception as e:
    print(f"Recording error: {e}")
