# Splinter Cell dialogue audio modding

This project replaces mono dialogue clips in Splinter Cell 1 PC English `.LS0` banks with custom audio. The banks use Ubisoft's legacy 4-bit ADPCM codec at 36 kHz. The encoder is experimental but has successfully replaced and decoded two Lambert lines in the training bank. [Ubitunedec](https://github.com/ldeon/Ubitunedec) provides the reference decoder used to check encoded clips.

## Known working replacements

- `Speech_0001L` ("Alright Sam..."): `Sounds/ENGLISH/0_0_2.LS0`, offset `0`, 129,240 samples (3.59 s), segment size 66,992 bytes.
- `Speech_0018L` ("We'll let you do your thing here..."): same bank, offset `564212`, 209,624 samples (5.823 s), segment size 108,588 bytes.

## Replace a clip

1. Locate the subtitle/cue, then decode candidate segments from the matching English bank and listen to confirm the exact line. Offsets are byte offsets from the beginning of that bank.
2. Convert the replacement/crop to mono signed 16-bit PCM WAV at 36 kHz, with exactly the target segment's sample count.
3. Keep an untouched bank copy. Run the encoder to a separate output file:

   ```sh
   python3 ubi_adpcm_encoder.py \
     --template path/to/original.LS0 \
     --input replacement.wav \
     --offset 564212 \
     --output /tmp/replacement.LS0
   ```

   Omit `--offset` for the first segment. Use `--preview path/to/model-preview.wav` only as a rough encoder-model preview.
4. Decode the candidate with Ubitunedec's bundled legacy decoder and listen before installing. For a mono 4-bit segment:

   ```sh
   UbitunedecCMD.exe /tmp/replacement.LS0 \
     --input-type ubi_6or4 --mono --offset 564212 --size 108588 \
     --raw --output /tmp/decoded.pcm
   ```

   Wrap the raw 36 kHz mono signed 16-bit PCM in a WAV to listen. The encoder's portable-model self-check is **not** a substitute for this reference-decoder check.
5. Back up the installed bank, then replace only after confirming the decoded candidate. Preserve the bank's total size and verify other known replacements still decode unchanged.

The encoder currently requires an input WAV with the exact sample count from the target bank segment; it does not resample or trim automatically. Never use its output without the legacy-decoder/listening check.

## Repository contents

This repo intentionally contains only the encoder and documentation. Game files, sound banks, source audio, previews, and backups are excluded; obtain and keep those locally.
