<script>
	
  import { getContext } from "svelte";
  import { scaleOrdinal, interpolateViridis } from "d3";
  
  let { 
    xAccessor, 
    yAccessor, 
    fillAccessor, 
    strokeAccessor = d => "black", 
    radiusAccessor = d => 5, 
    radiusScale = "none",
    width = 2,
    fillPalette = "auto",
    strokePalette = "black"
  } = $props()
  
  const { data, x, y } = getContext("data")

  const xScale = $derived(x())
  const yScale = $derived(y())
  const scatterData = $derived(data().map((d, i) => ({...d, id: i})))

  const scaleRadius = $derived.by(() => {
    let scaleRadius = d => d
    if (data()) {
      if (radiusScale === "x") {
        scaleRadius = (d) => xScale(d) - xScale(0)
      } else if (radiusScale === "y") {
        scaleRadius = (d) => yScale(0) - yScale(d)
      }
    }
    return scaleRadius
  })

  let fillClasses = $derived([...new Set(scatterData.map(d => fillAccessor(d)))].sort())
  let strokeClasses = $derived([...new Set(scatterData.map(d => strokeAccessor(d)))].sort())

  let fillRange = $derived.by(() => {
    let fillRange
    if (typeof(fillPalette) === "string") {
      if (fillPalette === "auto") {
        fillRange = Array(fillClasses.length)
          .fill(0)
          .map((d, i) => i / (fillClasses.length - 1))
          .map(d => interpolateViridis(d))
      } else {
        fillRange = [fillPalette, fillPalette]
      }
    } else {
      fillRange = fillPalette
    }
    return fillRange
  })

  let strokeRange = $derived.by(() => {
    let strokeRange
    if (typeof(strokePalette) === "string") {
      if (strokePalette === "auto") {
        strokeRange = Array(strokeClasses.length)
          .fill(0)
          .map((d, i) => i / (strokeClasses.length - 1))
          .map(d => interpolateViridis(d))
      } else {
        strokeRange = [strokePalette, strokePalette]
      }
    } else {
      strokeRange = strokePalette
    }
    return strokeRange
  })

  let fillScale = $derived(scaleOrdinal().domain(fillClasses).range(fillRange))
  let strokeScale = $derived(scaleOrdinal().domain(strokeClasses).range(strokeRange))
  
</script>

<g>
  {#each scatterData as scatterCirlce (scatterCirlce.id)}
    <circle 
      transition="r 2s"
      cx={xScale(xAccessor(scatterCirlce))} 
      cy={yScale(yAccessor(scatterCirlce))} 
      r={scaleRadius(radiusAccessor(scatterCirlce))} 
      fill={typeof fillAccessor === "function" ? fillScale(fillAccessor(scatterCirlce)) : fillAccessor}
      stroke={strokeScale(strokeAccessor(scatterCirlce))}
      stroke-width="{width}"
    />    
  {/each}
</g>
