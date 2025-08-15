# AI Bypass Node Documentation

## Overview

The **AI Bypass** node (`mbAIBypass`) is designed to modify images to help them pass FFT-based AI detection systems. It adds natural artifacts, noise patterns, and frequency domain modifications that make AI-generated images appear more like natural photographs.

## How It Works

AI detection systems that use FFT (Fast Fourier Transform) analysis typically look for:
- Missing high-frequency noise that natural images contain
- Overly smooth gradients and perfect edges
- Unnatural frequency distribution patterns
- Lack of sensor noise and compression artifacts

This node counters these detection methods by:

### 1. **High Frequency Enhancement**
- Uses FFT to boost high-frequency components
- Adds the subtle noise that natural cameras and sensors introduce
- Maintains natural frequency distribution patterns

### 2. **Realistic Noise Addition**
- **Sensor Noise**: Simulates camera sensor shot noise and read noise
- **Film Grain**: Multi-scale film grain patterns with fine and coarse grain layers
- **Gaussian**: Simple random noise with natural distribution  
- **Perlin**: Multi-octave organic noise patterns that look more natural
- **Mixed**: Combination of multiple noise types for best results

### 3. **Texture Enhancement**
- Detects overly smooth regions in the image
- Adds micro-textures that break up AI-like smoothness
- Preserves important image details while adding natural imperfections

### 4. **Edge Imperfections**
- Adds subtle imperfections to edges that are too "perfect"
- Simulates natural optical effects and lens characteristics
- Makes lines and curves appear more organic

### 5. **Compression Artifacts**
- Simulates realistic JPEG compression artifacts
- Adds the subtle blocking and quantization that real photos have
- Maintains visual quality while adding detection-fooling patterns

### 6. **Chromatic Aberration**
- Adds subtle color fringing effects
- Simulates lens imperfections that real cameras have
- Creates natural optical characteristics

## Parameters

### Required Parameters

- **Image**: Input image tensor to process
- **Bypass Mode**: 
  - `subtle`: Light modifications, barely perceptible
  - `moderate`: Balanced approach (recommended)
  - `aggressive`: Strong modifications, may affect quality
  - `custom`: Uses your exact parameter settings
- **Noise Type**: Type of noise pattern to add (sensor, film_grain, gaussian, perlin, mixed)
- **High Freq Boost**: Strength of high-frequency enhancement (0.0-1.0)
- **Texture Enhancement**: Amount of micro-texture to add (0.0-1.0)
- **Edge Imperfection**: Level of edge imperfections (0.0-1.0)
- **Compression Artifacts**: Amount of compression simulation (0.0-1.0)

### Optional Parameters

- **Preserve Quality**: Prioritizes visual quality while applying modifications
- **Adaptive Processing**: Adapts processing strength based on image content
- **Seed**: Random seed for reproducible results

## Usage Tips

1. **Start with "moderate" mode** for most use cases
2. **Use "mixed" noise type** for best detection bypass results
3. **Enable "Preserve Quality"** to maintain visual appearance
4. **Enable "Adaptive Processing"** for content-aware modifications
5. **Use consistent seeds** for reproducible results across batches

## Output

- **Image**: The modified image with bypass processing applied
- **Processing Info**: Text description of what modifications were applied

## Technical Notes

- The node uses frequency domain analysis to target specific patterns
- Processing is designed to be imperceptible to human viewers
- Multiple techniques are combined for comprehensive bypass coverage
- All modifications are based on real-world photography artifacts

## Best Practices

- Test different bypass modes to find the right balance for your use case
- Combine with other image processing nodes for additional naturalization
- Use batch processing with consistent seeds for uniform results
- Monitor the processing info to understand what modifications were applied

## Limitations

- May slightly reduce image quality at aggressive settings
- Processing time increases with image size and complexity
- Results may vary depending on the specific AI detection system
- Some compression artifacts may be visible at very high settings
