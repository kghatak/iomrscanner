#!/usr/bin/env python3
"""
Pipeline package for modular image processing stages.
"""

from .pipeline_stages import (
    PipelineStage,
    PipelineManager,
    ArUcoCheckStage,
    OrientationCheckStage,
    RollNumberExtractionStage,
    OMRProcessingStage,
    OMRProcessingSecondStage,
    OMRAnswerExtractionStage,
    APIUploadStage
)

__all__ = [
    'PipelineStage',
    'PipelineManager',
    'ArUcoCheckStage',
    'OrientationCheckStage',
    'RollNumberExtractionStage',
    'OMRProcessingStage',
    'OMRProcessingSecondStage',
    'OMRAnswerExtractionStage',
    'APIUploadStage'
]

__version__ = '1.0.0'
