<script>
	
  import { line } from "d3";
	import { getContext } from "svelte";
  
  let { colour = "black", numTicks = 5, labels = true, labelSize="0.75em", xOffset = -8} = $props()
  
  const { x, y } = getContext("data")

  const xScale = $derived(x())
  const yScale = $derived(y())

  let axisX = $derived(xScale.range()[0] + xOffset)
  let axisLine = $derived(yScale.range().map(d => ({x: axisX, y: d})))
  let lineGenerator = $derived(line().x(d => d.x).y(d => d.y))
  
  let ticks = $derived(yScale.ticks(numTicks))
  let tickLines = $derived(ticks.map(d => [{y: yScale(d), x: axisX}, {y: yScale(d), x: axisX - 5}]))

  let tickLabels = $derived(ticks.map(
    (d, i) => ({label: yScale.tickFormat()(d), x: tickLines[i][1].x - 2, y: tickLines[i][0].y})
  ))
  
</script>

<g>
  <path d={lineGenerator(axisLine)} stroke={colour} />
  {#each tickLines as tickLine}
    <path d={lineGenerator(tickLine)} stroke={colour} />
  {/each}
  {#if labels}
    {#each tickLabels as tickLabel}
      <text 
        x={tickLabel.x} 
        y={tickLabel.y} 
        class="axis-text" 
        fill={colour} 
        font-size="{labelSize}"
        alignment-baseline="middle"
      >
        {tickLabel.label} 
      </text>
    {/each}    
  {/if}
</g>

<style>
  .axis-text {
    text-anchor: end;
  }
</style>
