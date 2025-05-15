# -*- mode: python ; coding: utf-8 -*-

import os, sys

conda_prefix = os.environ.get('CONDA_PREFIX', sys.prefix)
libdir = os.path.join(conda_prefix, 'lib')

binaries = []
for fname in ('libssl.so.3', 'libcrypto.so.3'):
    p = os.path.join(libdir, fname)
    if os.path.exists(p):
        binaries.append((p, '.'))

from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('mpl_toolkits')

a = Analysis(
    ['ip_analysis_tool/ip_analysis_tool.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'graph_tool.centrality.libgraph_tool_centrality',
        'graph_tool.clustering.libgraph_tool_clustering',
        'graph_tool.correlations.libgraph_tool_correlations',
        'graph_tool.draw.libgraph_tool_draw',
        'graph_tool.draw.libgraph_tool_layout',
        'graph_tool.dynamics.libgraph_tool_dynamics',
        'graph_tool.flow.libgraph_tool_flow',
        'graph_tool.generation.libgraph_tool_generation',
        'graph_tool.search.libgraph_tool_search',
        'graph_tool.spectral.libgraph_tool_spectral',
        'graph_tool.stats.libgraph_tool_stats',
        'graph_tool.topology.libgraph_tool_topology',
        'graph_tool.util.libgraph_tool_util',
        'scipy._lib.array_api_compat.numpy.fft',
        'scipy.special._special_ufuncs',
        'ip_analysis_tool.caching.graph_cache',
        'ip_analysis_tool.time_series_analysis',
        'ip_analysis_tool.h_backbone',
        'ip_analysis_tool.k_core'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ip_analysis_tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
