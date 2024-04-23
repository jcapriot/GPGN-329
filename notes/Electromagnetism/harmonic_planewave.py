from ipywidgets import *
import numpy as np
import matplotlib.pyplot as plt

import discretize
from SimPEG.electromagnetics.natural_source.utils import getEHfields

class LayeredPlaneWaveInteract():


    def __init__(self, sigma, f, h, zmin=-1000, zmax=0, nx=512):

        h = h[:-1]
        h = np.r_[h, h[-1]]
        h = h[::-1]

        self._f  = f
        self._sigma = sigma[::-1]
        dt = 1/(f*256)
        self._mesh = discretize.TensorMesh([h[::-1],], origin='N')
        self._t0 = 0.0
        self._dt = dt
        self._zs = np.linspace(zmin, zmax, nx)

        self._i_time = 0

        self._play = Play(
            value=0,
            min=0,
            max=10000,
            step=1,
            interval=int(1000 * dt), #ms = 0.01
            description='Run',
            disabled=False,
        )

        with plt.ioff():
            fig, ax = plt.subplots(1,1)
        self._fig = fig

        e_v, h_v = self.get_wave()
        self._er_line, = ax.plot(e_v.real, self._zs, color='C0')
        self._ei_line, = ax.plot(e_v.imag, self._zs, color='C0',linestyle='--')
        self._hr_line, = ax.plot(h_v.real, self._zs, color='C1')
        self._hi_line, = ax.plot(h_v.imag, self._zs, color='C1',linestyle='--')

        for z in self._mesh.nodes_x[1:]:
            ax.axhline(z, color='k', alpha=0.5)

        def replot():
            e_v, h_v = self.get_wave()
            self._er_line.set_xdata(e_v.real)
            self._ei_line.set_xdata(e_v.imag)
            self._hr_line.set_xdata(h_v.real)
            self._hi_line.set_xdata(h_v.imag)

        def interact_play(change):
            replot()
            self._i_time = self._play.value
        self._play.observe(interact_play)

        # assemble:

        self._box = VBox([fig.canvas, self._play])

    def display(self):
        return self._box

    def get_wave(self):
        z = self._zs
        Ed, Eu, Hd, Hu = getEHfields(self._mesh, self._sigma, self._f, z)
        E = Ed + Eu
        H = Hd + Hu
        t = self._t0 + self._dt*self._i_time
        E = E * np.exp(2j * np.pi * self._f * t)
        H = H * np.exp(2j * np.pi * self._f * t)
        return E, H


    

    
    