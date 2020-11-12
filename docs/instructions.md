# Instructions


## Recordings

  - **Modality** (*Text*), one of these values:
    - **epi**: Modality for top-up scans. This modality does not have events. This modality has "IntendedFor".

### EPI recordings

  - Pulse Sequence Type (Text): any value but common values are "PRESTO", "MP2RAGE", "Gradient Echo", "Spin Echo"
  - **Multiband Acceleration Factor** (*Integer*): this is not stored in PAR/REC, so you need to specify the multiband factor.
  - **Phase Encoding Direction** (*Text*): this is not stored in PAR/REC, so you need to look it up in the examcard. In the Philips scanner, it's one letter (f.e. "P", "L"), but here it should specified as two letter ("AP", "RL").
