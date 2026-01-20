<script>
	
	import { getContext, getAllContexts } from "svelte";
  
  let { xAccessor, hoverFill = "#CCC", hoverOpacity = 1, hoverStroke = "none", hoverStrokeWidth = 1 } = $props()
  
  const { data, x, y } = getContext("data")
  let index = $state(-1)

  const xScale = $derived(x())
  const yScale = $derived(y())
  const colData = $derived(data())
  
  const { setIndex } = getContext("tooltip")

  const probConext = getContext("probHover")
 
  const colGenerator = $derived.by(() => {
    return function(data) {
      const colCentroids = data.map(d => xScale(xAccessor(d)))
      const colHeight = yScale.range()[0] 
      const colBase = 0
      const cols = Array(colCentroids.length)
      let currentColWidth
      let currentColStart
      for (let i = 0; i < colCentroids.length; i++) {
        if (i === 0) {
          currentColWidth = (colCentroids[i + 1] - colCentroids[i])
        } else {
          currentColWidth = (colCentroids[i] - colCentroids[i - 1])
        }
        currentColStart = colCentroids[i] - currentColWidth / 2
        cols[i] = {
          id: i,
          x: currentColStart, 
          y: colBase, 
          width: currentColWidth, 
          height: colHeight,
          hovered: false
        }
      }
      return(cols)
    }
  })


  const columns = $derived(colGenerator(colData))

  let hoveredCol = $state(-1)
  let mouseX = $state()
  let mouseY = $state()

  function handleMouseOver(e, i) {
    hoveredCol = i 
    mouseX = e.clientX
    mouseY = e.clientY
    setIndex(hoveredCol)
    if (probConext) {
      probConext.setIndex(hoveredCol)
    }
  }

  function handleMouseLeave(e) {
    hoveredCol = -1
    setIndex(hoveredCol)
    if (probConext) {
      probConext.setIndex(hoveredCol)
    }
  }

</script>

<g>
 {#each columns as column, i (column.id)} 
    <rect 
      key={i} 
      x={column.x} 
      y={column.y} 
      width={column.width} 
      height={column.height}
      fill={hoverFill}
      fill-opacity={i === hoveredCol ? hoverOpacity : 0} 
      stroke={hoverStroke}
      stroke-opacity={i === hoveredCol ? hoverOpacity : 0}
      stroke-width={hoverStrokeWidth}
      onmouseover={(e) => handleMouseOver(e, i)}
      onmouseleave={handleMouseLeave}
 />
  {/each}
</g>
