<script>
	import Overlay from "./Overlay.svelte";
  import { getContext } from "svelte";
  import { fade } from "svelte/transition"
	import ScatterCircle from "./ScatterCircle.svelte";
  import Svg from "./Svg.svelte";
  import Data from "./Data.svelte";
  import Xaxis from "./Xaxis.svelte";
  import { interpolateWarm } from "d3";

  let { data, children, tooltipWidth = 200, background="#AAA", textColour="#222", opacity=1, border="#222"} = $props()

  let { getMousePos, getIndex } = $derived(getContext("tooltip"))
  let x = $derived(getMousePos().x)
  let y = $derived(getMousePos().y)
  let i = $derived(getIndex())
  const xExtent = $derived(
    [Math.min(...data.flat().map(d => d.x)), Math.max(...data.flat().map(d => d.x))]
  ) 
  const yExtent = $derived(
    [Math.min(...data.flat().map(d => d.y)), Math.max(...data.flat().map(d => d.y))]
  )
  const xDomain = $derived.by(() => {
    const xLength = xExtent[1] - xExtent[0]
    const yLength = yExtent[1] - yExtent[0]
    if (xLength > yLength) {
      return [xExtent[0], yExtent[1]]
    }
    const xMiddle = xExtent[0] + (xExtent[1] - xExtent[0]) / 2
    return [xMiddle - yLength / 2, xMiddle + yLength / 2]
  })
  
  const yDomain = $derived.by(() => {
    const xLength = xExtent[1] - xExtent[0]
    const yLength = yExtent[1] - yExtent[0]
    if (yLength > xLength) {
      return [0, yExtent[1] + yExtent[0]]
    }
    const yMiddle = yExtent[0] + (yExtent[1] - yExtent[0]) / 2
    return [0, xLength + yExtent[0]]
  })
  
  let intializationData = $derived([
    {x: Math.min(...data.flat().map(d => d.x)) - 0.5, y: 0}, 
    {x: Math.max(...data.flat().map(d => d.x)) + 0.5, y: Math.max(...data.flat().map(d => d.y)) + 0.5}
  ])
  let tooltipData = $derived(data[i])
  let windowWidth = $state(0)
  const tooltipLeft = $derived(windowWidth - x < tooltipWidth + 10)
  const leftPos = $derived(tooltipLeft ? (x - tooltipWidth - 5) + "px" : (x + 5) + "px") 

  let circlePalette = $derived(tooltipData 
    ? Array(tooltipData.length).fill(0).map((d, i) => interpolateWarm(i / (tooltipData.length - 1)))
    : "blue"
  )

</script>

<svelte:window bind:innerWidth={windowWidth} />

{#if i && i >= 0}
  <Overlay>
    <div 
      class="tooltip" 
      transition:fade={{ duration: 100 }} 
      style="top: {y + 5}px; left: {leftPos}; width: {tooltipWidth}px; background-color: {background}; opacity: {opacity}; border-color:{border}">
      <!-- <h3>Ensemble</h3> -->
      <div class="tooltip-content">
        <Svg h={tooltipWidth} w={tooltipWidth * 0.9} marginLeft=10 marginRight=10 marginTop=10>
          <Data 
            data={tooltipData} 
            xAccessor={d => xExtent} 
            yAccessor={d => yDomain} <!--[0, 10]} <!--yExtent[0] + yExtent[1]]}-->
            yFixedLower={true}
          >
            <ScatterCircle xAccessor={d => d.x} yAccessor={d => d.y} fillAccessor = {d => d.member} radiusAccessor={d => d.radius} radiusScale="x" width=1 fillPalette={circlePalette}/>
            <Xaxis colour={textColour}/>
          </Data>
        </Svg>
      </div>
      {@render children?.()}
    </div>
  </Overlay>
{/if}

<style>
  
  .tooltip {
    border-radius: 15px;
    border-width: 2px;
    border-style: solid;
    position: fixed;
  }

  .tooltip-content {
    display: flex;
    justify-content: center;
  }

  h3 {
    color: #CCC;
    display: flex;
    align-items: center;
    text-align: center;
    display: flex;
    justify-content: center;
  }
</style>