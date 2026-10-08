# Six pilot-fit samples

Reference only: generic Cartesian FFF 220 × 220 × 250 mm, PLA 1.75 mm, 0.4 mm nozzle, 0.2 mm layers, requested 3 perimeters, 15% gyroid, top/bottom 5 layers, Arachne, automatic snug supports at 45°, 0.2 mm support Z gap, 0.3 mm XY gap, 5 mm brim, nozzle 205 °C / bed 60 °C. Actual printer and material are not selected.

| Pilot | Reference PLA including support | Estimated normal print time |
|---|---:|---|
| LF shoulder C001 | 6.98 g | 45 m 15 s |
| LF shoulder C002 | 9.22 g | 57 m 37 s |
| LM calf C001 | 31.20 g | 3 h 32 m 43 s |
| LM calf C002 | 34.05 g | 3 h 30 m 02 s |
| LM foot tip C001 | 5.81 g | 42 m 37 s |
| Upper shell C001 | 190.98 g | 18 h 37 m 34 s |

One of each: 278.24 g / 28 h 05 m 48 s. Estimates depend on the reference motion settings. Calf support occupies roughly half the deposited material in the current orientations; the foot-tip sample needs little support. These are starting orientations, not optimized process plans.

`oriented_stl/` keeps original scale with rigid placement only. `slicer/` holds six configured 3MF, complete INI. Each 3MF was CRC/geometry checked and re-imported to confirm the embedded settings. `wall_samples/` contains 18,000 source-coordinate normal-ray measurements, not certified minimum wall thickness. The remaining JSON reports preserve geometry, slicing, toolpath bounds and config checks.

Open a 3MF as a PrusaSlicer project, bind the actual printer, filament, temperatures, retraction, firmware and start/end routines, inspect layers/support contacts, then re-slice. Other slicers can ignore Prusa metadata. Start with foot/shoulder samples and use [the measurement checklist](FIT_CHECKLIST.md).

Raw reference G-code and execution logs are excluded from the public repository. Slicing summaries, toolpath inspection results and G-code digests are retained; scripts can regenerate local paths in `../experiments/reference_gcode/`. Actual machine start/end routines must be configured before printing. No print job has been sent. Source material, flexible pad requirements and load performance remain unknown.
