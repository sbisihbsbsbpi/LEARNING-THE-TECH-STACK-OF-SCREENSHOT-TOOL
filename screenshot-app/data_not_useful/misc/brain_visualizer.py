#!/usr/bin/env python3
"""
Project Brain Visualizer - Interactive dependency graph visualization
Generates an interactive HTML dashboard showing project structure
"""

import json
from pathlib import Path
from project_brain import ProjectBrain


def generate_html_dashboard(brain: ProjectBrain, output_file: str = "project_brain_dashboard.html"):
    """Generate interactive HTML dashboard with D3.js visualization"""
    
    # Prepare graph data for D3.js
    nodes = []
    links = []
    
    # Create nodes
    for rel_path, info in brain.index.items():
        nodes.append({
            "id": rel_path,
            "name": info['name'],
            "category": info['category'],
            "purpose": info['purpose'],
            "size": info['size'],
            "type": info['type'],
        })
    
    # Create links from dependencies
    for file_path, deps in brain.dependencies.items():
        for dep in deps:
            dep_file = brain._resolve_dependency(dep)
            if dep_file and dep_file in brain.index:
                links.append({
                    "source": file_path,
                    "target": dep_file,
                    "type": "imports"
                })
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Project Brain Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            overflow: hidden;
        }}
        
        .container {{
            display: flex;
            height: 100vh;
        }}
        
        .sidebar {{
            width: 300px;
            background: white;
            padding: 20px;
            overflow-y: auto;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        }}
        
        .main {{
            flex: 1;
            position: relative;
        }}
        
        h1 {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #667eea;
        }}
        
        .stats {{
            background: #f7fafc;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .stat-item {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            font-size: 14px;
        }}
        
        .stat-label {{
            color: #718096;
        }}
        
        .stat-value {{
            font-weight: 600;
            color: #2d3748;
        }}
        
        .category-filter {{
            margin: 20px 0;
        }}
        
        .category-btn {{
            display: block;
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            text-align: left;
            transition: all 0.2s;
        }}
        
        .category-btn:hover {{
            transform: translateX(5px);
        }}
        
        .category-btn.production {{
            background: #48bb78;
            color: white;
        }}
        
        .category-btn.config {{
            background: #4299e1;
            color: white;
        }}
        
        .category-btn.test {{
            background: #ed8936;
            color: white;
        }}
        
        .category-btn.docs {{
            background: #9f7aea;
            color: white;
        }}
        
        .category-btn.archived {{
            background: #a0aec0;
            color: white;
        }}
        
        .category-btn.runtime {{
            background: #f56565;
            color: white;
        }}
        
        #graph {{
            width: 100%;
            height: 100%;
        }}
        
        .node {{
            cursor: pointer;
            stroke: white;
            stroke-width: 2px;
        }}
        
        .node:hover {{
            stroke-width: 4px;
        }}
        
        .link {{
            stroke: #999;
            stroke-opacity: 0.3;
            stroke-width: 1px;
        }}
        
        .node-label {{
            font-size: 10px;
            pointer-events: none;
            fill: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        }}
        
        .tooltip {{
            position: absolute;
            background: white;
            padding: 12px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            max-width: 300px;
            z-index: 1000;
        }}
        
        .tooltip.show {{
            opacity: 1;
        }}
        
        .tooltip-title {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #2d3748;
        }}
        
        .tooltip-info {{
            font-size: 12px;
            color: #718096;
            margin: 4px 0;
        }}
        
        .controls {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .control-btn {{
            display: block;
            width: 100%;
            padding: 8px 16px;
            margin: 5px 0;
            border: none;
            border-radius: 6px;
            background: #667eea;
            color: white;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }}
        
        .control-btn:hover {{
            background: #5568d3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h1>🧠 Project Brain</h1>
            
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-label">Total Files</span>
                    <span class="stat-value">{len(brain.index)}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Dependencies</span>
                    <span class="stat-value">{len(brain.dependencies)}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Production Files</span>
                    <span class="stat-value">{len([f for f in brain.index.values() if f['category'] == 'production'])}</span>
                </div>
            </div>
            
            <div class="category-filter">
                <h3 style="margin-bottom: 10px; font-size: 16px;">Filter by Category</h3>
                <button class="category-btn production" onclick="filterCategory('production')">
                    ✅ Production ({len([f for f in brain.index.values() if f['category'] == 'production'])})
                </button>
                <button class="category-btn config" onclick="filterCategory('config')">
                    ⚙️ Config ({len([f for f in brain.index.values() if f['category'] == 'config'])})
                </button>
                <button class="category-btn test" onclick="filterCategory('test')">
                    🧪 Test ({len([f for f in brain.index.values() if f['category'] == 'test'])})
                </button>
                <button class="category-btn docs" onclick="filterCategory('docs')">
                    📄 Docs ({len([f for f in brain.index.values() if f['category'] == 'docs'])})
                </button>
                <button class="category-btn archived" onclick="filterCategory('archived')">
                    📦 Archived ({len([f for f in brain.index.values() if f['category'] == 'archived'])})
                </button>
                <button class="category-btn runtime" onclick="filterCategory('runtime')">
                    🔄 Runtime ({len([f for f in brain.index.values() if f['category'] == 'runtime'])})
                </button>
                <button class="category-btn" style="background: #2d3748;" onclick="filterCategory(null)">
                    🔍 Show All
                </button>
            </div>
        </div>
        
        <div class="main">
            <div class="controls">
                <button class="control-btn" onclick="resetZoom()">🔍 Reset Zoom</button>
                <button class="control-btn" onclick="toggleLabels()">🏷️ Toggle Labels</button>
            </div>
            <svg id="graph"></svg>
            <div class="tooltip" id="tooltip"></div>
        </div>
    </div>
    
    <script>
        const graphData = {{
            nodes: {json.dumps(nodes)},
            links: {json.dumps(links)}
        }};
        
        // Color mapping for categories
        const categoryColors = {{
            production: '#48bb78',
            config: '#4299e1',
            test: '#ed8936',
            docs: '#9f7aea',
            archived: '#a0aec0',
            runtime: '#f56565',
            unknown: '#718096'
        }};
        
        // Setup SVG
        const width = window.innerWidth - 300;
        const height = window.innerHeight;
        
        const svg = d3.select('#graph')
            .attr('width', width)
            .attr('height', height);
        
        const g = svg.append('g');
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on('zoom', (event) => {{
                g.attr('transform', event.transform);
            }});
        
        svg.call(zoom);
        
        // Create force simulation
        const simulation = d3.forceSimulation(graphData.nodes)
            .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(30));
        
        // Create links
        const link = g.append('g')
            .selectAll('line')
            .data(graphData.links)
            .join('line')
            .attr('class', 'link');
        
        // Create nodes
        const node = g.append('g')
            .selectAll('circle')
            .data(graphData.nodes)
            .join('circle')
            .attr('class', 'node')
            .attr('r', d => Math.min(Math.max(d.size / 5000, 5), 20))
            .attr('fill', d => categoryColors[d.category] || categoryColors.unknown)
            .call(drag(simulation))
            .on('mouseover', showTooltip)
            .on('mouseout', hideTooltip);
        
        // Create labels
        const labels = g.append('g')
            .selectAll('text')
            .data(graphData.nodes)
            .join('text')
            .attr('class', 'node-label')
            .text(d => d.name)
            .attr('text-anchor', 'middle')
            .attr('dy', 25);
        
        // Update positions on tick
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
            
            labels
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }});
        
        // Drag behavior
        function drag(simulation) {{
            function dragstarted(event) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }}
            
            function dragged(event) {{
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }}
            
            function dragended(event) {{
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }}
            
            return d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended);
        }}
        
        // Tooltip functions
        function showTooltip(event, d) {{
            const tooltip = document.getElementById('tooltip');
            tooltip.innerHTML = `
                <div class="tooltip-title">${{d.name}}</div>
                <div class="tooltip-info"><strong>Category:</strong> ${{d.category}}</div>
                <div class="tooltip-info"><strong>Purpose:</strong> ${{d.purpose}}</div>
                <div class="tooltip-info"><strong>Size:</strong> ${{(d.size / 1024).toFixed(1)}} KB</div>
            `;
            tooltip.style.left = event.pageX + 10 + 'px';
            tooltip.style.top = event.pageY + 10 + 'px';
            tooltip.classList.add('show');
        }}
        
        function hideTooltip() {{
            document.getElementById('tooltip').classList.remove('show');
        }}
        
        // Filter by category
        function filterCategory(category) {{
            if (category) {{
                node.style('opacity', d => d.category === category ? 1 : 0.1);
                labels.style('opacity', d => d.category === category ? 1 : 0.1);
                link.style('opacity', 0.05);
            }} else {{
                node.style('opacity', 1);
                labels.style('opacity', 1);
                link.style('opacity', 0.3);
            }}
        }}
        
        // Reset zoom
        function resetZoom() {{
            svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
        }}
        
        // Toggle labels
        let labelsVisible = true;
        function toggleLabels() {{
            labelsVisible = !labelsVisible;
            labels.style('opacity', labelsVisible ? 1 : 0);
        }}
    </script>
</body>
</html>"""
    
    # Save HTML file
    output_path = brain.root / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard generated: {output_file}")
    print(f"📂 Open in browser: file://{output_path}")
    
    return str(output_path)


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "/Users/tlreddy/Documents/project 1/screenshot-app"
    
    print("🧠 Generating Project Brain Dashboard...")
    brain = ProjectBrain(project_path)
    
    # Load existing index
    index_file = brain.root / "project_index.json"
    if index_file.exists():
        print("📖 Loading existing index...")
        import json
        with open(index_file) as f:
            data = json.load(f)
            brain.index = data['index']
            brain.dependencies = {k: set(v) for k, v in data['dependencies'].items()}
        print(f"✅ Loaded {len(brain.index)} files")
    else:
        print("🔍 Scanning project...")
        brain.scan_project()
        brain.save_index()
    
    # Generate dashboard
    output_path = generate_html_dashboard(brain)
    
    # Try to open in browser
    try:
        import webbrowser
        webbrowser.open(f'file://{output_path}')
        print("🌐 Opening in browser...")
    except Exception:
        print("ℹ️  Please open the file manually in your browser")


if __name__ == "__main__":
    main()

