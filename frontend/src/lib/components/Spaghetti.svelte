<script>

  import { spaghetti, binMembers } from "$lib/utils";

  import ProbData from "$lib/components/ProbData.svelte";
  import Svg from "$lib/components/Svg.svelte"
  import Data from "$lib/components/Data.svelte";
  import MultLineWithHighlight from "./MultLineWithHighlight.svelte";
  import Xaxis from "$lib/components/Xaxis.svelte";
  import Yaxis from "$lib/components/Yaxis.svelte";
	import ThresholdSlider from "$lib/components/ThresholdSlider.svelte";
  import ProbCols from "$lib/components/ProbCols.svelte"

  let { 
    data, 
    xAccessor,
    yAccessors,
    colour             = "#777",
    highlightColour    = "#333",
    noHighlightColour  = "#CCC",
    h                  = 250,
    marginTop          = 10,
    marginRight        = 10,
    marginBottom       = 30, 
    marginLeft         = 30,
    xScale             = "linear",
    yFixedLower        = false,
    threshSlider       = false,
    threshSliderProps  = {
      step:         1, 
      offset:       10,
      width:        8,
      buttonRadius: 8, 
      stroke:       "black", 
      fill:         "none",
      selectedFill: "steelblue",
      buttonFill:   "black", 
      buttonStroke: "black", 
      threshStroke: "black",
      textColour:   "black"
    },

    xAxis      = true,
    xAxisProps = {
      colour:    "black", 
      numTicks:  10, 
      labels:    true, 
      labelSize: "0.75em", 
      yOffset:   0
    },

    yAxis      = true,
    yAxisProps = {
      colour:    "black", 
      numTicks:  5, 
      labels:    true, 
      labelSize: "0.75em", 
      xOffset:   -8  
    },

    tooltip     = "none",
    xHoverProps = {
      hoverFill:        "#CCC", 
      hoverOpacity:     0.5, 
      hoverStroke:      "none", 
      hoverStrokeWidth: 1
    },

    probCols             = false,
    probColsH            = 125,
    probColsMarginTop    = 10,
    probColsMarginRight  = 10,
    probColsMarginBottom = 30,
    probColsMarginLeft   = 30,
    probColsNumTicks     = 3,
    probColsProps        = {
      fillPalette: "steelblue", 
      stroke:      "black", 
      colWidth:     0.9  
    },
    probColsXaxis      = true,
    probColsXaxisProps = {
      colour:    "black", 
      numTicks:  10, 
      labels:    true, 
      labelSize: "0.75em", 
      yOffset:   0
    },
    probColsYaxis      = true,
    probColsYaxisProps = {
      colour:    "black", 
      numTicks:  3, 
      labels:    true, 
      labelSize: "0.75em", 
      yOffset:   -8
    }

  } = $props()

  // data will likely always be a state variable


  const spagData = $derived(spaghetti(data))
  const members  = $derived(data ? Object.keys(data.data) : null)
  
  const yAccessorsData = $derived(yAccessors ? yAccessors : members.map(m => ({key: m, fun: d => d[m]})))
  $inspect(yAccessorsData)

  const binnedData = $derived(xHover ? binMembers(data, 10) : [])


</script>

<ProbData {data}>

  <div>
    <Svg {h} {marginTop} {marginRight} {marginBottom} {marginLeft}>
      <Data data={spagData} {xAccessor} yAccessor = {d => members.map(m => d[m])} {xScale} {yFixedLower}>
        <MultLineWithHighlight {xAccessor} yAccessors = {yAccessorsData} {colour} {highlightColour} {noHighlightColour} width="1" />
        {#if xAxis}
          <Xaxis {...xAxisProps}/>
        {/if}

        {#if yAxis}
          <Yaxis {...yAxisProps}/>
        {/if}

        {#if threshSlider}
          <ThresholdSlider {...threshSliderProps}/>
        {/if}
      </Data>
    </Svg>
  </div>

  {#if threshSlider}
    <div>
      <Svg 
        h={probColsH} 
        marginTop={probColsMarginTop}
        marginRight={probColsMarginRight}
        marginBottom={probColsMarginBottom}
        marginLeft={probColsMarginLeft}
      >
        <ProbCols {xAccessor} y1Accessor = {d => d.prob} y0Accessor = {d => 0} {...probColsProps}>
          {#if probColsXaxis}
            <Xaxis {...probColsXaxisProps}/>
          {/if}
          {#if probColsYaxis}
            <Yaxis {...probColsYaxisProps}/>
          {/if}
        </ProbCols>
      </Svg>            
    </div>
  {/if}


</ProbData>
