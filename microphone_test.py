import threading
import audioop
import pyaudio
import time
from pydub import AudioSegment

# Set the parameters for the audio
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1  # Mono audio
SAMPLE_RATE = 44100  # 44.1kHz sample rate
CHUNK = 1024  # Number of frames per buffer

blinker_on = False

stop_event = threading.Event()

def list_microphones():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"Device {i}: {device_info['name']}, Channels: {device_info['maxInputChannels']}, Sample Rate: {device_info['defaultSampleRate']}")
    p.terminate()

def detect_turn_signal_click(threshold=500, chunk=1024, rate=44100, device_index=None, file_path=None):
    """
    Detect if the provided audio data contains a short transient click
    typical of a turn signal click.

    Methodology:
    1. 
    """
    global blinker_on
    # current_blinker_state = False

    if file_path:
        seg = AudioSegment.from_file(file_path, format="mp3")
        raw_rate = seg.frame_rate
        raw_data = seg.raw_data
        raw_channels = seg.channels
        raw_width = seg.sample_width
        total_len = len(raw_data)
        pos = 0

        def read_frames(n):
            nonlocal pos
            start = pos
            end = min(pos + n * raw_channels * raw_width, total_len)
            chunk_bytes = raw_data[start:end]
            pos = end
            return chunk_bytes

        rms_width = raw_width

        def read_chunk():
            data = read_frames(chunk)
            return data if data else None
    else:


        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            frames_per_buffer=chunk,
            input_device_index=device_index)
        rms_width = 2

        def read_chunk():
            return stream.read(chunk, exception_on_overflow=False)
    
    in_spike = False
    spike_chunks = 0
    MAX_SPIKE_CHUNKS = 2

    last_click_time = 0
    click_group = [] # three triggers must be within 3 seconds
    
    rms_count = 0
    rms_average = 0

    while not stop_event.is_set():
        # data = stream.read(chunk, exception_on_overflow=False)
        data = read_chunk()
        if not data:
            print("End of file reached.")
            break
        # Compute RMS; audioop.rms returns RMS of signed 16-bit samples :contentReference[oaicite:4]{index=4}
        rms = audioop.rms(data, rms_width)
        rms_count += 1
        rms_average = (rms_average * (rms_count - 1) + rms) / rms_count

        print(f"RMS: {rms} Avg: {rms_average} - potential signal click detected!")

        # Update flag if RMS exceeds threshold
        # blinker_on = rms > threshold
        blinker_on = rms > rms_average * 1.2

        now = time.time()
        

        if blinker_on:
            print("🔔 Turn signal click detected!")
            if now - last_click_time < 0.5 or now - last_click_time > 1:
                click_group.clear()
                # print(f"❌ Resetting click group due to invalid timing - Time since last click: {now - last_click_time:.2f} seconds")
                last_click_time = now
                continue

            click_group.append(now)
            if len(click_group) > 3:
                click_group.pop(0)

            # print(f"Current click time elapsed: {click_group[-1] - click_group[0]:.2f} seconds")
            if len(click_group) == 3 and (click_group[-1] - click_group[0]) >= 3:
                # print(f"❌ Deleting invalid click group because it took: {click_group[-1] - click_group[0]} seconds")
                # print(f"Click group prior to deletion: {click_group}")
                click_group.clear()
                last_click_time = now
                continue

            # print(f"RMS: {rms} (Threshold: {threshold}) - Turn signal click detected!")
            # print("Click group start times:", click_group)
            # print("Time since last click:", now - last_click_time)
            # click_group.clear()
            last_click_time = now

            if len(click_group) == 3:
                print("✅ Turn signal click confirmed!")
                print("Click group start times:", click_group)
                print(f"Time elapsed since first click: {click_group[-1] - click_group[0]:.2f} seconds")
                print(f"RMS: {rms} (Threshold: {threshold}) - Turn signal click confirmed!")
                # Reset the click group after confirming a click
                click_group.clear()
                # last_click_time = now

            # current_blinker_state = blinker_on
        #     if not in_spike:
        #         in_spike = True
        #         spike_chunks = 1
        #     else:
        #         spike_chunks += 1
        # else:
        #     if in_spike:
        #         if spike_chunks <= MAX_SPIKE_CHUNKS:
        #             current_time = time.strftime("%H:%M:%S", time.localtime())
        #             print(f"{current_time} Turn signal click detected!")
        #         in_spike = False
        #         spike_chunks = 0
        # small delay to avoid excessive CPU usage
        time.sleep(0.1)

if __name__ == "__main__":
    print("Available Microphones:")
    list_microphones()
    device_index = int(input("Enter the microphone device index to use: "))
    print("Starting turn signal detection...")
    detection_thread = threading.Thread(target=detect_turn_signal_click, args=(500, CHUNK, SAMPLE_RATE, device_index), daemon=True)

    # test_audio_path = "C:\\Users\\maxli\\Driving\\soundTest\\turn-signal.mp3" # TODO: fix this as it crashes on windows atm
    # detection_thread = threading.Thread(target=detect_turn_signal_click, args=(500, CHUNK, SAMPLE_RATE, device_index, test_audio_path), daemon=True)
    detection_thread.start()

    # input command to stop the detection
    try:
        command = input("Press Q to stop detection: ")
        while command.lower() != 'q':
            command = input("Press Q to stop detection: ")
            if command.lower() == 'q':
                break
        
        stop_event.set()
        detection_thread.join()

    except KeyboardInterrupt:
        print("Stopping detection due to keyboard interrupt.")
        detection_thread.join()
    finally:
        print("Detection stopped.")
        detection_thread.join()
        print("Exiting program.")