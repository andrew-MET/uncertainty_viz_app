<script>

  import { setContext } from "svelte";
  
  let { 
    w="100%", 
    h=300,
    minW=0,
    marginTop=10,
    marginRight=10,
    marginBottom=30,
    marginLeft=30, 
    children 
  } = $props()
  
  let svgWidth = $state(0)
  let boundedWidth = $derived(Math.max(...[minW, svgWidth - marginLeft - marginRight])) 

  // Use context API to make getters for boundedWidth and boundedHeight scoped to any 
  // children of an instance of this component.
  setContext("svgDims", {
  	w() { return  boundedWidth },
		h() { return h - marginTop - marginBottom }
	})

  const transX = marginLeft + "px"
  const transY = marginTop + "px"

 </script>



<svg bind:clientWidth={svgWidth} width="{w}" height="{h}">
  <g style:transform="translate({transX}, {transY})">
    {@render children()}		
  </g>
</svg>




<style>

</style>