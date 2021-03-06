from typing import Tuple
from xicam.plugins.operationplugin import operation, output_names, display_name, describe_input, describe_output, \
    categories, plot_hint
import numpy as np
from pyFAI.azimuthalIntegrator import AzimuthalIntegrator


@operation
@output_names("q_z", "I")
@display_name("Z Integration")
@describe_input("azimuthal_integrator", 'A PyFAI.AzimuthalIntegrator object')
@describe_input("data", '2d array representing intensity for each pixel')
@describe_input("mask", 'Array (same size as image) with 1 for masked pixels, and 0 for valid pixels')
@describe_input("dark", "Dark noise image")
@describe_input("flat", "Flat field image")
@describe_input("normalization_factor", 'Value of normalization monitor')
@describe_output("q", 'q_z bin center positions')
@describe_output("I", "Binned/pixel-split integrated intensity")
@categories(("Scattering", "Integration"))
@plot_hint("q_z", "I", name="Z Integration")
def z_integrate(azimuthal_integrator: AzimuthalIntegrator,
                data: np.ndarray,
                mask: np.ndarray,
                dark: np.ndarray,
                flat: np.ndarray,
                normalization_factor: float = 1) -> Tuple[np.ndarray, np.ndarray]:
    if dark is None: dark = np.zeros_like(data)
    if flat is None: flat = np.ones_like(data)
    if mask is None: mask = np.zeros_like(data)
    I = np.sum((data - dark) * np.average(flat - dark) / (
            flat - dark) / normalization_factor * np.logical_not(mask), axis=1)[::-1]
    centerx = azimuthal_integrator.getFit2D()['centerX']
    centerz = azimuthal_integrator.getFit2D()['centerY']
    q_z = azimuthal_integrator.qFunction(np.arange(0, data.shape[0]),
                                         np.array([centerx] * data.shape[0])) / 10
    q_z[np.arange(0, data.shape[0]) < centerz] *= -1.

    return q_z, I
