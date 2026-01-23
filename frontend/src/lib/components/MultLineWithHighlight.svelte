<script>
	
  import { curveMonotoneX, hierarchy, line } from "d3";
	import { getContext } from "svelte";
  
  let { xAccessor, yAccessors, colour = "black", highlightColour = "steelblue", noHighlightColour = "#555", width = 1} = $props()

  let lineColors = $derived(Array(yAccessors.length).fill(colour))
  let highLightLine = $state("")
  let strokeWidth = $state(Array(yAccessors.length).fill(width))
  
  const { data, x, y } = getContext("data")

  const xScale = $derived(x())
  const yScale = $derived(y())
  const spaghettiData = $derived(data())

  const lineGenerators = $derived(yAccessors.map(
    (yAccessor, i) => ({
      id: i, 
      fun: line()
        .curve(curveMonotoneX)
        .x(d => xScale(xAccessor(d)))
        .y(d => yScale(yAccessor.fun(d)))
    })
  ))

  let ticks = $derived(yScale.ticks())

  let hoverTimeout

  function handleMouseOver(event, index) {
    clearTimeout(hoverTimeout)
    lineColors.forEach((d, i) => i === index ? lineColors[i] = highlightColour : lineColors[i] = noHighlightColour)
    strokeWidth.forEach((d, i) => i === index ? strokeWidth[i] = width * 2 : strokeWidth[i] = width)
    highLightLine = "#" + yAccessors[index].key
  }

  function handleMouseLeave(event) {
    hoverTimeout = setTimeout(() => {
      lineColors.forEach((d, i) => lineColors[i] = colour)
      strokeWidth.forEach((d, i) => strokeWidth[i] = width)
      highLightLine = ""
    }, 500)
  }

</script>

<g>
  <rect 
    onmouseleave={handleMouseLeave} 
    onblur={handleMouseLeave} 
    role="button"
    tabindex="0"
    stroke="none" 
    fill="yellow" 
    fill-opacity=0
    x={xScale.range()[0] - 20} 
    width={xScale.range()[1] + 20}
    y={yScale.range()[1] - 20}
    height={yScale.range()[0] + 30} 
  />
  {#each lineGenerators as lineGenerator, i (lineGenerator.id)}
    <path 
      role="button"
      aria-label="{yAccessors[i].key}"
      tabindex="0"
      d="{lineGenerator.fun(spaghettiData)}" 
      id={yAccessors[i].key}
      stroke={lineColors[i]}
      fill="none"
      stroke-width={strokeWidth[i]}
      stroke-linecap="round"
      onmouseover={(event) => handleMouseOver(event, i)}
      onfocus={(event) => handleMouseOver(event, i)}
    />  
  {/each}
</g>
<use xlink:href="{highLightLine}" />
