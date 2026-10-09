# Dataset review — 2026-10-09

| Candidate | Relevance | Access and license | Decision |
|---|---|---|---|
| [IEEE DataPort simulated boiler fault detection](https://ieee-dataport.org/open-access/simulated-boiler-data-fault-detection-and-classification) | Multisensor fault classification; adjacent to thermal/process cascade, not GPU | Landing page fetch FAILED (restricted URL). Content, row schema, labels and license NOT_VERIFIED | DEFERRED; do not invent measurements or import third-party mirrors |
| [IEEE DataPort three-level NPC inverter normal/open-circuit faults](https://ieee-dataport.org/documents/three-level-npc-inverter-dataset-under-normal-and-open-circuit-fault-conditions) | Electrical hardware fault signatures and physical topology | Landing page fetch FAILED. Source/license NOT_VERIFIED | DEFERRED |
| [ORNL SMC 2021 Titan resource utilization and GPU failures](https://doi.ccs.ornl.gov/dataset/293bf697-819e-5e8c-a7cd-ec8a7c2f0d1a) / [TitanGPULife](https://github.com/olcf/TitanGPULife) | Direct GPU DBE/OTB failures and job resource data; best Akash relevance | Primary landing page and repo README read. Globus download offered. Repository requires citation; redistribution license still UNKNOWN. No bytes downloaded | Preferred next adapter after license and download validation |
| Our controlled byte-corruption fixture | Exact fault, source and regression checks known | Generated locally; no third-party dataset | EXECUTED simulation lane; no physical GPU reliability benchmark claim |

ORNL source: Dash, Paul, Oral and Wang (2021), DOI 10.13139/OLCF/1772811. GPU data includes location changes and prominent Double Bit Error and Out of the Bus failures. TitanGPULife accompanies Ostrouchov et al., GPU Lifetimes on Titan Supercomputer: Survival Analysis and Reliability, SC20. These are historical HPC data, not current Akash lease telemetry and not local Mac temperature sensors.

Next ingestion gate: retrieve authoritative bytes, record DOI/version/license/file SHA-256 and exact columns; deterministic normalize failure labels; temporal split before modeling and group by GPU identity to prevent leakage; baseline simple failure detector; count false positives/negatives and detection latency. Train/evaluate on Akash only if a GPU-sized task and budget justify it. Bind the real lease/model/data/output hashes. Historical location coordinates may drive a separate rack view; do not transplant Titan coordinates onto our Macs.

The 3D schematic in this MVP uses virtual CPU/RAM/worker blocks. It is not an IEEE CAD model, die floorplan, sensor localization, finite-element simulation or measured thermal field. CAD import and physical sensor mapping are NOT_IMPLEMENTED.
