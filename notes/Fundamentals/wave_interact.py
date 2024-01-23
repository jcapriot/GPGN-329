from ipywidgets import *
import numpy as np
import matplotlib.pyplot as plt


class WaveInteract():

    def __init__(self, t0=0.0, dt=0.01, xmin=0.0, xmax=5, nx=512):

        self._constant_c = Checkbox(
            value=False,
            description='Hold Speed Constant?',
            disabled=False,
            indent=False,
        )

        self._frequency = FloatLogSlider(
            value=1.0,
            description='Frequency (Hz)',
            min=-1,
            max=0,
            step=0.01,
            disabled=False,
            continuous_update=True,
            readout=True,
            base=10,
            # readout_format='.1f',
        )

        self._spatial_frequency = FloatLogSlider(
            value=1.0,
            description='Spatial Frequency (1/m)',
            min=-1,
            max=0,
            step=0.01,
            disabled=False,
            continuous_update=True,
            readout=True,
            readout_format='.1f',
        )

        self._speed = self.frequency / self.spatial_frequency
        self._speed_label = Label(
            value=f'Wave Speed {self.speed:.2f}(m/s)',
        )

        self._t0 = t0
        self._dt = dt
        self._xs = np.linspace(xmin, xmax, nx)

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

        self._direction = RadioButtons(
            options=['left', 'right'],
            description='Wave direction',
            disabled=False,
        )

        with plt.ioff():
            fig, ax = plt.subplots(1,1)
        self._fig = fig

        u_r, u_i = self.get_wave()
        self._real_line, = ax.plot(self._xs, u_r)
        self._comp_line, = ax.plot(self._xs, u_i)

        def replot():
            u_r, u_i = self.get_wave()
            self._real_line.set_ydata(u_r)
            self._comp_line.set_ydata(u_i)

        self.interacting_sf = False
        self.interacting_tf = False
        def observe_spatial_frequency(change):
            if not self.interacting_tf:
                self.interacting_sf = True
                if self._constant_c.value:
                    self._frequency.value = self.speed * self.spatial_frequency
                else:
                    self._speed = self.frequency / self.spatial_frequency
                self._speed_label.value = f'Wave Speed {self.speed:.2f}(m/s)'
                replot()
                self.interacting_sf = False
        self._spatial_frequency.observe(observe_spatial_frequency)

        def interact_frequency(change):
            if not self.interacting_sf:
                self.interacting_tf = True
                if self._constant_c.value:
                    self._spatial_frequency.value = self.frequency / self.speed
                else:
                    self._speed = self.frequency / self.spatial_frequency
                self._speed_label.value = f'Wave Speed {self.speed:.2f}(m/s)'
                replot()
                self.interacting_tf = False
        self._frequency.observe(interact_frequency)

        def interact_play(change):
            replot()
            self._i_time = self._play.value
        self._play.observe(interact_play)

        # assemble:
        left = VBox([self._frequency, self._spatial_frequency, self._speed_label, self._constant_c, self._direction, self._play])

        self._box = HBox([left, fig.canvas])

    def display(self):
        return self._box

    def get_wave(self):
        x = self._xs
        t = self._t0 + self._dt * self._i_time
        k = self.wave_number
        if self._direction.value == 'left':
            k *= -1
        omega = self.angular_frequency
        phase = omega * t - k * x
        return np.cos(phase), np.sin(phase)

    @property
    def angular_frequency(self):
        return 2 * np.pi * self.frequency

    @property
    def frequency(self):
        return self._frequency.value

    @property
    def wave_number(self):
        return 2 * np.pi * self.spatial_frequency

    @property
    def spatial_frequency(self):
        return self._spatial_frequency.value

    @property
    def speed(self):
        return self._speed# self.frequency/self.spatial_frequency

    @property
    def period(self):
        return 1.0/self.frequency

    @property
    def wavelength(self):
        return 1.0/self.spatial_frequency


