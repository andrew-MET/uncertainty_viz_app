<script>
	
	import { getContext } from "svelte";
  
  let { xAccessor, y0Accessor, y1Accessor, fillColour = "steelblue", colour = "black", colWidth = 0.9} = $props()
  
  const { data, x, y } = getContext("data")

  const xScale = $derived(x())
  const yScale = $derived(y())
  const colData = $derived(data())

  const colGenerator = $derived.by(() => {
    return function(data) {
      const colCentroids = data.map(d => xScale(xAccessor(d)))
      const colHeights = data.map(d => yScale(y1Accessor(d))) 
      const colBase = data.map(d => yScale(y0Accessor(d)))
      const cols = Array(colCentroids.length)
      let currentColWidth
      let currentColStart
      for (let i = 0; i < colCentroids.length; i++) {
        if (i === 0) {
          currentColWidth = (colCentroids[i + 1] - colCentroids[i]) * colWidth
        } else {
          currentColWidth = (colCentroids[i] - colCentroids[i - 1]) * colWidth
        }
        currentColStart = colCentroids[i] - currentColWidth / 2
        cols[i] = {
          id: i,
          x: currentColStart, 
          y: colHeights[i], 
          width: currentColWidth, 
          height: colBase[i] - colHeights[i] > 0 ? colBase[i] - colHeights[i] : 0,
          ...colData[i] 
        }
      }
      return(cols)
    }
  })


  const columns = $derived(colGenerator(colData))

</script>

<g stroke={colour}>
 {#each columns as column, i (column.id)} 
    <rect 
      key={i} 
      x={column.x} 
      y={column.y} 
      width={column.width} 
      height={column.height}
      fill={typeof fillColour === "function" ? fillColour(column) : fillColour} 
    />
  {/each}
</g>
