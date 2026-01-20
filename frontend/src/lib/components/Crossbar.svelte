<script>

  import { getContext } from "svelte";
  
  let { xAccessor, yAccessor, colour = "black", barWidth = 0.9, strokeWidth = 2} = $props()
  
  const { data, x, y } = getContext("data")

  const xScale = $derived(x())
  const yScale = $derived(y())
  const barData = $derived(data())

  const barGenerator = $derived.by(() => {
    return function(data) {
      const barCentroids = data.map(d => xScale(xAccessor(d)))
      const barY = data.map(d => yScale(yAccessor(d))) 
      const bars = Array(barCentroids.length)
      let currentBarWidth
      let currentBarStart
      for (let i = 0; i < barCentroids.length; i++) {
        if (i === 0) {
          currentBarWidth = (barCentroids[i + 1] - barCentroids[i]) * barWidth
        } else {
          currentBarWidth = (barCentroids[i] - barCentroids[i - 1]) * barWidth
        }
        currentBarStart = barCentroids[i] - currentBarWidth / 2
        bars[i] = {
          id: i,
          x1: currentBarStart,
          x2: currentBarStart + currentBarWidth,
          y1: barY[i],
          y2: barY[i] ,
          ...barData[i] 
        }
      }
      return(bars)
    }
  })

  const bars = $derived(barGenerator(barData))

</script>

<g>
  {#each bars as bar}
    <line x1={bar.x1} x2={bar.x2} y1={bar.y1} y2={bar.y2} stroke={colour} stroke-width={strokeWidth} />
  {/each}
</g>