
<img src="figs/s1.gif" width="750" align="center">

[![DOI](https://zenodo.org/badge/259046250.svg)](https://zenodo.org/badge/latestdoi/259046250) 
[![Coverage Status](https://coveralls.io/repos/github/aalling93/Sentinel_1_python/badge.svg)](https://coveralls.io/github/aalling93/Sentinel_1_python)
![Repo Size](https://img.shields.io/github/repo-size/aalling93/Sentinel_1_python) 
[![Known Vulnerabilities](https://snyk.io/test/github/aalling93/Sentinel_1_python//badge.svg)](https://snyk.io/test/github/aalling93/Sentinel_1_python/)
![Python](https://img.shields.io/badge/python-3.9-blue.svg)



## Introduction <a class="anchor" id="intro"></a>

This is a Python module for working with Sentinel-1 satellite images, purly in Python. It allows you to find the images you want, download them and work with them (calibrate, speckle fitler etc.).. I use the SentinelSAT package for the metadata. The data is then downloaded from NASA ASF. 





## Content <a class="anchor" id="content"></a>
*  [Download Sentinel-1 images with Python](#dwl)

*  [Use Sentinel-1 images in Python](#use)
    *  [Load Sentinel-1 GRD](#grd)

    *  [Decode Sentinel-1 level-0](#decode)
    *  [Calibrate Sentinel-1 GRD](#calibrate)


*  [SAR, briefly](#sar)


## Download Sentinel-1 images with Python <a class="anchor" id="dwl"></a>
The sentinel_download module can be used to find the images you need and subsequently to download them. 
```python
#decide area, time, and level
# filter the data, e.g., only iw, vv, etc etc.
met.iw()
# Check the images before downloading 
met.show_cross_pol()
```
<img src="figs/slc_thumn.png" width="750" align="center">


We can now download the images we want, for instance the third and fourth
```python
with Satellite_download(met.products_df[2:3]) as dwl:

```

And voila. You have now downloaded the images.


## Use Sentinel-1 images in Python <a class="anchor" id="use"></a>
Go back to [Table of Content](#content)


### Load Sentinel-1 level-0 in python<a class="anchor" id="level0"></a>

### Load Sentinel-1 SLC <a class="anchor" id="slc"></a>

### Sentinel-1 GRD <a class="anchor" id="grd"></a>

### Sentinel-1 calibrate <a class="anchor" id="calibrate"></a>

### Decode Sentinel-1 level-0 <a class="anchor" id="decode"></a>



## SAR satellites <a class="anchor" id="sar"></a>
Go back to [Table of Content](#content)

A Synthetic Aperture Radar (SAR) is an active instrument that can be used for e.g. non-cooperative surveillance tasks. Its biggest advantages over e.g. MSI, is that it works day and night, and that it can see though clouds and rain. By placing the SAR instrument on a satellite, it is possible to acquire global coverage with design-specific temporal and spatial resolution. Consequently, by combining, e.g., <font color=yellow> AIS </font>and <font color=yellow> SAR instruments</font>, cooperative and non-cooperative surveillance can be acquired.


A radar is an instrument that is emitting electromagnetic pulses with a specific signature in the microwave spectrum. For a mono-static radar, the radar instrument is both transmitting and receiving the backscatter signal from the pulse. The backscatter signal depends on the structure of the target it illuminated and thus, by comparing the well-known transmitted and received signal, it is possible to describe both the geometrical and underlying characteristics of the target using the mono-static radar equation:

$P_r = \frac{P_t \lambda^2 G(\phi, \theta)^2}{(4 \pi )^3 R^4}\sigma (\phi,\theta),$



where 𝑃𝑟 is the received signal derived from the transmitted signal, 𝑃𝑡. The variable 𝜆 is the design specific wavelength of the radar, and 𝐺(𝜙,𝜃) the radar Gain pattern. The signal is dispersed according to the distance travelled, 𝑅. The radar cross-section, 𝜎(𝜙, 𝜃), can therefore be derived and is describing the target’s dielectric and geometrical characteristics and is dependant on the angles 𝜙 and 𝜃. <font color=yellow> However, in the presence of noise, another contrubution must be added to the mono-static radar equation. In my other Repo, https://github.com/aalling93/Finding-on-groud-Radars-in-SAR-images,  I work with Radio Frequency Interfence (</font> <font color=red> RFI</font>) <font color=yellow>. A phenomenan where other signals from other radars interfer with the SAR signal. </font>
Generally speaking, 𝜎(𝜙,𝜃) is describing the available energy within the target area and must therefore be normalised with the area. The radar backscattering coefficient is found by:

$\sigma^0(\phi, \theta) = \frac{\sigma (\phi, \theta)}{Area}, $

where different areas can be used depending on the problem at hand. When using a SAR as an imaging radar, each pixel in the image has a phase and an amplitude value. By calibrating the image, it is possible to get the radar backscattering coeﬀicient as seen in the equation. <font color=yellow>. In this module, it is possible to download load and calibrate Sentinel-1 images without the need of external software or, e.g., the (infamous) Snappy package.</font> 


Since a SAR is getting a backscatter contribution from all objects within the area illuminated, a noise-like phenomena called speckle arises. This results in a granular image where each pixel is a combination of the backscatter from the individual object in the area. </font> <font color=yellow>  In my repo, https://github.com/aalling93/Custom-made-SAR-speckle-reduction, I have implemented several differente Speckle filters and show the difference under varying conditions. </font>.

A SAR imaging radar differs from a normal radar, by utilising the movement of its platform to synthesise a better resolution, hence the name Synthetic Aperture Radar. When taking pictures of a stationary target, a doppler frequency is found from the velocity of the platform. The SAR is emitting and receiving several pulses to and from the same target. When the SAR is flying towards its target, it will measure a positive doppler frequency which is decreasing until it is perpendicular to the target whereafter it will experience an increasing negative doppler frequency


The electromagnetic signal is transmitted with either a horizontal or a vertical polar- isation, with full parametric SARs being capable of transmitting both horizontal and vertical polarisation. Due to the interaction of the transmitted pulse with the target, both a vertical and horizontal signal is reflected back to the SAR. This causes several different scattering mechanism to occur. Several types of scattering mechanisms ex- ists. For ship detection, the most prominent are Surface scattering and Double bounce scattering. 



#### Surfance scattering

A transmitted signal will be partly absorbed, and partly reflected by the object it illuminates. Surface scattering is the scattering describing the reflected signal. If a surface is completely smooth(specular), no backscatter is reflected back to the SAR. If the surface is rough, a scattering occurs and part of the incident pulse is scattered back to the SAR. Rough surfaces have a higher backscatter as compared to smoother surfaces. Moreover, VV and HH has a higher backscatter compared to VH and HV(HV and VHthey are almost always the same) for both rough and smooth surfaces.  A moist surface results in a higher Radar Cross Section. The backscatter of a surface depends on the roughness and dielectric constant of the target it illuminates. The ocean surface will therefore often result in a small backscatter due to its wet and relatively smooth surface (at low wind speeds), even considering its high dielectric constant at SAR frequencies.


#### Double bounce scattering


Double bounce scattering and occurs when the transmitted pulse is reflected specularly twice from a corner back to the SAR. This results in a very high backscatter. Ships often have many corners and are very smooth, resulting in an especially high backscatter. It is therefore often easy to differentiate e.g. ships with the ocean surface. For more information on the scattering mechanisms on the oceans. As aforementioned, several other scattering mechanisms exist and when detecting e.g. ships in SAR images in the Arctic, volume scattering has to be considers as well.

#### SAR and moving targets


Due to the geometry of the SAR and its moving platform, typical SAR imaging sensors are designed to take focused images with good resolution under the assumption that their target is stationary during image acquisition. This focusing can not be made on moving targets, and normal SAR instruments are therefore ill suited to detect fast moving objects, such as ships. The results is a well resolved static background and poorly resolved moving target. In non-cooperative surveillance tasks, this is a significant problem. Under the assumption that a target is moving perpendicular to the line of sight of the SAR with a constant acceleration, it is possible to reduce the problem by taking the doppler shift of the SAR images into consideration. Maritime vessels do not normally follow such patterns. Hence, more complex trajectory patterns must be accounted for when looking at ships with SAR instruments.

In summary, using the capabilities of a SAR instrument, it should be possible to detect ships on the ocean surface. 