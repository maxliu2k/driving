"""
Load the models

MODELS:
1. Object finder (finds traffic lights, stop signs, etc.)
2. Traffic light classifier (classifies traffic lights)
3. *Sign classifier (classifies signs)

Analyze the road

1. Find objects with at least 25% confidence
2. Classify traffic lights

If a traffic light is red, stop. If it is green, go. If it is yellow, slow down. Assume the current lane is the one closest to the center of the image.
Say what you should do through a speaker.
"""