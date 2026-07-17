import subprocess
import numpy as np

from core.runtime import require_binary

SR = 48000


def load_pcm(path, sample_rate=SR, mono=True):

    cmd = [
        require_binary("ffmpeg"),
        "-hide_banner",
        "-loglevel", "error",
        "-i", path,
        "-f", "s16le",
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", "1" if mono else "2",
        "-"
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        check=True
    )

    pcm = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32)

    return pcm
