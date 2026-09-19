# Automated Computer Vision Quality Control for Industrial Light Guides

Industrial automation and quality inspection system developed as part of the **MSc in Industrial Automation Engineering** curriculum at the University of Aveiro. This project delivers an automated inline inspection workstation designed to eliminate subjective manual inspection in light guide manufacturing through computer vision, chromatic analysis, and PLC integration.

---

##  Industrial Problem & Solution Overview

* **The Challenge:** Traditional quality control relied exclusively on manual human observation, leading to high subjectivity, inconsistent defect classification, and low throughput consistency.
* **The Solution:** A high-precision automated optical inspection (AOI) cell based on an isolated optical dark enclosure ("Caixa Escura"), dedicated 12 MP camera optics, and a colorimetry pipeline running real-time defect verification.

---

##  Architecture & Pipeline Overview

```text
[ Trigger / Start ] ──> [ Raspberry Pi 5 (Vision Processing) ] ──> [ Decision OK/NOK ]
                                │                    │
                  [ HQ Camera + C-Mount Lens ]   [ Socket/Industrial Server ]
                                                     │
                                        [ Omron CP2 PLC & NB HMI ]
