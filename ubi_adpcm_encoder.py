#!/usr/bin/env python3
"""Encode mono Ubisoft 4-bit ADPCM audio into an existing SC1 LS0 bank."""

from __future__ import annotations

import argparse
import math
import struct
import wave
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable


GLOBAL_HEADER = struct.Struct("<12I")
CHANNEL_HEADER = struct.Struct("<4i18h")
GLOBAL_HEADER_SIZE = GLOBAL_HEADER.size
CHANNEL_HEADER_SIZE = CHANNEL_HEADER.size
CHANNEL_SIGNATURE = 2
BITS_PER_SAMPLE = 4

ADPCM4_TABLE1 = (-100000000, 8, 269, 425, 545, 645, 745, 850)
ADPCM4_TABLE2 = (-1536, 2314, 5243, 8192, 14336, 25354, 45445, 143626)
DELTA_TABLE = (
    1024, 1031, 1053, 1076, 1099, 1123, 1148, 1172,
    1198, 1224, 1251, 1278, 1306, 1334, 1363, 1393,
    1423, 1454, 1485, 1518, 1551, 1584, 1619, 1654,
    1690, 1726, 1764, 1802, 1841, 1881, 1922, 1964, 2007,
    -1024, -1031, -1053, -1076, -1099, -1123, -1148, -1172,
    -1198, -1224, -1251, -1278, -1306, -1334, -1363, -1393,
    -1423, -1454, -1485, -1518, -1551, -1584, -1619, -1654,
    -1690, -1726, -1764, -1802, -1841, -1881, -1922, -1964,
    -2007,
)


@dataclass
class ChannelState:
    signature: int
    step1: int
    next1: int
    next2: int
    coef1: int
    coef2: int
    unused1: int
    unused2: int
    mod1: int
    mod2: int
    mod3: int
    mod4: int
    hist1: int
    hist2: int
    unused3: int
    unused4: int
    delta1: int
    delta2: int
    delta3: int
    delta4: int
    delta5: int
    unused5: int

    @classmethod
    def unpack(cls, data: bytes) -> ChannelState:
        return cls(*CHANNEL_HEADER.unpack(data))

    def pack(self) -> bytes:
        return CHANNEL_HEADER.pack(
            self.signature, self.step1, self.next1, self.next2,
            self.coef1, self.coef2, self.unused1, self.unused2,
            self.mod1, self.mod2, self.mod3, self.mod4,
            self.hist1, self.hist2, self.unused3, self.unused4,
            self.delta1, self.delta2, self.delta3, self.delta4,
            self.delta5, self.unused5,
        )


@dataclass(frozen=True)
class BankHeader:
    signature: int
    sample_count: int
    subframe_count: int
    codes_per_subframe_last: int
    codes_per_subframe: int
    subframes_per_frame: int
    sample_rate: int
    unknown1c: int
    unknown20: int
    bits_per_sample: int
    unknown28: int
    channels: int

    @classmethod
    def unpack(cls, data: bytes) -> BankHeader:
        return cls(*GLOBAL_HEADER.unpack(data))


@dataclass(frozen=True)
class Subframe:
    code_count: int
    data: bytes
    padding: bytes


@dataclass(frozen=True)
class Frame:
    state: ChannelState
    subframes: tuple[Subframe, ...]


def _i16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value >= 0x8000 else value


def _i32(value: int) -> int:
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value >= 0x80000000 else value


def _clamp16(value: int) -> int:
    return max(-32768, min(32767, value))


def _absmax16(value: int, maximum: int) -> int:
    if value < 0:
        return max(value, -maximum)
    return min(value, maximum)


def _sign(value: int) -> int:
    return -1 if value < 0 else 1


def expand_code_4bit(code: int, state: ChannelState) -> int:
    """Decode one 4-bit code and update the adaptive channel state."""
    code_signed = code - 7
    step_index = abs(code_signed)
    if step_index > 7:
        raise ValueError(f"4-bit code {code} is outside the supported range 0..14")

    step_next = _i32(ADPCM4_TABLE1[step_index] + state.step1)
    step = _i32((state.step1 & 0xFFFF) * 246 + ADPCM4_TABLE2[step_index]) >> 8
    step = max(271, min(2560, step))

    if ((step_next & 0xFFFFFF00) - 1) & 0x80000000:
        delta = 0
    else:
        delta_index = ((step_next >> 3) & 0x1F) + (33 if code_signed < 0 else 0)
        delta_shift = max(0, min(31, (step_next >> 8) & 0xFF))
        delta = _i32(DELTA_TABLE[delta_index] << delta_shift) >> 10

    next_value = _i16(_i32(
        state.mod1 * state.delta1
        + state.mod2 * state.delta2
        + state.mod3 * state.delta3
        + state.mod4 * state.delta4
    ) >> 10)
    prediction = _i32(state.coef1 * state.hist1 + state.coef2 * state.hist2) >> 10
    sample = _i16(
        _i32(delta + next_value + prediction)
    )

    coef1_next = state.coef1 * 255
    coef2_next = state.coef2 * 254
    delta = _i16(delta)
    if delta + next_value:
        sign1 = _sign(delta + next_value) * _sign(state.delta1 + state.next1)
        sign2 = _sign(delta + next_value) * _sign(state.delta2 + state.next2)
        coef_delta = _i16(((sign1 * 3072 + coef1_next) >> 6) & ~0x3)
        coef_delta = _clamp16(_clamp16(coef_delta + 30719) - 30719)
        coef_delta = _clamp16(_clamp16(coef_delta - 30720) + 30720)
        coef_delta = (
            _i16(sign2 * 1024) - _i16(sign1 * coef_delta)
        ) * 2
        coef1_next += sign1 * 3072
        coef2_next += coef_delta

    state.hist2 = state.hist1
    state.hist1 = sample
    state.coef2 = _absmax16(_i16(coef2_next >> 8), 768)
    state.coef1 = _absmax16(_i16(coef1_next >> 8), 960 - state.coef2)
    state.next2 = state.next1
    state.next1 = next_value
    state.step1 = step

    state.delta5 = state.delta4
    state.delta4 = state.delta3
    state.delta3 = state.delta2
    state.delta2 = state.delta1
    state.delta1 = delta

    state.mod4 = _clamp16(
        state.mod4 * 255 + 2048 * _sign(state.delta1) * _sign(state.delta5)
    ) >> 8
    state.mod3 = _clamp16(
        state.mod3 * 255 + 2048 * _sign(state.delta1) * _sign(state.delta4)
    ) >> 8
    state.mod2 = _clamp16(
        state.mod2 * 255 + 2048 * _sign(state.delta1) * _sign(state.delta3)
    ) >> 8
    state.mod1 = _clamp16(
        state.mod1 * 255 + 2048 * _sign(state.delta1) * _sign(state.delta2)
    ) >> 8

    return sample


def _subframe_counts(header: BankHeader) -> list[int]:
    counts: list[int] = []
    while len(counts) < header.subframe_count:
        remaining = header.subframe_count - len(counts)
        if remaining == 1:
            counts.append(header.codes_per_subframe_last)
        elif remaining == 2:
            counts.extend((header.codes_per_subframe, header.codes_per_subframe_last))
        else:
            counts.extend((header.codes_per_subframe, header.codes_per_subframe))
    return counts


def _unpack_codes(data: bytes, count: int) -> list[int]:
    codes: list[int] = []
    for offset in range(0, len(data), 4):
        chunk = data[offset:offset + 4]
        word = int.from_bytes(chunk, "little") << (4 - len(chunk)) * 8
        codes.extend((word >> shift) & 0xF for shift in range(28, -1, -4))
    return codes[:count]


def _pack_codes(codes: Iterable[int]) -> bytes:
    values = list(codes)
    packed = bytearray()
    full_code_count = len(values) - len(values) % 8
    for offset in range(0, full_code_count, 8):
        word = 0
        for code in values[offset:offset + 8]:
            if not 0 <= code <= 14:
                raise ValueError(f"unsupported 4-bit code: {code}")
            word = (word << 4) | code
        packed.extend(word.to_bytes(4, "little"))
    remaining = values[full_code_count:]
    if remaining:
        word = 0
        for code in remaining:
            if not 0 <= code <= 14:
                raise ValueError(f"unsupported 4-bit code: {code}")
            word = (word << 4) | code
        word <<= (8 - len(remaining)) * 4
        byte_count = (len(remaining) + 1) // 2
        packed.extend(word.to_bytes(4, "little")[-byte_count:])
    return bytes(packed)


def parse_bank_segment(segment: bytes) -> tuple[BankHeader, list[Frame], int, bytes]:
    if len(segment) < GLOBAL_HEADER_SIZE:
        raise ValueError("input is shorter than the Ubisoft audio header")
    header = BankHeader.unpack(segment[:GLOBAL_HEADER_SIZE])
    if header.signature != 8 or header.bits_per_sample != BITS_PER_SAMPLE or header.channels != 1:
        raise ValueError("only mono Ubisoft 4-bit audio segments are supported")
    if header.subframes_per_frame != 2:
        raise ValueError("unsupported subframes-per-frame value")

    cursor = GLOBAL_HEADER_SIZE
    all_counts = _subframe_counts(header)
    frames: list[Frame] = []
    count_index = 0
    while count_index < len(all_counts):
        if cursor + CHANNEL_HEADER_SIZE > len(segment):
            raise ValueError("truncated channel state in audio segment")
        state = ChannelState.unpack(segment[cursor:cursor + CHANNEL_HEADER_SIZE])
        cursor += CHANNEL_HEADER_SIZE
        subframes: list[Subframe] = []
        for code_count in all_counts[count_index:count_index + 2]:
            data_size = (code_count * BITS_PER_SAMPLE + 7) // 8
            end = cursor + data_size
            is_final_partial_subframe = (
                count_index + len(subframes) == len(all_counts) - 1
                and code_count % 8 != 0
            )
            if end + (0 if is_final_partial_subframe else 1) > len(segment):
                raise ValueError("truncated ADPCM subframe in audio segment")
            padding = b"" if is_final_partial_subframe else segment[end:end + 1]
            subframes.append(Subframe(code_count, segment[cursor:end], padding))
            cursor = end + len(padding)
        frames.append(Frame(state, tuple(subframes)))
        count_index += len(subframes)

    aligned_size = (cursor + 3) & ~3
    if aligned_size > len(segment):
        raise ValueError("audio segment is missing its trailing alignment padding")
    return header, frames, aligned_size, segment[cursor:aligned_size]


def decode_segment(segment: bytes) -> tuple[BankHeader, list[int]]:
    header, frames, _, _ = parse_bank_segment(segment)
    pcm: list[int] = []
    for frame in frames:
        state = frame.state
        for subframe in frame.subframes:
            for code in _unpack_codes(subframe.data, subframe.code_count):
                pcm.append(expand_code_4bit(code, state))
    return header, pcm[:header.sample_count]


def _read_wave(path: Path, expected_rate: int, expected_samples: int) -> list[int]:
    with wave.open(str(path), "rb") as wav:
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
            raise ValueError("input WAV must be mono, signed 16-bit PCM")
        if wav.getframerate() != expected_rate:
            raise ValueError(f"input WAV rate is {wav.getframerate()} Hz, expected {expected_rate} Hz")
        if wav.getnframes() != expected_samples:
            raise ValueError(
                f"input WAV has {wav.getnframes()} samples, expected {expected_samples}"
            )
        raw = wav.readframes(wav.getnframes())
    return list(struct.unpack(f"<{expected_samples}h", raw))


def _write_wave(path: Path, samples: Iterable[int], sample_rate: int) -> None:
    values = list(samples)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(struct.pack(f"<{len(values)}h", *values))


def _encode_subframe(samples: list[int], state: ChannelState) -> bytes:
    codes: list[int] = []
    for target in samples:
        best_code = 0
        best_error: int | None = None
        best_state: ChannelState | None = None
        for code in range(15):
            candidate = replace(state)
            reconstructed = expand_code_4bit(code, candidate)
            error = (target - reconstructed) ** 2
            if best_error is None or error < best_error:
                best_code = code
                best_error = error
                best_state = candidate
        assert best_state is not None
        codes.append(best_code)
        state.__dict__.update(best_state.__dict__)
    return _pack_codes(codes)


def encode_segment(template: bytes, input_wav: Path) -> tuple[bytes, list[int]]:
    header, frames, segment_size, padding = parse_bank_segment(template)
    input_samples = _read_wave(input_wav, header.sample_rate, header.sample_count)
    counts = _subframe_counts(header)
    if sum(counts) != header.sample_count:
        raise ValueError("header sample count does not match the number of encoded samples")

    result = bytearray(template[:GLOBAL_HEADER_SIZE])
    decoded: list[int] = []
    sample_offset = 0
    state = frames[0].state
    for frame in frames:
        result.extend(state.pack())
        for subframe in frame.subframes:
            target = input_samples[sample_offset:sample_offset + subframe.code_count]
            sample_offset += subframe.code_count
            encoded_data = _encode_subframe(target, state)
            if len(encoded_data) == len(subframe.data):
                result.extend(encoded_data)
                result.extend(subframe.padding)
            elif len(encoded_data) == len(subframe.data) + len(subframe.padding):
                result.extend(encoded_data)
            else:
                raise ValueError("partial ADPCM subframe does not fit the template layout")
    result.extend(padding)

    if len(result) != segment_size:
        raise ValueError(f"encoded segment size changed ({len(result)} vs {segment_size})")
    decoded_header, decoded = decode_segment(bytes(result))
    if decoded_header.sample_count != len(decoded):
        raise ValueError("encoded segment did not decode to its declared sample count")
    return bytes(result), decoded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, required=True, help="original LS0 bank")
    parser.add_argument("--input", type=Path, required=True, help="mono 16-bit PCM WAV")
    parser.add_argument("--output", type=Path, required=True, help="new LS0 bank; source is not modified")
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="byte offset of the target audio segment in the bank (default: 0)",
    )
    parser.add_argument(
        "--preview",
        type=Path,
        help="write a WAV decoded with this script's portable codec model",
    )
    args = parser.parse_args()

    if args.template.resolve() == args.output.resolve():
        parser.error("output must be a separate file; the template bank will not be overwritten")
    if args.offset < 0:
        parser.error("offset must be zero or greater")
    original = args.template.read_bytes()
    if args.offset + GLOBAL_HEADER_SIZE > len(original):
        parser.error("offset is beyond the end of the template bank")
    target = original[args.offset:]
    _, _, original_segment_size, _ = parse_bank_segment(target)
    encoded_segment, decoded = encode_segment(target[:original_segment_size], args.input)
    if len(encoded_segment) != original_segment_size:
        raise ValueError("encoded segment changed size; refusing to rewrite the bank")
    result = original[:args.offset] + encoded_segment + original[args.offset + original_segment_size:]
    args.output.write_bytes(result)
    if args.preview:
        sample_rate = BankHeader.unpack(encoded_segment[:GLOBAL_HEADER_SIZE]).sample_rate
        _write_wave(args.preview, decoded, sample_rate)

    source_samples = _read_wave(
        args.input,
        BankHeader.unpack(encoded_segment[:GLOBAL_HEADER_SIZE]).sample_rate,
        len(decoded),
    )
    peak_error = max(abs(a - b) for a, b in zip(source_samples, decoded))
    rms_error = math.sqrt(
        sum((a - b) ** 2 for a, b in zip(source_samples, decoded)) / len(decoded)
    )
    print(
        f"Wrote {args.output} (replaced {original_segment_size} bytes "
        f"at bank offset {args.offset})"
    )
    print(
        f"Portable-model self-check: {len(decoded)} samples, "
        f"peak error {peak_error}, RMS error {rms_error:.1f}"
    )
    print("The portable-model self-check does not verify output with the game's legacy decoder.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
