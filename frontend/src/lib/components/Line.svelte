<script>
	
  import { curveMonotoneX, line } from "d3";
	import { getContext } from "svelte";
  
  let { xAccessor, yAccessor, colour = "black", width = 1} = $props()
  
  const { data, x, y } = getContext("data")

  const xScale = $derived(x())
  const yScale = $derived(y())
  const lineData = $derived(data())

  const lineGenerator = $derived(line()
    .curve(curveMonotoneX)
    .x(d => xScale(xAccessor(d)))
    .y(d => yScale(yAccessor(d)))
  )

</script>

<g fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="round">
  <path d="{lineGenerator(lineData)}" />
</g>
