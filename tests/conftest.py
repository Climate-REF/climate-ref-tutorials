"""Shared fixtures"""
import matplotlib

# The plotting helpers use pyplot.
# Force a non-interactive backend so the figure-producing tests run headless
matplotlib.use("Agg")
