<script>

  import { getContext, getAllContexts } from "svelte";
  import Rect from "./Rect.svelte";
  import Data from "./Data.svelte";

  let { xAccessor, y0Accessor, y1Accessor, fillPalette = "steelblue", colour = "black", colWidth = 0.9, children} = $props()

  const { getProbs } = getContext("probs")

  
  const probData = $derived(
    getProbs() 
    ? getProbs().map(d => 
        ({
          ...d, 
          fill: typeof fillPalette === "function" ? fillPalette(d.prob) : fillPalette
        })
    )
    : []
  )
  
</script>

{#if probData.length > 0}
  <Data data={probData} {xAccessor} yAccessor = {d => [0, 1]} xScale="utc" yFixedLower={true}>
    <Rect {xAccessor} {y0Accessor} {y1Accessor} fillColour = {d => d.fill} colour = "none" {colWidth} />
    {@render children?.()}
  </Data>  
{/if}
