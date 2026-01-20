<script>
	
  import { line } from "d3";
	import { getContext } from "svelte";
  
  let { colour = "black", numTicks = 10, labels = true, labelSize="0.75em", yOffset = 0} = $props()
  
  const { x, y } = getContext("data")

  const xScale = $derived(x())
  const yScale = $derived(y())

  let axisY = $derived(yScale.range()[0] + yOffset)
  let axisLine = $derived(xScale.range().map(d => ({x: d, y: axisY})))
  let lineGenerator = $derived(line().x(d => d.x).y(d => d.y))
  
  let ticks = $derived(xScale.ticks(numTicks))
  let tickLines = $derived(ticks.map(d => [{x: xScale(d), y: axisY}, {x: xScale(d), y: axisY + 5}]))

  let tickLabels = $derived(ticks.map(
    (d, i) => ({label: xScale.tickFormat()(d), x: tickLines[i][0].x, y: tickLines[i][1].y + 2})
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
        alignment-baseline="hanging"
        font-size="{labelSize}"
      >
        {tickLabel.label} 
      </text>
    {/each}    
  {/if}
</g>

<style>
  .axis-text {
    text-anchor: middle;
    font-size: "0.5em";
  }
</style>
