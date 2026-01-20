<script>
	
  import { curveMonotoneX, area, ribbon } from "d3";
	import { getContext } from "svelte";
  
  let { xAccessor, y0Accessor, y1Accessor, fillColour = "steelblue" } = $props()
  
  const { data, x, y } = getContext("data")

  const xScale = $derived(x())
  const yScale = $derived(y())
  const ribbonData = $derived(data())

  const areaGenerator = $derived(area()
    .curve(curveMonotoneX)
    .x(d => xScale(xAccessor(d)))
    .y0(d => yScale(y0Accessor(d)))
    .y1(d => yScale(y1Accessor(d)))
  )

</script>

<g fill={fillColour}>
  <path d="{areaGenerator(ribbonData)}" />
</g>
