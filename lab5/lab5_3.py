import subprocess
import numpy as np
from scipy import signal
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row, gridplot
from bokeh.models import Button, CheckboxGroup, Select, Slider
from bokeh.models import Div

INITIAL_AMPLITUDE = 1.0
INITIAL_FREQUENCY = 1.0
INITIAL_PHASE = 0.0
INITIAL_NOISE_MEAN = 0.0
INITIAL_NOISE_DISPERSION = 0.1
SHOW_NOISE_FLAG = True
BASE_NOISE_ARRAY = np.random.normal(0, 1, 1000)

def create_new_noise():
    global BASE_NOISE_ARRAY
    BASE_NOISE_ARRAY = np.random.normal(0, 1, 1000)
    update_plot(None, None, None)

def harmonic_signal_with_noise(amplitude, frequency, phase, noise_mean, noise_dispersion, SHOW_NOISE_FLAG=True):
    t = np.linspace(0, 10, 1000)
    y = amplitude * np.sin(2 * np.pi * frequency * t + phase)

    if SHOW_NOISE_FLAG:
        scaled_noise = noise_mean + np.sqrt(noise_dispersion) * BASE_NOISE_ARRAY
        y += scaled_noise

    return t, y

def apply_filter(y, filter_type, gaussian_std=2, gaussian_window=5, uniform_window=5, median_window=5):
    if filter_type == "gaussian":
        window = signal.windows.gaussian(gaussian_window, std=gaussian_std)
        filtered_y = signal.convolve(y, window / window.sum(), mode='same')
    elif filter_type == "uniform":
        filtered_y = np.convolve(y, np.ones(uniform_window) / uniform_window, mode='same')
    elif filter_type == "median":
        filtered_y = median_filter(y, median_window)

    return filtered_y

def median_filter(y, window_size):
    filtered_y = np.zeros_like(y)
    half_window = window_size // 2
    for i in range(half_window, len(y) - half_window):
        window = y[i - half_window:i + half_window + 1]
        filtered_y[i] = np.median(window)
    return filtered_y

plot1 = figure(title="Гармоніка з накладеним шумом", x_axis_label='Час (с)', y_axis_label='Амплітуда',
               x_axis_type="linear", y_axis_type="linear")

plot2 = figure(title="Відфільтрована гармоніка", x_axis_label='Час (с)', y_axis_label='Амплітуда',
               x_axis_type="linear", y_axis_type="linear")

line1 = plot1.line([], [], line_width=3, line_color="green", line_alpha=0.8, line_cap="round", line_join="round")

line2 = plot2.line([], [], line_width=3, line_color="blue", line_alpha=0.8, line_cap="round", line_join="round")

amp_slider = Slider(title="Амплітуда", value=INITIAL_AMPLITUDE, start=0.1, end=5.0, step=0.1)
freq_slider = Slider(title="Частота", value=INITIAL_FREQUENCY, start=0.1, end=5.0, step=0.1)
phase_slider = Slider(title="Фаза", value=INITIAL_PHASE, start=-np.pi, end=np.pi, step=0.1)
noise_mean_slider = Slider(title="Шум (середнє)", value=INITIAL_NOISE_MEAN, start=-1.0, end=1.0, step=0.1)
noise_dispersion_slider = Slider(title="Шум (дисперсія)", value=INITIAL_NOISE_DISPERSION, start=0.01, end=1.0, step=0.01)
gaussian_window_slider = Slider(title="Gaussian Window", value=5, start=3, end=100, step=2)
gaussian_std_slider = Slider(title="Gaussian STD", value=2, start=0.1, end=8.0, step=0.1)
uniform_window_slider = Slider(title="Uniform Window", value=5, start=3, end=100, step=2)
median_window_slider = Slider(title="Median Window", value=5, start=3, end=100, step=2)

checkbox_group = CheckboxGroup(labels=["Показати шум"], active=[0], width=200)

filter_menu = Select(title="Згладжування", value="none", options=["none", "gaussian", "uniform", "median"], width=200)

reset_parameters_button = Button(label="Скинути", button_type="success", width=100)
new_noise_button = Button(label="Новий шум", button_type="warning", width=100)

def update_plot(attr, old, new):
    amplitude = amp_slider.value
    frequency = freq_slider.value
    phase = phase_slider.value
    noise_mean = noise_mean_slider.value
    noise_dispersion = noise_dispersion_slider.value
    SHOW_NOISE_FLAG = False in checkbox_group.active
    filter_type = filter_menu.value
    gaussian_std = gaussian_std_slider.value
    gaussian_window = int(gaussian_window_slider.value)
    uniform_window = int(uniform_window_slider.value)
    median_window = median_window_slider.value

    t, y = harmonic_signal_with_noise(amplitude, frequency, phase, noise_mean, noise_dispersion, SHOW_NOISE_FLAG)
    line1.data_source.data = {'x': t, 'y': y}
    plot1.title.text = f'Гармоніка з накладеним шумом (A={amplitude:.2f}, f={frequency:.2f}, φ={phase:.2f})'

    if filter_type == "none":
        filtered_y = y
    else:
        filtered_y = apply_filter(y, filter_type, gaussian_std, gaussian_window, uniform_window, median_window)

    line2.data_source.data = {'x': t, 'y': filtered_y}

def reset_parameters():
    amp_slider.value = INITIAL_AMPLITUDE
    freq_slider.value = INITIAL_FREQUENCY
    phase_slider.value = INITIAL_PHASE
    noise_mean_slider.value = INITIAL_NOISE_MEAN
    noise_dispersion_slider.value = INITIAL_NOISE_DISPERSION
    filter_menu.value = "none"
    update_plot(None, None, None)

amp_slider.on_change('value', update_plot)
freq_slider.on_change('value', update_plot)
phase_slider.on_change('value', update_plot)
noise_mean_slider.on_change('value', update_plot)
noise_dispersion_slider.on_change('value', update_plot)
checkbox_group.on_change('active', update_plot)
filter_menu.on_change('value', update_plot)
gaussian_std_slider.on_change('value', update_plot)
uniform_window_slider.on_change('value', update_plot)
median_window_slider.on_change('value', update_plot)
gaussian_window_slider.on_change('value', update_plot)
reset_parameters_button.on_click(reset_parameters)
new_noise_button.on_click(create_new_noise)

category_gaussian = Div(text="<b>Фільтр Гауса</b>", width=200) 
category_uniform = Div(text="<b>Фільтр з рівномірним вікном</b>", width=200)
category_median = Div(text="<b>Медіанний фільтр</b>", width=200)
category_sliders = Div(text="<b>Параметри сигналу</b>", width=200)
category_buttons = Div(text="<b>Управління</b>", width=200)

layout = column(
    gridplot([[plot1, plot2]], toolbar_location="above"), 
    category_sliders,
    row(noise_mean_slider, noise_dispersion_slider),
    row(amp_slider, freq_slider, phase_slider),
    category_gaussian,
    row(gaussian_std_slider, gaussian_window_slider),
    category_uniform,
    row(uniform_window_slider),
    category_median,
    row(median_window_slider),
    category_buttons,
    row(new_noise_button, reset_parameters_button, filter_menu, checkbox_group)
)
curdoc().add_root(layout)

if __name__ == "__main__":
    subprocess.run(["bokeh", "serve", "--show", __file__])
