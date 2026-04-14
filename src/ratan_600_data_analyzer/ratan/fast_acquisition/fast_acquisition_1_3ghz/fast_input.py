import numpy as np
import pandas as pd
from itertools import groupby
import plotly.colors
from PIL import ImageColor

CHUNK_LENGTH = 0x80
POLARIZATION_MASK = 0b00000000000010000000000000000000

dt = np.dtype([
    ('cnt', '<u4'),
    ('avg_kurt', '<u4'),
    ('state', '<u4'),
    ('channel', '<u4'),
    ('data', '<u8', 0x80)
])


def get_polarization_arrays(raw_array, channel):
    def align_to_chunk_length(length):
        return ((length + 1) // CHUNK_LENGTH) * CHUNK_LENGTH

    # Select elements of the channel
    if channel == 0:
        a = raw_array[raw_array['channel'] == 0]
    elif channel == 1:
        a = raw_array[raw_array['channel'] != 0]
    else:
        raise ValueError(f'Bad channel number: {channel}. Must be 0 or 1.')

    # Separate two polarizations
    p0 = a[(a['state'] & POLARIZATION_MASK) == 0]
    p1 = a[(a['state'] & POLARIZATION_MASK) != 0]

    # Find max frame numbers
    p0_maxindex = p0['cnt'].max() if p0.size > 0 else 0
    p1_maxindex = p1['cnt'].max() if p1.size > 0 else 0

    # Make the array size a multiple of chunk (ethernet frame payload) size throwing away any possible trailing trash
    p0_length = align_to_chunk_length(p0_maxindex)
    p1_length = align_to_chunk_length(p1_maxindex)
    p0 = p0[p0['cnt'] < p0_length]
    p1 = p1[p1['cnt'] < p1_length]

    # Construct zero arrays to accomodate the full data in the case when there are no missing values
    # and fill them with the available data
    r_p0 = np.zeros(p0_length, dtype=dt)
    r_p0[p0['cnt']] = p0
    r_p1 = np.zeros(p1_length, dtype=dt)
    r_p1[p1['cnt']] = p1

    return r_p0, r_p1


def get_data_and_kurtosis(a, spectrum_length):
    cc = a['data'].reshape(-1, spectrum_length)
    state = np.empty(a['data'].shape, dtype=np.uint32)
    for i in np.arange(0, state.shape[0]):
        state[i, :] = a['state'][i]
    state = state.reshape(-1, spectrum_length)
    return (cc & 0x7FFFFFFFFFFFFF).astype(np.float32), (cc >> 55).astype(np.float32), state


def remove_spikes_from_polarization_arrays(a, b, shift=-4):
    idx_a = np.roll((a['cnt'] > 0), shift, axis=0)
    idx_b = np.roll((b['cnt'] > 0), shift, axis=0)
    a[idx_b] = 0
    b[idx_a] = 0

    return a, b


def get_data_from_file(file_name, remove_spikes=True):
    block_array = np.fromfile(file_name, dtype=dt)
    return get_data(block_array, remove_spikes=True)


def get_data(block_array, remove_spikes=True):
    avg_num = 2 ** (block_array[0]['avg_kurt'] & 0b111111)
    spectrum_length = 8192 // avg_num

    chan0_pol0, chan0_pol1 = get_polarization_arrays(block_array, channel=0)
    chan1_pol0, chan1_pol1 = get_polarization_arrays(block_array, channel=1)

    if remove_spikes:
        chan0_length = min(chan0_pol0.shape[0], chan0_pol1.shape[0])
        if chan0_length > 0:
            chan0_pol0, chan0_pol1 \
                = remove_spikes_from_polarization_arrays(chan0_pol0[:chan0_length], chan0_pol1[:chan0_length])
        chan1_length = min(chan1_pol0.shape[0], chan1_pol1.shape[0])
        if chan1_length > 0:
            chan1_pol0, chan1_pol1 \
                = remove_spikes_from_polarization_arrays(chan1_pol0[:chan1_length], chan1_pol1[:chan1_length])

    c0p0_data, c0p0_kurtosis, c0p0_state = get_data_and_kurtosis(chan0_pol0, spectrum_length)
    c0p1_data, c0p1_kurtosis, c0p1_state = get_data_and_kurtosis(chan0_pol1, spectrum_length)
    c1p0_data, c1p0_kurtosis, c1p0_state = get_data_and_kurtosis(chan1_pol0, spectrum_length)
    c1p1_data, c1p1_kurtosis, c1p1_state = get_data_and_kurtosis(chan1_pol1, spectrum_length)

    return c0p0_data, c0p1_data, c1p0_data, c1p1_data, \
        c0p0_kurtosis, c0p1_kurtosis, c1p0_kurtosis, c1p1_kurtosis, \
        c0p0_state, c0p1_state, c1p0_state, c1p1_state


def get_mixed_data_from_file(file_name):
    block_array = np.fromfile(file_name, dtype=dt)
    avg_num = 2 ** (block_array[0]['avg_kurt'] & 0b111111)
    spectrum_length = 8192 // avg_num

    def align_to_spectrum_length(length):
        return ((length + 1) // spectrum_length) * spectrum_length

    chan0 = block_array[block_array['channel'] == 0]
    chan1 = block_array[block_array['channel'] != 1]

    c0_maxindex = chan0['cnt'].max()
    c1_maxindex = chan1['cnt'].max()

    c0_length = align_to_spectrum_length(c0_maxindex)
    c1_length = align_to_spectrum_length(c1_maxindex)

    c_length = max(c0_length, c1_length)

    c0 = chan0[chan0['cnt'] < c_length]
    c1 = chan1[chan1['cnt'] < c_length]

    r_c = np.zeros((2, c_length), dtype=dt)
    r_c[0, c0['cnt']] = c0
    r_c[1, c1['cnt']] = c1

    r_c[0]['cnt'] = np.arange(len(r_c[0]))
    r_c[1]['cnt'] = np.arange(len(r_c[1]))

    return r_c


def replace_nan(a, axis=0):
    # return np.nan_to_num(a)
    return pd.DataFrame(a).interpolate(axis=axis, method='linear').to_numpy()


def replace_nan_awgn(b, axis=0):
    c = b.copy()
    a = np.moveaxis(c, axis, -1)

    for j, vec in enumerate(a):
        keyfunc = lambda x: np.isnan(x)
        variances = []
        groups = []
        for key, group in groupby(vec, keyfunc):
            y = np.array(list(group))
            groups.append({'key': key, 'data': y})
            if key == True:
                variances.append(np.nan)
            else:
                variances.append(np.sqrt(y.var()))

        vars_n = pd.Series(variances).interpolate(method='linear').to_numpy()
        if np.isnan(vars_n[0]) and len(vars_n) > 1:
            vars_n[0] = vars_n[1]
        if np.isnan(vars_n[-1]) and len(vars_n) > 1:
            vars_n[-1] = vars_n[-2]

        for i, group in enumerate(groups):
            if group['key']:
                group['data'] = np.random.normal(0, vars_n[i], group['data'].shape[0])
            else:
                group['data'] = np.zeros(group['data'].shape[0])

        noise = np.concatenate(list(map(lambda x: x['data'], groups)))
        a[j] = pd.Series(vec).interpolate(method='linear').to_numpy() + noise
    return c


def replace_val(a, k, value=0., axis=0):
    a[a == value] = np.nan
    k[a == value] = 512.
    # return np.apply_along_axis(replace_nan, 0, a), k
    return pd.DataFrame(a).interpolate(axis=axis, method='linear').to_numpy(), k
    # return pd.DataFrame(a).fillna(axis=axis, value=0).to_numpy(), k


def get_color(colorscale_name, loc):
    from _plotly_utils.basevalidators import ColorscaleValidator

    # first parameter: Name of the property being validated
    # second parameter: a string, doesn't really matter in our use case
    cv = ColorscaleValidator("colorscale", "")
    # colorscale will be a list of lists: [[loc1, "rgb1"], [loc2, "rgb2"], ...]
    colorscale = cv.validate_coerce(colorscale_name)

    if hasattr(loc, "__iter__"):
        return [get_continuous_color(colorscale, x) for x in loc]
    return get_continuous_color(colorscale, loc)


def get_continuous_color(colorscale, intermed):
    """
    Plotly continuous colorscales assign colors to the range [0, 1]. This function computes the intermediate
    color for any value in that range.

    Plotly doesn't make the colorscales directly accessible in a common format.
    Some are ready to use:

    colorscale = plotly.colors.PLOTLY_SCALES["Greens"]

    Others are just swatches that need to be constructed into a colorscale:

    viridis_colors, scale = plotly.colors.convert_colors_to_same_type(plotly.colors.sequential.Viridis)
    colorscale = plotly.colors.make_colorscale(viridis_colors, scale=scale)

    :param colorscale: A plotly continuous colorscale defined with RGB string colors.
    :param intermed: value in the range [0, 1]
    :return: color in rgb string format
    :rtype: str
    """
    if len(colorscale) < 1:
        raise ValueError("colorscale must have at least one color")

    hex_to_rgb = lambda c: "rgb" + str(ImageColor.getcolor(c, "RGB"))

    if intermed <= 0 or len(colorscale) == 1:
        c = colorscale[0][1]
        return c if c[0] != "#" else hex_to_rgb(c)
    if intermed >= 1:
        c = colorscale[-1][1]
        return c if c[0] != "#" else hex_to_rgb(c)

    for cutoff, color in colorscale:
        if intermed > cutoff:
            low_cutoff, low_color = cutoff, color
        else:
            high_cutoff, high_color = cutoff, color
            break

    if (low_color[0] == "#") or (high_color[0] == "#"):
        # some color scale names (such as cividis) returns:
        # [[loc1, "hex1"], [loc2, "hex2"], ...]
        low_color = hex_to_rgb(low_color)
        high_color = hex_to_rgb(high_color)

    return plotly.colors.find_intermediate_color(
        lowcolor=low_color,
        highcolor=high_color,
        intermed=((intermed - low_cutoff) / (high_cutoff - low_cutoff)),
        colortype="rgb",
    )
