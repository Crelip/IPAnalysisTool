# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['IPAnalysisTool/IPAnalysisTool.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='IPAnalysisTool',
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
