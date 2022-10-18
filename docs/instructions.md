# Instructions

## Sessions

## Runs

### Experimenters
how to add experimenters



## Recordings

  - **Modality** (*Text*), one of these values:
    - **epi**: Modality for top_up scans. This modality does not have events. This modality has "IntendedFor".
    - **T1w**: Modality for T1w structural scans (also MP2RAGE).

### MRI_Recordings

### EPI_Recordings


  - Pulse Sequence Type (Text): any value but common values are "PRESTO", "MP2RAGE", "Gradient-Echo Head Coil", "Gradient-Echo Surface Coil", "Spin-Echo Surface Coil", "Wouter standard 1.6s", "Gradient-Echo Multiband", "Spin-Echo Multiband", "Standard 2.1s"
  - **Multiband Acceleration Factor** (*Integer*): this is not stored in PAR/REC, so you need to specify the multiband factor.
  - **Phase Encoding Direction** (*Text*): this is not stored in PAR/REC, so you need to look it up in the examcard. In the Philips scanner, it's one letter (f.e. "P", "L"), but here it should specified as two letter ("AP", "RL").

## Navigation
  - Back to [index](index.md)
