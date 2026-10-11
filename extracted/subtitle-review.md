# Tbilisi audio segment subtitle review

The audio-to-event mappings below are taken from the compiled pattern scripts
and `Sounds\ENGLISH\MAPS.LM0`, not guessed from physical stream order. The
first thirteen rows have an explicit compiled `Localize(cue), Sound(event)`
pair. For the Gurgenidze conversation, the compiled pattern calls `Talk` with
the ten sound events in the order shown; its subtitle cue assignment follows
the localization cue sequence and is therefore marked as sequence-based.

The chain is:

1. `EchelonPattern.u` pairs a subtitle cue with a named sound event (explicitly
   for LambertComms; in event order for Gurgenidze).
2. `S1_1_0Voice.uax` stores that event's sound-map key, such as
   `0x00840001`.
3. `MAPS.LM0` maps the key to the bank and stream offset.
4. DecUbiSnd scan boundaries confirm the playable stream spans and sample
   counts at those offsets. The map's recorded byte count can be one byte
   smaller than the scanner's padded stream span; offsets are the join key.

Subtitle text is from
[P_1_1_0Tbilisi.int](../../Splinter%20Cell/system/LOCALIZATION/P_1_1_0Tbilisi.int)
and
[P_1_1_1Tbilisi.int](../../Splinter%20Cell/system/LOCALIZATION/P_1_1_1Tbilisi.int).
The cue currently reads in Spanish for `Speech_0002L`.

## `1_1_0.LS0` — LambertComms cues

These cue/event pairs are explicit in the compiled pattern. `Speech_0002L`,
the replaced line, resolves to `Play_11_04_02`, key `0x00840001`, offset
`173296` in `1_1_0.LS0`.

| Segment | Duration | Subtitle cue and text | Sound event / key → bank offset | Mapping |
|---|---:|---|---|---|
| [00](1_1_0/segment_00_offset_0000000.wav) | 9.298s | `Speech_0001L` — KENNY: “Well, I would say that we ARE worried. Blah blah blah.” | `Play_11_04_01` / `0x00840000` → 0 | Explicit compiled pair |
| [01](1_1_0/segment_01_offset_0173296.wav) | 0.832s | `Speech_0002L` — PESCADORA: “Estoy en camino.” | `Play_11_04_02` / `0x00840001` → 173296 | Explicit compiled pair; audio user-confirmed |
| [02](1_1_0/segment_02_offset_0188868.wav) | 8.689s | `Speech_0003L` — LAMBERT: “And stay off the streets. There's a heavy cop presence in this town and we don't have Washington's backing if this turns into an incident. Details on your OPSAT.” | `Play_11_04_03` / `0x00840002` → 188868 | Explicit compiled pair |
| [03](1_1_0/segment_03_offset_0350832.wav) | 2.963s | `Speech_0009L` — SAM: “Don't tell me Gurgenidze's inside there.” | `Play_11_08_01` / `0x00840003` → 350832 | Explicit compiled pair |
| [04](1_1_0/segment_04_offset_0406104.wav) | 9.144s | `Speech_0010L` — LAMBERT: “Why would I tell you what you already know? You're gonna have to hurry. Grimsdottir's comparing a Darkstar drone sonar to the warehouse blueprints. She'll be guiding you through.” | `Play_11_08_02` / `0x00840004` → 406104 | Explicit compiled pair |
| [05](1_1_0/segment_05_offset_0576584.wav) | 9.309s | `Speech_0015L` — GRIMSDOTTIR: “Sam, Grimsdottir here. I say jump, don't ask how high, just do it; you should get through this fine. There's a room directly across the hall. Go there now.” | `Play_11_16_01` / `0x0084000F` → 576584 | Explicit compiled pair |
| [06](1_1_0/segment_06_offset_0750132.wav) | 6.411s | `Speech_0016L` — GRIMSDOTTIR: “Damn, sorry about that. Get back into the hall and go to the stairwell at the far end. Make it fast. You've only got a few seconds.” | `Play_11_17_01` / `0x00840010` → 750132 | Explicit compiled pair |
| [07](1_1_0/segment_07_offset_0869688.wav) | 7.521s | `Speech_0018L` — GRIMSDOTTIR: “Jesus but that was close. Take a left just ahead and cut through the room. You'll find a stairwell on the opposite corner. Take it to the top floor.” | `Play_11_18_02` / `0x00840012` → 869688 | Explicit compiled pair |
| [08](1_1_0/segment_08_offset_1009928.wav) | 3.119s | `Speech_0019L` — GRIMSDOTTIR: “The contact's in this room. Let's hope to God he's still alive.” | `Play_11_19_01` / `0x00840013` → 1009928 | Explicit compiled pair |
| [09](1_1_0/segment_09_offset_1068124.wav) | 1.343s | `Speech_0089L` — FISHER: “Gurgenidze checked out.” | `Play_11_20_01` / `0x00840014` → 1068124 | Explicit compiled pair |
| [10](1_1_0/segment_10_offset_1093204.wav) | 3.525s | `Speech_0090L` — LAMBERT: “Leave the corpse for the fire. It'll be less to explain to his family.” | `Play_11_20_02` / `0x00840015` → 1093204 | Explicit compiled pair |
| [11](1_1_0/segment_11_offset_1158964.wav) | 2.660s | `Speech_0024L` — GRIMSDOTTIR: “You've got a safe exit by on the west side of the room. Take it.” | `Play_11_20_03` / `0x00840016` → 1158964 | Explicit compiled pair |
| [12](1_1_0/segment_12_offset_1208620.wav) | 1.994s | `Speech_0025L` — GRIMSDOTTIR: “There's too much smoke. Shoot out the skylights.” | `Play_11_20_04` / `0x00840017` → 1208620 | Explicit compiled pair |

## `1_1_0.LS0` — Gurgenidze conversation

The pattern calls `Play_11_09_01` through `Play_11_09_10` in this order. Each
event's bank key and offset are direct; the subtitle pairing below follows
the order of the Gurgenidze `Speech_*` cues. Unlike the rows above, the
individual `Talk` calls do not contain an explicit subtitle-key argument.

| Segment | Duration | Sequence-matched cue and text | Sound event / key → bank offset | Mapping |
|---|---:|---|---|---|
| [13](1_1_0/segment_13_offset_1245860.wav) | 1.026s | `Speech_0001L` — FISHER: “Gurgenidze?” | `Play_11_09_01` / `0x00840005` → 1245860 | Talk order + cue order |
| [14](1_1_0/segment_14_offset_1265084.wav) | 0.707s | `Speech_0002L` — THOMAS: “...yeah...” | `Play_11_09_02` / `0x00840006` → 1265084 | Talk order + cue order |
| [15](1_1_0/segment_15_offset_1278340.wav) | 2.390s | `Speech_0003L` — FISHER: “I'm NSA. We're gonna get you out of here.” | `Play_11_09_03` / `0x00840007` → 1278340 | Talk order + cue order |
| [16](1_1_0/segment_16_offset_1322976.wav) | 6.535s | `Speech_0004L` — THOMAS: “Don't bother, I'm good as dead. You're looking for Blaustein and Madison.” | `Play_11_09_04` / `0x00840008` → 1322976 | Talk order + cue order |
| [17](1_1_0/segment_17_offset_1444812.wav) | 0.480s | `Speech_0005L` — FISHER: “Yeah.” | `Play_11_09_05` / `0x00840009` → 1444812 | Talk order + cue order |
| [18](1_1_0/segment_18_offset_1453824.wav) | 8.125s | `Speech_0006L` — THOMAS: “Madison was deep into Nikoladze's cabinet, she was on to something big. Blaustein must have figured it out.” | `Play_11_09_06` / `0x0084000A` → 1453824 | Talk order + cue order |
| [19](1_1_0/segment_19_offset_1605312.wav) | 1.251s | `Speech_0007L` — FISHER: “How do I find him?” | `Play_11_09_07` / `0x0084000B` → 1605312 | Talk order + cue order |
| [20](1_1_0/segment_20_offset_1628684.wav) | 9.339s | `Speech_0008L` — THOMAS: “Blaustein's black box, the tracking relay for his subdermals. It's stashed in his safe house just East of Morevi Square.” | `Play_11_09_08` / `0x0084000C` → 1628684 | Talk order + cue order |
| [21](1_1_0/segment_21_offset_1802768.wav) | 3.269s | `Speech_0010L` — FISHER: “Lambert, do we have resources to evac this guy?” | `Play_11_09_09` / `0x0084000D` → 1802768 | Talk order + cue order |
| [22](1_1_0/segment_22_offset_1863756.wav) | 13.278s | `Speech_0011L` — THOMAS: “I said don't bother. Whatever Madison found, it's big. She kept saying 'proof would mean war.' I think Nikoladze wanted...” | `Play_11_09_10` / `0x0084000E` → 1863756 | Talk order + cue order |

The per-stream offsets, encoded sizes, and sample counts are in the
[segment manifest](1_1_0/segments.csv).

## Shared Lambert / Defense Ministry bank

The first three clips in shared `1_1.LS0` are explicitly referenced by the
Tbilisi LambertComms pattern. The fourth is `Play_11_95_01`; compiled
Defense Ministry patterns pair that same event with several subtitle cues.
This confirms the bank is shared across those scenes, rather than merely
finding a similar subtitle string in an unrelated map.

See the [shared segment manifest](1_1/segments.csv) for
the event keys, offsets, and script cue references. User-confirmed audio:

- [Shared segment 00](1_1/segment_00_offset_0000000.wav),
  `Speech_0045L` — LAMBERT: “Dammit Sam, this mission is too sensitive to have
  you wandering around on the streets in public. I'm pulling the plug. The
  mission's over.”
- [Shared segment 01](1_1/segment_01_offset_0104840.wav),
  `Speech_0083L` — LAMBERT: “You know you just gunned down a civilian, right?
  One more mistake like that and the mission's finished.”
- [Shared segment 02](1_1/segment_02_offset_0219132.wav),
  `Speech_0084L` — LAMBERT: “Dammit Fisher, we can't keep covering up these
  civilian corpses. Maybe you weren't the agent we were looking for. You and
  this mission are finished.”
