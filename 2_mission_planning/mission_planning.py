# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 15:48:44 2023

@author: berksma1
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.table import QTable

from sympy.solvers import nsolve
from sympy import Symbol
from sympy import sin

from astropy.visualization import time_support
time_support()

# Definitions of universal constants
G = 6.67259e-11* u.N*u.m**2/(u.kg**2)  # G is the universal gravitation constant in Nm^2/kg^2
M_Earth = 5.97219e24*u.kg              # kg mass of body being orbitted, for this purpose using earth

# helpful functions

def _get_xyz(sc):
    '''
    Returns a 3 x len(sc) Quantity array of x,y,z coordinates of a given
    SkyCoord object.

    Parameters
    ----------
    sc : astropy.coordinates.SkyCoord

    Returns
    -------
    astropy.units.Quantity
        DESCRIPTION.

    '''
    sc_xyz = sc
    sc_xyz.representation_type = 'cartesian'
    return u.Quantity([sc_xyz.x,sc_xyz.y,sc_xyz.z]).T

def _rotate(vec,Omega,inc,w):
    '''
    After calculating cartesian coordinates of an orbit, rotate the orbit
    to account for non-zero longitude of ascending node, non-zero inclination,
    and non-zero argument of periapsis

    Parameters
    ----------
    vec : array-like
        Array of coordinates to be rotated.
    Omega : Quantity (angle)
        Longitude of ascending node.
    inc : Quantity (angle)
        Inclination of orbit.
    w : Quantity (angle)
        Argument of periapsis.

    Returns
    -------
    array-like
        Array of rotated coordintes.

    '''
    long_asc_node = np.array([[np.cos(Omega)    , np.sin(Omega) , 0],
                              [-1*np.sin(Omega) , np.cos(Omega) , 0],
                              [0                , 0             , 1]])
    
    incline = np.array([[np.cos(inc)      , 0  , np.sin(inc)],
                        [0                , 1  , 0          ],
                        [-1 * np.sin(inc) , 0  , np.cos(inc)]])

    periapsis = np.array([[np.cos(w)    , np.sin(w) , 0],
                          [-1*np.sin(w) , np.cos(w) , 0],
                          [0            , 0         , 1]])
    
    return vec.dot(long_asc_node).dot(incline).dot(periapsis)

def plot_accesses(ax,t,accesses):
    '''
    Creates a plot of pulsar access vs. time

    Parameters
    ----------
    ax : matplotlib.pyplot.Axes
        Subfigure in which to plot accesses.
    t : Time
        Observation time array.
    accesses : dict
        Access arrays for each pulsar.

    Returns
    -------
    ax : matplotlib.pyplot.Axes
        Subfigure with plotted accesses.

    '''
    ax.set_ylim([-1, len(accesses)])
    ax.set_yticks(np.arange(len(accesses.keys())))
    ax.set_yticklabels(accesses.keys())
    colors=['C'+str(i) for i in range(len(accesses))]
    
    for i, (pulsar, access_array) in enumerate(accesses.items()):

        access_df = pd.DataFrame(access_array,columns=['access'])
        has_access = access_df[access_df['access'] == True]

        for j in range(len(has_access)-1):
            xmin_j = t.datetime64[has_access.index[j]]
            xmax_j = t.datetime64[has_access.index[j]+1]

            ax.hlines(y=i,xmin=xmin_j,xmax=xmax_j,linewidth=1,colors=colors[i])
    
    return ax

# Orbital Mechanics Classes

class Trajectory(SkyCoord):
    def __init__(self,t,x,y,z,
                 *args, copy=True, 
                 V_x=0*u.m/u.s, V_y=0*u.m/u.s, V_z=0*u.m/u.s,
                 **kwargs):
        super().__init__(x=x,
                         y=y,
                         z=z,
                         obstime=t,
                         representation_type='cartesian',
                         frame='gcrs',
                         *args, **kwargs)
        
        if V_x > 0*u.m/u.s:
            self.V_x = V_x
            self.V_y = V_y
            self.V_z = V_z
    
    def separation_vec(self,space_object):
        sc_xyz = _get_xyz(self)
        so_xyz = _get_xyz(space_object)
        
        try:
            so_vec = so_xyz * np.ones([len(space_object),3])
        except TypeError:
            so_vec = so_xyz
        
        return so_vec - sc_xyz
    
    def pulsar_access(self,pulsar,*args):
        '''
        Returns an array of bool values representing when the spacecraft does and 
        does not have access to the pulsar based on obstruction by a given
        series of celestial bodies.

        Parameters
        ----------
        pulsar : TYPE
            DESCRIPTION.
        *args : tuple
            Celestial bodies to consider when calculating pulsar access, and 
            their respective radii. Elements of args should alternate in type
            between astropy.coordinates.SkyCoord and Quantity (distance).

        Returns
        -------
        access : numpy.array
            array of bool values representing pulsar access at corresponding index
            in spacecraft time array.

        '''
        
        # Parse *args into celestial objects and object radii
        objects = [obj for obj in args[::2]]
        radii = [radius for radius in args[1::2]]
        
        # Instantiate empty DataFrame where each column will represent pulsar
        # obfuscation by a different celestial body
        access_df = pd.DataFrame()
        
        # For each celestial body, calculate pulsar access
        for i in range(int(len(args)/2)):
            space_object = objects[i]
            object_rad = radii[i]
        
            s2o_vec = self.separation_vec(space_object)
            s2p_vec = self.separation_vec(pulsar)
            
            # s2o = self.separation_3d(space_object) # not working for some reason
            s2o_norm = np.linalg.norm(s2o_vec,axis=1)
            
            # sin(ang_s) = object_rad / s2o
            ang_S = np.arcsin(object_rad / s2o_norm)
            
            # tan(ang_BP) = ||s2p_vec x s2o_vec|| / (s2p dot s2o)
            cross = np.linalg.norm(np.cross(s2o_vec,s2p_vec),axis=1)
            dot = np.diag(np.dot(s2p_vec,s2o_vec.T))
            ang_BP = np.arctan2(cross,dot)
            
            access_obj = ang_BP > ang_S
            access_df[str(i)] = access_obj
        
        # Find truth value across each row for pulsar access at each obstime
        access = access_df.all(axis=1)
        return np.array(access)
    
    def pulsar_access_export(self,pulsar_qtbl,*args,
                             make_csv=True, save_csv=True, csv_name = 'access.csv',
                             make_fig=False, save_fig=True, fig_name = 'access.png'):
        '''
        Exports pulsar access data for a given pulsar accounting for 
        obfuscation from a given celestial body. The default is to create and 
        export a CSV, and the option to create and export a PNG plot is 
        included.

        Parameters
        ----------
        pulsar_qtbl : astropy.table.QTable
            QTable of pulsars and their coordinates. It is assumed that pulsar 
            QTables are given with columns NAME, RAJD, DECJD, and DIST, since
            these are the default column names given by the psrqpy package.
        *args : tuple
            Celestial bodies to consider when calculating pulsar access, and 
            their respective radii. Elements of args should alternate in type
            between astropy.coordinates.SkyCoord and Quantity (distance).
            
        make_csv : bool, optional
            Option to create pulsar access table. The default is True.
        save_csv : bool, optional
            Option to save pulsar access CSV. The detauls is True.
        csv_name : str, optional
            Filename of pulsar access CSV. The default is 'access.csv', but the
            file is only created if save_csv is True.
            
        make_fig : bool, optional
            Option to create pulsar access plot. The default is False.
        save_fig : bool, optional
            Option to export pulsar access plot PNG. The default is True, but
            the PNG is only exported if make_fig is also True.
        fig_name : str, optional
            Filename of pulsar access plot PNG. The default is 'access.png',
            the file is only created if save_fig is True.

        Returns
        -------
        tuple (pandas.DataFrame, 
               (matplotlib.pyplot.Figure,matplotlib.pyplot.Axes))
            Tuple of access DataFrame and/or access plot.
        '''
        # convert each row of QTable to GCRS cartesian SkyCoord and calculate
        # pulsar access for each one
        accesses = {}
        for pulsar in pulsar_qtbl:
            pulsar_sc = SkyCoord(ra = pulsar['RAJD'],
                          dec = pulsar['DECJD'],
                          distance = pulsar['DIST'])
            pulsar_sc = pulsar_sc.transform_to(self)
            
            pulsar_access = self.pulsar_access(pulsar_sc,*args)
            accesses[pulsar['NAME']] = pulsar_access
        
        # export CSV and plot PNG, if enabled in method call
        if make_csv:
            accesses_df = pd.DataFrame({'Time_JDate':self.obstime.jd,
                                        'Spacecraft_pos_X_km':self.x.to(u.km),
                                        'Spacecraft_pos_Y_km':self.y.to(u.km),
                                        'Spacecraft_pos_Z_km':self.z.to(u.km),
                                        'Spacecraft_vel_X_kmps':self.V_x.to(u.km/u.s),
                                        'Spacecraft_vel_Y_kmps':self.V_y.to(u.km/u.s),
                                        'Spacecraft_vel_Z_kmps':self.V_z.to(u.km/u.s),
                                        **accesses})
            if save_csv:
                accesses_df.to_csv(csv_name)
        else:
            accesses_df = None

        if make_fig:
            fig,ax = plt.subplots()
            ax = plot_accesses(ax, self.obstime, accesses)
            fig.set_figwidth(10)
            ax.set_title('Pulsar accesses between spacecraft and requested pulsars in requested time frame')
            
            if save_fig:
                fig.savefig(fig_name)
        else:
            fig = None
            ax = None
        
        return accesses_df,(fig,ax)
        
class EllipticalOrbit(Trajectory):
    def __init__(self,t,a,e,v_0=0*u.deg,M_body=M_Earth, # default body Earth
                 inc=0*u.deg,w=0*u.deg, # if you want to input orbital elements directly
                 B=None,dec=None,       # if you want to calculate orbital elements from orbital insertion
                 hifi=False,
                 Omega=0*u.deg,lambda2=None): # direct input of ascending node longitude vs. calculate from burnout longitude
        '''
        Initialization function for elliptical_orbit object.
        
        Parameters
        ----------
        t : Time
            Observation time array.
        a : Quantity (distance)
            Semi-major axis.
        e : float
            Eccentricity of orbit.
        v_0 : Quantity (angle), optional
            Initial true anomaly. This along with inclination and argument of 
            periapsis comprise the orbital elements of the trajectory. The 
            default is 0 degrees.
        M_body : Quantity (mass), optional
            Mass of celestial body around which the satellite will orbit.
            The default is 5.97219e24 kg, the mass of Earth.
            
        inc : Quantity (angle), optional
            Inclination of orbit. This along with argument of periapsis 
            comprise the orbital elements of the trajectory. The default is 
            0 degrees.
        w : Quantity (angle), optional
            Argument of periapsis. This along with inclination and initial true 
            anomaly comprise the orbital elements of the trajectory. The 
            default is 0 degrees.
            
        B : Quantity (angle), optional
            Azimuth heading, measured clockwise from north. The default is 
            None. This along with burnout latitude describe the location of the 
            spacecraft at orbital insertion, which can be used to calculate the
            orbital elements.
        dec : Quantity (angle), optional
            Geocentric latitude at burnout point. The default is None. his 
            along with azimuth heading describe the location of the spacecraft 
            at orbital insertion, which can be used to calculate the orbital 
            elements.
            
        hifi : bool, optional
            Tells the function whether to use the hi-fidelity version of the 
            eccentric anomaly calculation. The default is False.
            
        Omega : Quantity (angle), optional
            Longitude of ascending node. The default is 0 degrees.
        lambda2 : Quantity (angle), optional
            Geographical longitude of burnout point. The default is None. This
            can be used to calculate the longitude of the ascending node.

        Returns
        -------
        None.

        '''
        
        self.a = a
        self.e = e
        self.v_0 = v_0
        
        if B != None:
            self.B = B
            self.dec = dec
            
            self.l = np.arctan(np.tan(dec)/np.cos(B))
            
            self.w = self.l - self.v_0
            self.inc = np.arccos(np.cos(dec) * np.sin(B)) # inclination of orbit
            
        else:
            self.inc = inc
            self.w = w
            
        
        self.Ra = a*(1-e)   # apoapsis radii
        self.Rp = a*(1+e)   # periapsis radii
        
        # calculate anomaly parameters

        self.E_0 = np.arccos((e + np.cos(self.v_0))/
                             (1+e*np.cos(self.v_0)))  # initial eccentric anomaly
        
        self.M_0 = self.E_0 - e * np.sin(self.E_0) * u.rad  # initial mean anomaly at t_0
        self.n = np.sqrt(G*M_body / a**3) * u.rad           # mean motion, or average angular velocity
        
        delta_t = t - t[0]
        self.M_t = self.n*delta_t + self.M_0
        
        if hifi == True:
            self.E = self._calc_E(self.M_t,self.E_0, self.e)
            self.v = np.arccos((np.cos(self.E) - self.e) /   # anomoly as a 
                               (1 - self.e*np.cos(self.E)))  # function of t
        else:
            self.v = self.M_t + 2 * e * np.sin(self.M_t) * u.rad \
                              + 1.25 * e**2 * np.sin(2*self.M_t) * u.rad # lofi anomaly
            
        self.r_t = a*(1-e**2)/(1+e*np.cos(self.v))
        
        
        # Calculate x, y, z assuming ascending node at vernal equinox
        xyz_coords = u.Quantity([self.r_t * np.cos(self.v) * np.cos(self.inc),
                                 self.r_t * np.sin(self.v),
                                 self.r_t * np.sin(self.v) * np.sin(self.inc)]).T
        
        # Calculate and account for non-zero longitude of ascending node
        
        if lambda2 != None:
            delta_lambda = np.arctan(np.sin(dec) * np.tan(B))
            lambda1 = lambda2 - delta_lambda
            self.Omega = t[0].sidereal_time('apparent',longitude=lambda1)
        else:
            self.Omega = Omega
        
        xyz_coords_rot = _rotate(xyz_coords,self.Omega,self.inc,self.w)
        [x,y,z] = [xyz_coords_rot[:,i] for i in range(3)]
        
        super().__init__(t,x,y,z)
        
        self.ang = np.arctan(e*np.sin(self.v)/(1+e*np.cos(self.v))) # flight-path angle at any point
        self.V = np.sqrt(G*M_body*((2/self.r_t)-(1/a)))                   # spacecraft velocity at any point
        
        self.V_x = self.V * np.cos(self.v) * np.cos(self.inc)
        self.V_y = self.V * np.sin(self.v)
        self.V_z = self.V * np.sin(self.v) * np.sin(self.inc)
    
    
    def _calc_E(self,M,E_0,e):
        '''
        Calculates eccentric anomaly as a function of M at each obstime.
        Used only in the high fidelity version of the class.

        Parameters
        ----------
        M : Quantity array (angle)
            Mean anomaly as a function of t.
        E_0 : Quantity (angle)
            Initial eccentric anomaly.
        e : float
            Eccentricity of orbit.

        Returns
        -------
        Quantity array (angle)
            Eccentric anomaly array.

        '''
        E_list = []
        
        E = Symbol('E')
        E_temp = nsolve(E - (e * sin(E)) - float(M[0].to(u.rad)/u.rad),
                        E,
                        float(E_0.to(u.rad)/u.rad))
        E_list.append(E_temp)
        
        for i in range(1,len(M)):
            E_last = E_list[-1]
            E_temp = nsolve(E - e*sin(E) - float(M[i].to(u.rad)/u.rad),
                            E,
                            E_last)
            E_list.append(E_temp)
        
        return np.array(E_list)*u.rad
    
class CircularOrbit(EllipticalOrbit):
    def __init__(self,t,r,v_0=0*u.deg,M_body=M_Earth):
        '''
        Special case of the EllipticalOrbit class in which eccentricity and 
        orbital inclination are zero. 

        Parameters
        ----------
        t : Time
            Observation time array.
        r : Quantity (distance)
            Orbital radius.
        v_0 : Quantity (angle), optional
            Initial true anomaly. The default is 0 degrees.
        M_body : Quantity (mass), optional
            Mass of celestial body around which the satellite will orbit.
            The default is 5.97219e24 kg, the mass of Earth.
        
        Returns
        -------
        None.

        '''
        
        e = 0
        a = r
        
        super().__init__(t,a,e,v_0,M_body)
        
        self.r = r
        
        self.V = np.sqrt(G*M_body/r)
        self.W = self.V/r * u.rad
        
        self.V_x = self.V * np.cos(self.v)
        self.V_y = self.V * np.sin(self.v)
        self.V_z = 0 * u.m / u.s