# **Timing & Event Generation**


In this Python notebook, the ``event_generation`` module from the PLANTS library is demonstrated.

We start by importing the necessary libraries:

```python
%load_ext autoreload
%autoreload 2
from pint_backend import *
import pulsar_definitions
pint.logging.setup(level="INFO")

```


**Loads the ephemerides kernel**


```python
pint.solar_system_ephemerides.load_kernel("de440")
```

    [1mINFO    [0m (pint.solar_system_ephemerides ): [1mSet solar system ephemeris to de440 through astropy[0m


Creates the time vector that the user hopes to observe at and adds additional error if desired. Specifies what pulsar model to use


```python
time_interval = astrotime.Time( ['2022-07-11T16:00:01.000', '2022-07-11T16:21:01.000'], format='isot', scale='utc')
obs_fs = 100e6
n_toa = 10
error = 5 * u.us
apply_error = False
model_name = "j0218" 

```

Loads in the navigation data provided by STK and generates a spacecraft object off of that navigation data. Note that spacecraft is a custom class created in the PINT backend


```python
time, pos, vel = load_nav_data("XNAVSAT_TEMEofDate_Position_Velocity_JD.txt")
my_spacecraft = SpaceCraft("my_spacecraft", time, pos, vel, overwrite = True)

```

Generates the times of arrival at the barycenter compared to the spacecraft. Note that printing the time of arrival generated is slightly different at the two locations


```python
if(model_name == "j0218"):  
    pulsar_of_interest = PulsarObj(pulsar_definitions.J0218)
elif(model_name == "b1821"):
    pulsar_of_interest = PulsarObj(pulsar_definitions.B1821)
toas_barycenter = pint.simulation.make_fake_toas_uniform(
    time_interval[0].mjd, time_interval[1].mjd, n_toa, model=pulsar_of_interest.model, freq = 1e15*u.Hz, obs='barycenter',  error=error)
toas_spacecraft = pint.simulation.make_fake_toas_uniform(
    time_interval[0].mjd, time_interval[1].mjd, n_toa, model=pulsar_of_interest.model, freq = 1e15*u.Hz, obs = "my_spacecraft",  error=error)



print("Barycenter first TOA: " + str(toas_barycenter.get_mjds("True")[0].utc.iso))
print("Spacecraft first TOA: " + str(toas_spacecraft.get_mjds("True")[0].utc.iso))
```

    [33m[1mWARNING [0m (pint.logging                  ): [33m[1m/opt/anaconda/lib/python3.10/site-packages/pint/models/timing_model.py:373 UserWarning: PINT only supports 'T2CMETHOD IAU2000B'[0m
    [33m[1mWARNING [0m (pint.logging                  ): [33m[1m/opt/anaconda/lib/python3.10/site-packages/pint/models/model_builder.py:139 UserWarning: Unrecognized parfile line 'EPHVER 2'[0m
    [1mINFO    [0m (pint.simulation               ): [1mUsing CLOCK = TT(TAI), so setting include_bipm = False[0m
    [1mINFO    [0m (pint.models.absolute_phase    ): [1mThe TZRSITE is set at the solar system barycenter.[0m
    [1mINFO    [0m (pint.models.absolute_phase    ): [1mTZRFRQ was 0.0 or None. Setting to infinite frequency.[0m
    [1mINFO    [0m (pint.simulation               ): [1mUsing CLOCK = TT(TAI), so setting include_bipm = False[0m


    Barycenter first TOA: 2022-07-11 15:58:51.816031354
    Spacecraft first TOA: 2022-07-11 15:58:51.815489874



```python
%matplotlib inline
resolution_factor = 1
pulsar_of_interest.lightcurve.plot_lightcurve()
time_vec, photon_vec, probability_arr = pulsar_of_interest.lightcurve.create_toa_vec(0, 10, k=4,resolution_factor= resolution_factor)
```


    
![png](output_9_0.png)
    



```python
%matplotlib inline
plt.plot(time_vec[0:10000], photon_vec[0:10000])
plt.xlabel("Time (s)")
plt.ylabel("Number of photons received")
plt.title("Photon vector over 25 ms")
```




    Text(0.5, 1.0, 'Photon vector over 25 ms')




    
![png](output_10_1.png)
    



```python
snip = time_vec
indices = np.argwhere(photon_vec != 0).flatten()
plt.hist(snip[indices], bins = 500)
plt.title("Histogram of photons received with bin resolution = 60 ms")
plt.xlabel("Time (s)")
plt.ylabel("Number of photons received")
```




    Text(0, 0.5, 'Number of photons received')




    
![png](output_11_1.png)
    



```python
%matplotlib inline
barycenter_toas =  create_obs_time_vec(toas_barycenter.first_MJD, time_vec)
pulse_fold_barycenter = LightProfile.pulse_folding(barycenter_toas, photon_vec, pulsar_of_interest.lightcurve, mjd = True, start_offset = toas_barycenter.first_MJD, resolution_factor = resolution_factor)

plt.plot(pulsar_of_interest.lightcurve.phase_list, pulse_fold_barycenter)
plt.xlabel("Phase")
plt.ylabel("Count")
spacecraft_toas = create_obs_time_vec(toas_spacecraft.first_MJD, time_vec)
pulse_fold_spacecraft = LightProfile.pulse_folding(spacecraft_toas, photon_vec, pulsar_of_interest.lightcurve, mjd = True, start_offset = toas_barycenter.first_MJD, resolution_factor = resolution_factor)
plt.plot(pulsar_of_interest.lightcurve.phase_list, pulse_fold_spacecraft)
plt.legend(['Barycenter', 'Spacecraft'])
# plt.plot(pulse_fold_spacecraft.phase_list, pulse_fold_barycenter)
# plt.show()
```




    <matplotlib.legend.Legend at 0x7f9a6dc79120>




    
![png](output_12_1.png)
    


An example of what happens if you fold the pulse with the wrong pulsar of interest


```python
pulse_fold_barycenter = LightProfile.pulse_folding(barycenter_toas, photon_vec, pulsar_of_interest.lightcurve, mjd = True, start_offset = toas_barycenter.first_MJD, resolution_factor = resolution_factor)
plt.plot(pulsar_of_interest.lightcurve.phase_list, pulse_fold_barycenter)
plt.xlabel("Phase")
plt.ylabel("Count")
```




    Text(0, 0.5, 'Count')




    
![png](output_14_1.png)
    



```python
np.save("pulsar_vec.npy", np.asarray(photon_vec))
```
