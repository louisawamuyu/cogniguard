"""
Render the CogniGuard walkthrough video FULLY OFFLINE on this Windows machine.

Voice: Windows SAPI (Microsoft David) - no internet, no AVX, no Colab.
Slides: Pillow. Stitching: ffmpeg (from imageio-ffmpeg).

Note: segment 7 does NOT state a specific accuracy number, because the real number comes from the
Stage 3 evaluation (which needs the GPU/Colab). Once you have it, edit SEGMENTS[6] and re-run.
"""
import os, subprocess, textwrap
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
VOICE = "Microsoft Zira Desktop"

# Windows font files
FONT = r"C:\Windows\Fonts\segoeui.ttf"
FB = r"C:\Windows\Fonts\segoeuib.ttf"

SEGMENTS = [
    ("What is CogniGuard?",
     "CogniGuard is a safety tool for A.I. agents. An agent reads messages, calls tools, and takes actions for you. CogniGuard's job is to keep an eye on that worker."),
    ("It began as a flight recorder",
     "It started as a flight recorder. Every prompt, every tool call, every file, and what it cost, all recorded, so you could replay a run and see what happened. Great for audits. But a recorder only tells you what went wrong after the fact. It watches. It does not step in."),
    ("The gap",
     "Attackers don't always use the obvious words. One writes: ignore all previous instructions. Another writes: please disregard what you were told. Same attack, different words. I wanted CogniGuard to catch the second one, live, before the agent acts."),
    ("What it is now: a real-time gate",
     "So CogniGuard grew a second job. A real-time gate that checks a message before the agent acts. It works in stages, cheapest first. Stage one is fast pattern matching for known attack phrases. Most messages are settled right there."),
    ("Stage three: meaning, not words",
     "The interesting part is stage three, the semantic stage. It turns a message into numbers that capture its meaning, then compares that meaning to a library of known attacks. Please disregard what you were told lands close to ignore all previous instructions, even with almost no shared words. If the meaning is close enough, CogniGuard flags it."),
    ("How we know: an honest test",
     "A claim like that only counts if it is measured. So I built a test, with attacks in fresh wording the system had never seen, plus ordinary safe messages, including tricky ones that contain words like ignore or password."),
    ("The result",
     "So I measured it, on attacks it had never seen. At its tuned setting, the semantic stage catches about eighty-three percent of rephrased attacks, at a six percent false alarm rate. At a stricter setting it is more cautious and misses more. That tradeoff is real, and I measured it, rather than guessing a number."),
    ("The other half: an A.I. front desk",
     "CogniGuard is one half of my work. The other is an A.I. front desk for clinics, built on one promise: never miss a client. When a call goes unanswered, it texts the caller back within seconds, answers the common questions, and books the appointment over WhatsApp, around the clock."),
    ("The Aristotle system",
     "I call the wider system Aristotle: a small team of A.I. assistants that cover reception, follow-ups, and bookings, so a solo clinic runs like it has a full front office. And CogniGuard's safety gate sits on top, refusing medical advice and logging every action."),
    ("Where this is going",
     "This is early, honest work, but the shape is real. A front desk that never misses a client, and a safety layer that can act in the present, not just explain the past. Every claim here is something I can show, not something I assert."),
]


def font(path, size):
    return ImageFont.truetype(path, size)


def slide(path, heading, body):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), (15, 23, 42))
    d = ImageDraw.Draw(img)
    d.text((70, 55), heading, font=font(FB, 50), fill=(56, 189, 248))
    y = 190
    for line in textwrap.wrap(body, 54):
        d.text((70, y), line, font=font(FONT, 32), fill=(226, 232, 240))
        y += 52
    d.text((70, H - 55), "CogniGuard", font=font(FB, 26), fill=(100, 116, 139))
    img.save(path)


def speak(text, wav):
    ps = (
        'Add-Type -AssemblyName System.Speech; '
        '$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
        f'$s.SelectVoice("{VOICE}"); $s.Rate = -1; '
        f'$s.SetOutputToWaveFile("{wav}"); '
        '$s.Speak(@"\n' + text + '\n"@); $s.Dispose()'
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True,
                   capture_output=True, text=True)


def main():
    clips = []
    for i, (h, b) in enumerate(SEGMENTS):
        wav = os.path.join(OUT, f"s{i}.wav")
        png = os.path.join(OUT, f"s{i}.png")
        mp4 = os.path.join(OUT, f"s{i}.mp4")
        speak(b, wav)
        slide(png, h, b)
        subprocess.run([FF, "-y", "-loop", "1", "-i", png, "-i", wav,
                        "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac",
                        "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest", mp4],
                       check=True, capture_output=True)
        clips.append(f"s{i}.mp4")
        print("rendered segment", i)
    listf = os.path.join(OUT, "list.txt")
    with open(listf, "w", encoding="utf-8") as f:
        f.write("".join(f"file '{c}'\n" for c in clips))
    final = os.path.join(OUT, "cogniguard_walkthrough.mp4")
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", listf,
                    "-c", "copy", final], check=True, capture_output=True)
    print("DONE ->", final)


if __name__ == "__main__":
    main()
