import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

function GraphView({ data }) {
  const svgRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  
  useEffect(() => {
    if (!data || !data.nodes || data.nodes.length === 0) return;
    
    // Ensure links array exists
    const links = data.links || [];
    const nodes = data.nodes || [];
    
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    
    const width = svgRef.current.clientWidth;
    const height = 600;
    
    // Create container group for zoom
    const g = svg.append('g');
    
    // Zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.3, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });
    
    svg.call(zoom);
    
    // Create simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));
    
    // Draw links
    const link = g.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#64748b')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', d => Math.sqrt(d.weight || 1));
    
    // Draw nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', d => 8 + (d.degree || 0) * 0.5)
      .attr('fill', d => getNodeColor(d))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .call(drag(simulation))
      .on('click', (event, d) => {
        setSelectedNode(d);
      });
    
    // Add labels
    const label = g.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .text(d => d.label || d.id.substring(0, 8))
      .attr('font-size', 10)
      .attr('fill', '#e2e8f0')
      .attr('text-anchor', 'middle')
      .attr('dy', -15);
    
    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      
      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
      
      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });
    
    return () => {
      simulation.stop();
    };
  }, [data]);
  
  const getNodeColor = (node) => {
    if (node.in_fraud_ring) return '#ef4444'; // red
    if (node.is_flagged) return '#f59e0b'; // amber
    if (node.type === 'user') return '#3b82f6'; // blue
    if (node.type === 'merchant') return '#10b981'; // green
    if (node.type === 'device') return '#8b5cf6'; // purple
    if (node.type === 'ip') return '#ec4899'; // pink
    return '#6b7280'; // gray
  };
  
  const drag = (simulation) => {
    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }
    
    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }
    
    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }
    
    return d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended);
  };
  
  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">Entity Relationship Graph</h2>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-blue-200">User</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-blue-200">Merchant</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-purple-500"></div>
            <span className="text-blue-200">Device</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-blue-200">Fraud Ring</span>
          </div>
        </div>
      </div>
      
      <div className="bg-slate-900/50 rounded-lg overflow-hidden">
        <svg 
          ref={svgRef} 
          width="100%" 
          height="600"
          className="w-full"
        />
      </div>
      
      {selectedNode && (
        <div className="mt-4 bg-slate-800/80 backdrop-blur-sm rounded-lg p-4 border border-blue-500/30">
          <h3 className="text-white font-bold mb-2">Node Details</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="text-blue-200">ID:</div>
            <div className="text-white">{selectedNode.id}</div>
            <div className="text-blue-200">Type:</div>
            <div className="text-white">{selectedNode.type}</div>
            <div className="text-blue-200">Degree:</div>
            <div className="text-white">{selectedNode.degree || 0}</div>
            {selectedNode.is_flagged && (
              <>
                <div className="text-blue-200">Status:</div>
                <div className="text-red-400 font-bold">FLAGGED</div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default GraphView;
