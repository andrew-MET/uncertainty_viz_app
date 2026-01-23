<script>

  import { binMembers, quantiles } from "$lib/utils";

  import ProbData from "$lib/components/ProbData.svelte";
  import Svg from "$lib/components/Svg.svelte"
  import Data from "$lib/components/Data.svelte";
  import Rect from "$lib/components/Rect.svelte";
  import Xhover from "$lib/components/Xhover.svelte";
  import Xaxis from "$lib/components/Xaxis.svelte";
  import Yaxis from "$lib/components/Yaxis.svelte";
	import ThresholdSlider from "$lib/components/ThresholdSlider.svelte";
  import ProbCols from "$lib/components/ProbCols.svelte"
	import Crossbar from "$lib/components/Crossbar.svelte";
  import WithTooltip from "$lib/components/WithTooltip.svelte";
  import Tooltip from "$lib/components/Tooltip.svelte";

  let { 
    data, 
    xAccessor,
    yAccessor,
    quantilePairs     = [ [0, 0.2], [0.2, 0.4], [0.4, 0.6], [0.6, 0.8], [0.8, 1] ],
    quantileFill      = [ "#0570b0", "#3690c0", "#74a9cf", "#a6bddb", "#d0d1e6" ],
    quantileStroke    = "none",
    extendToZero      = true,
    toZeroFill        = "#034e7b",
    colWidth          = 0.9,
    toZeroColWidth    = 0.9,
    median            = true,
    medianBarWidth    = 0.9,
    medianStroke      = "black",
    medianWidth       = 2,
    h                 = 250,
    marginTop         = 10,
    marginRight       = 10,
    marginBottom      = 30, 
    marginLeft        = 30,
    xScale            = "linear",
    yFixedLower       = false,
    threshSlider      = false,
    threshSliderProps = {
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
      textColour:   "black",
      whichComparators: {gt: true, ge: true, eq: true, le: true, lt: true, between: true}
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
      hoverOpacity:     0.1, 
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

  const allQuantiles = $derived([...new Set(quantilePairs.flat())])
  if (median && !allQuantiles.includes(0.5)) {
    allQuantiles.push(0.5)
  }
  const quantileData = $derived(quantiles(data, allQuantiles))
  const maxQuantile = $derived(Math.max(...allQuantiles).toString())
  const minQuantile = $derived(Math.min(...allQuantiles).toString())

  const yAccessorData = yAccessor ? yAccessor : d => [d[minQuantile], d[maxQuantile]]

  if (!Array.isArray(colWidth)) {
    colWidth = Array(extendToZero ? quantilePairs.length + 1 : quantilePairs.length).fill(colWidth)
  }

  let xHover = $state(false)
  if (tooltip === "dotplot") {
    xHover = true
  } 

  const binnedData = $derived(xHover ? binMembers(data, 10) : [])

</script>

<ProbData {data}>

  <div>
    <WithTooltip>
      <Svg {h} {marginTop} {marginRight} {marginBottom} {marginLeft}>
        <Data data={quantileData} {xAccessor} yAccessor = {yAccessorData} {xScale} {yFixedLower}>
          
          {#each quantilePairs as quantilePair, i}
            <Rect 
              {xAccessor} 
              y0Accessor = {d => d[quantilePair[0].toString()]} 
              y1Accessor = {d => d[quantilePair[1].toString()]} 
              fillColour = {quantileFill[i]}
              colour     = {quantileStroke}
              colWidth   = {colWidth[i]}
            />
          {/each}

          {#if extendToZero}
            <Rect 
              {xAccessor} 
              y0Accessor = {d => 0} 
              y1Accessor = {d => d[quantilePairs[0][0].toString()]} 
              fillColour = {toZeroFill}
              colour     = {quantileStroke}
              colWidth   = {toZeroColWidth}
            />          
          {/if}
          
          {#if median}
            <Crossbar {xAccessor} yAccessor = {d => d["0.5"]} strokeWidth={medianWidth} colour={medianStroke} barWidth={medianBarWidth}/>
          {/if}

          {#if xHover}
            <Xhover {xAccessor} {...xHoverProps}/>      
          {/if}

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
      <Tooltip data={binnedData} tooltipWidth={200} opacity={0.9} background="#EEE" textColour="#333" border="#333"/>
    </WithTooltip>
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
