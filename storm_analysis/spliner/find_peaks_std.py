#!/usr/bin/env python
"""
Cubic spline peak finder.

Hazen 03/16
"""

import pickle
import numpy

import tifffile

import storm_analysis.sa_library.fitting as fitting
import storm_analysis.sa_library.ia_utilities_c as utilC
import storm_analysis.sa_library.matched_filter_c as matchedFilterC

import storm_analysis.spliner.cubic_fit_c as cubicFitC
import storm_analysis.spliner.spline_to_psf as splineToPSF


def initFitter(finder, parameters, spline_fn):
    """
    Initialize and return a cubicFitC.CSplineFit object.
    """
    # Load variance, scale by gain.
    #
    # Variance is in units of ADU*ADU.
    # Gain is ADU/photo-electron.
    #
    variance = None
    if parameters.hasAttr("camera_calibration"):
        [offset, variance, gain] = numpy.load(parameters.getAttr("camera_calibration"))
        variance = variance/(gain*gain)

        # Set variance in the peak finder, this method also pads the
        # variance to the correct size.
        variance = finder.setVariance(variance)
    
    # Create C fitter object.
    if (spline_fn.getType() == "2D"):
        return cubicFitC.CSpline2DFit(scmos_cal = variance,
                                      spline_fn = spline_fn)
    else:
        return cubicFitC.CSpline3DFit(scmos_cal = variance,
                                      spline_fn = spline_fn)
    
def initFindAndFit(parameters):
    """
    Initialize and return a SplinerFinderFitter object.
    """
    # Create spline object.
    spline_fn = splineToPSF.loadSpline(parameters.getAttr("spline"))    
        
    # Create peak finder.
    finder = fitting.PeakFinderArbitraryPSF(parameters = parameters,
                                            psf_object = spline_fn)

    # Create cubicFitC.CSplineFit object.
    mfitter = initFitter(finder, parameters, spline_fn)
    
    # Create peak fitter.
    fitter = fitting.PeakFitterArbitraryPSF(mfitter = mfitter,
                                            parameters = parameters)

    # Specify which properties we want from the analysis.
    properties = ["background", "error", "height", "x", "y", "z"]
    
    return fitting.PeakFinderFitter(peak_finder = finder,
                                    peak_fitter = fitter,
                                    properties = properties)
