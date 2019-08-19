# MarkAndRecapture
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/staddlez/AWRI-Initial/master)

Simulation for mark and recapture method used in ecology to estimate population size.

**Current Functionality**
-----
* Choose sampling size.
* Add small variations in sampling size to simulate real sampling.
* Choose the number of samplings.
	
**To-do:**
-----
- [ ] Fit the needs of research
- [ ] Find a way to use ndarray to enhance the speed.
- [ ] Improve population def and marking.
- [ ] Add tools to visualize the effect of variation of different parameters.
- [x] Develop GUI or a web-based UI.

**How to use?**
-----
1. Online method:
	1. [Click here](https://mybinder.org/v2/gh/staddlez/AWRI-Initial/master) to launch master branch on Binder. (Note: it may take some time for the branch to load, so be patient.)
	1. Click on MnR.ipynb to launch the notebook.

2. Standalone GUI tool:
	1. Download MnRGUI.py
	1. Go to the the directory where you downloaded the file.
	1. Run MnRGUI.py with python3 (For linux users: run ```python3 MnRGUI.py```)

3. Offline notebook:  
Download the MnR.ipynb file and open it with [Jupyter Notebook](https://jupyter.org/install).
