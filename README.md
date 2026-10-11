# Splinter Cell dialogue audio modding

This project replaces mono dialogue clips in Splinter Cell 1 PC English `.LS0` banks with custom audio. The banks use Ubisoft's legacy 4-bit ADPCM codec at 36 kHz. Use [DecUbiSnd](https://github.com/laymonage/DecUbiSnd)'s experimental audio-replacement feature to encode and replace segments, then use its decoder to verify the result.

## Known working replacements

- `Speech_0001L` ("Alright Sam..."): `Sounds/ENGLISH/0_0_2.LS0`, offset `0`, 129,240 samples (3.59 s), segment size 66,992 bytes.
- `Speech_0018L` ("We'll let you do your thing here..."): same bank, offset `564212`, 209,624 samples (5.823 s), segment size 108,588 bytes.

## Replace a clip

1. Locate the subtitle/cue, then decode candidate segments from the matching English bank and listen to confirm the exact line. Offsets are byte offsets from the beginning of that bank.
2. Convert the replacement/crop to mono signed 16-bit PCM WAV at 36 kHz, with exactly the target segment's sample count. For example, to convert an MP3:

     ```powershell
     ffmpeg -i replacement.mp3 -vn -ac 1 -ar 36000 -c:a pcm_s16le replacement.wav
     ```

   This converts the format and sample rate but does not change the duration. If needed, adjust the audio's speed or crop/pad it to the target duration, then verify that the WAV has exactly the target sample count before encoding.

   To crop a 3.59-second segment starting 1.5 seconds into the source:

     ```powershell
     ffmpeg -i replacement.mp3 -ss 00:00:01.500 -t 3.590 -vn -ac 1 -ar 36000 -c:a pcm_s16le replacement.wav
     ```

   To change speed while preserving pitch, use `atempo` above `1` to speed up or below `1` to slow down. For example, make the audio 1.25x faster:

     ```powershell
     ffmpeg -i replacement.mp3 -vn -af "atempo=1.25" -ac 1 -ar 36000 -c:a pcm_s16le faster.wav
     ```

   Or make it 0.8x speed (slower):

     ```powershell
     ffmpeg -i replacement.mp3 -vn -af "atempo=0.8" -ac 1 -ar 36000 -c:a pcm_s16le slower.wav
     ```

   These examples illustrate cropping and tempo changes; adjust their values for the target segment and verify the resulting WAV has exactly the required sample count. DecUbiSnd does not resample or trim the WAV for you.
3. Keep an untouched bank copy. Use DecUbiSnd's replacement command to write a separate output bank:

     ```powershell
   .\DecUbiSnd.exe .\original.LS0 --replace --replacement-wav .\replacement.wav --offset 564212 --output .\replacement.LS0
   ```

   Use the segment's byte offset; use `--offset 0` for the first segment. Alternatively, open or scan the bank in the GUI, select a mono 4-bit segment, choose **Replace Segment...**, select the replacement WAV, and save to an output bank. You can overwrite the source bank, but only after making a backup.
4. Scan the output bank with DecUbiSnd, decode the replacement segment, and listen to confirm it sounds correct. For a mono 4-bit segment:

     ```powershell
     .\DecUbiSnd.exe .\replacement.LS0 --input-type ubi_6or4 --mono --offset 564212 --size 108588 --raw --output .\decoded.pcm
   ```

   Wrap the raw 36 kHz mono signed 16-bit PCM in a WAV to listen. A successful replacement only confirms format and size checks; it does not confirm in-game playback.
5. Install the verified output bank. Preserve the original backup and verify other known replacements still decode unchanged.

The replacement feature currently supports only mono 4-bit ADPCM segments in Splinter Cell 1 PC `.LS0` banks. It requires an input WAV with the exact sample count from the target segment and does not resample or trim automatically. Never install an output without decoding and listening to it first.

## Repository contents

The Python encoder remains in the repository but is not needed for the workflow above. Game files, sound banks, source audio, previews, and backups are excluded; obtain and keep those locally.
