'''
A container for custom types.
'''
from .types import *
from .enums import *

# This is a combination from both types and enums, this seems to be the best place for it
type PlotData = tuple[PlotInput, PlotInput, SamplePoints, AnalysisMethod]