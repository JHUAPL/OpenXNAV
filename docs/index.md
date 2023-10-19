---
hide:
  - navigation
---

# 

![OpenXNAV Logo](assets/images/logo/png/23-03611_OpenXNav_Color-full.png#only-light){ width=50% }
![OpenXNAV Logo](assets/images/logo/png/23-03611_OpenXNav_White-lightblue-full.png#only-dark){ width=50% }

*Open-source modular toolkit for simulating high-fidelity pulsar X-ray events.* 


### **Introduction**

OpenXNAV is designed to aid development and testing of Pulsar-based Autonomous Navigation (XNAV) Positioning, Navigation, and Timing (PNT) solutions.

This is a flexible, cost-effective testbed to enable the next generation of XNAV solutions. OpenXNAV includes three modular components that allow engineers simulate high-fidelity pulsar X-ray events along a flight trajectory over a user-defined mission timeline.
<br />

### **Components**

* [Pulsar Querying](components/1__pulsar_querying/pq_overview.md)
* [Mission Planning](components/2__mission_planning/mp_overview.md)
* [Timing & Event Generation](components/3__custom_event_generation/ceg_overview.md)
* [Hardware In The Loop](components/3__custom_event_generation/ceg_overview.md#hardware-in-the-loop-sdrs)
<br />

Users can query for pulsar candidates using the query tool component (powered by the [ATNF Pulsar Catalogue](https://www.atnf.csiro.au/research/pulsar/psrcat/)). Mission planning for a desired trajectory can be done with our open-source mission planning tool, or via the commercial Ansys System Tool Kit (STK) if desired. X-Ray events can then be generated using our Timing & Event Generation component, and these pulses can (optionally) be simulated in hardware using software-defined radios (SDRs). 
<br />
<br />

**For more information, you can read our [IEEE paper](https://ieeexplore.ieee.org/document/10139942).** <br />
<font color="#8a8a8a">_NOTE_: OpenXNAV was previously named Pulsar-Leveraged Autonomous Navigation Testbed System (PLANTS).</font>


<br /> 
<br /> 

---


### **Support**
If you have questions, suggestions, or require assistance with OpenXNAV, please email: **OpenXNAV@jhuapl.edu**


### **Authors**

This work was created by the following contributors, with funding from Johns Hopkins Applied Physics Lab:

| Contributor | Organization | Department/Sector |
| ----------- | ------------ | ----------------- |
| Sarah Hasnain   |  JHU-APL | Space Exploration Sector (SES)  |
| Michael Berkson |  JHU-APL | Research & Exploratory Development (REDD)  |
| Sharon Maguire  |  JHU-APL | Air & Missile Defense Sector (AMDS)  |
| Evan Sun        |  JHU-APL | Force Projection Sector (FPS)  |
| Katie Zaback    |  JHU-APL | Air & Missile Defense Sector (AMDS)  |

### **Cite This Work**

If you use any component of the OpenXNAV library, please include the following attribution statement: <br /> 
_`
This software derives from OpenXNAV (https://github.com/JHUAPL/OpenXNAV) software developed by The Johns Hopkins University Applied Physics Laboratory.
`_
<br />
<br />
You can also cite our IEEE paper: <br />
``` BibTeX title="Citation (BibTeX)"
@INPROCEEDINGS{10139942, 
author={Hasnain, Sarah and Berkson, Michael and Maguire, Sharon and Sun, Evan and Zaback, Katie},
booktitle={2023 IEEE/ION Position, Location and Navigation Symposium (PLANS)},
title={Pulsar-Leveraged Autonomous Navigation Testbed System (PLANTS): A Low-Cost Software-Hardware Hybrid Testbed for Pulsar-based Autonomous Navigation (XNAV) Positioning, Navigation, and Timing (PNT) Solutions}, 
year={2023}, 
volume={}, 
number={}, 
pages={1286-1292}, 
doi={10.1109/PLANS53410.2023.10139942}}
```

<br /> 
### **<font color="#8a8a8a">License</font>**
<font color="#b3b3b3">
_© 2023 The Johns Hopkins University Applied Physics Laboratory LLC_

_Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)._

_Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License._
</font>
