import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons, RadioButtons

INITIAL_AMPLITUDE = 1.0
INITIAL_FREQUENCY = 1.0
INITIAL_PHASE = 0.0
INITIAL_NOISE_MEAN = 0.0
INITIAL_NOISE_DISPERSION = 0.1
SHOW_NOISE_FLAG = True
BASE_NOISE_ARRAY = np.random.normal(0, 1, 1000)

def create_new_noise(event):
    global BASE_NOISE_ARRAY
    BASE_NOISE_ARRAY = np.random.normal(0, 1, 1000)
    update_plot(None)

def harmonic_signal_with_noise(amplitude, frequency, phase, noise_mean, noise_dispersion, show_noise=True):
    time = np.linspace(0, 10, 1000)
    harmonic_signal = amplitude * np.sin(2 * np.pi * frequency * time + phase)

    if show_noise:
        scaled_noise = noise_mean + np.sqrt(noise_dispersion) * BASE_NOISE_ARRAY
        harmonic_signal += scaled_noise

    return time, harmonic_signal

def apply_filter(input_signal, filter_type='None', sigma=None, window_size=None):
    if filter_type == 'None':
        filtered_signal = input_signal
    elif filter_type == 'Gaussian':
        window = signal.windows.gaussian(window_size, std=sigma)
        filtered_signal = signal.convolve(input_signal, window / window.sum(), mode='same')
    elif filter_type == 'Uniform':
        window = np.ones(window_size) / window_size
        filtered_signal = signal.convolve(input_signal, window, mode='same')
    return filtered_signal

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1.5, 1.5]})
plt.subplots_adjust(bottom=0.6, hspace=0.9)

time, original_signal = harmonic_signal_with_noise(INITIAL_AMPLITUDE, INITIAL_FREQUENCY, INITIAL_PHASE,
                                                   INITIAL_NOISE_MEAN, INITIAL_NOISE_DISPERSION, SHOW_NOISE_FLAG)
filtered_signal = apply_filter(original_signal, 'None')

line1, = ax1.plot(time, original_signal, lw=2, color='b', label='Оригінальний сигнал')
line2, = ax2.plot(time, filtered_signal, lw=2, color='g', label='Відфільтрований сигнал')

ax1.set_xlabel('Час (с)')
ax1.set_ylabel('Амплітуда')
ax1.set_title('Гармоніка з накладеним шумом')

ax2.set_xlabel('Час (с)')
ax2.set_ylabel('Амплітуда')
ax2.set_title('Відфільтрована гармоніка')

ax_phase = plt.axes([0.25, 0.5, 0.65, 0.03])
phase_slider = Slider(ax_phase, 'Фаза', -np.pi, np.pi, valinit=INITIAL_PHASE, valstep=0.1)

ax_frequency = plt.axes([0.25, 0.45, 0.65, 0.03])
freq_slider = Slider(ax_frequency, 'Частота', 0.1, 5.0, valinit=INITIAL_FREQUENCY, valstep=0.005)

ax_amplitude = plt.axes([0.25, 0.4, 0.65, 0.03])
amp_slider = Slider(ax_amplitude, 'Амплітуда', 0.1, 5.0, valinit=INITIAL_AMPLITUDE, valstep=0.05)

ax_noise_mean = plt.axes([0.25, 0.35, 0.65, 0.03])
noise_mean_slider = Slider(ax_noise_mean, 'Шум (середнє)', -1.0, 1.0, valinit=INITIAL_NOISE_MEAN, valstep=0.01)

ax_noise_dispersion = plt.axes([0.25, 0.3, 0.65, 0.03])
noise_dispersion_slider = Slider(ax_noise_dispersion, 'Шум (дисперсія)', 0.01, 1.0, valinit=INITIAL_NOISE_DISPERSION,
                                 valstep=0.01)

ax_sigma = plt.axes([0.25, 0.25, 0.65, 0.03])
sigma_slider = Slider(ax_sigma, 'Sigma STD', 0.1, 8, valinit=2.0, valstep=0.05)

ax_window_size = plt.axes([0.25, 0.2, 0.65, 0.03])
window_size_slider = Slider(ax_window_size, 'Window Size', 3, 21, valinit=5, valstep=2)

ax_checkbox = plt.axes([0.7, 0.9, 0.2, 0.05])
checkbox = CheckButtons(ax_checkbox, ['Показати шум'], [SHOW_NOISE_FLAG])

ax_filter_type = plt.axes([0.3, 0.07, 0.4, 0.1])
filter_type_buttons = RadioButtons(ax_filter_type, ['None', 'Uniform', 'Gaussian'], active=0)

reset_button_ax = plt.axes([0.35, 0.01, 0.1, 0.04])
reset_button = Button(reset_button_ax, 'Reset')

ax_new_noise_button = plt.axes([0.55, 0.01, 0.1, 0.04])
new_noise_button = Button(ax_new_noise_button, 'Новий шум')

def update_plot(val):
    amplitude = amp_slider.val
    frequency = freq_slider.val
    phase = phase_slider.val
    noise_mean = noise_mean_slider.val
    noise_dispersion = noise_dispersion_slider.val
    show_noise = checkbox.get_status()[0]
    filter_type = filter_type_buttons.value_selected

    sigma = sigma_slider.val if filter_type == 'Gaussian' else None
    window_size = int(window_size_slider.val) if filter_type in ['Gaussian', 'Uniform'] else None

    time, signal = harmonic_signal_with_noise(amplitude, frequency, phase, noise_mean, noise_dispersion, show_noise)
    filtered_signal = apply_filter(signal, filter_type, sigma, window_size)

    line1.set_data(time, signal)
    line2.set_data(time, filtered_signal)

    ax1.set_title(f'Гармоніка з накладеним шумом (A={amplitude:.2f}, f={frequency:.2f}, φ={phase:.2f})')

    if filter_type == 'None':
        ax2.set_title('Відфільтрована гармоніка (без фільтрації)')
    else:
        ax2.set_title(f'Відфільтрована гармоніка (тип={filter_type})')
    fig.canvas.draw_idle()

def reset_parameters(event):
    amp_slider.reset()
    freq_slider.reset()
    phase_slider.reset()
    noise_mean_slider.reset()
    noise_dispersion_slider.reset()
    filter_type_buttons.set_active(0)
    sigma_slider.reset()
    window_size_slider.reset()
    update_plot(None)

amp_slider.on_changed(update_plot)
freq_slider.on_changed(update_plot)
phase_slider.on_changed(update_plot)
noise_mean_slider.on_changed(update_plot)
noise_dispersion_slider.on_changed(update_plot)
checkbox.on_clicked(update_plot)
filter_type_buttons.on_clicked(update_plot)
sigma_slider.on_changed(update_plot)
window_size_slider.on_changed(update_plot)
new_noise_button.on_clicked(create_new_noise)
reset_button.on_clicked(reset_parameters)

plt.show()
