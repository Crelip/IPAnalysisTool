import graph_tool.all as gt

def baseVisualize(g: gt.Graph, name: str):
    gt.graph_draw(g,
            gt.sfdp_layout(g),
            output_size=(10000,10000),
            vertex_text=g.vp.ip,
            vertex_font_size=8,
            vertex_size=6,
            edge_pen_width=2.0,
            bg_color=[1,1,1,1],
            output=f"scratchpad/{name}.png"
                  )