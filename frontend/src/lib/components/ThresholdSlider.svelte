<script>

  import { getContext } from "svelte";
  import ComparatorChooser from "./ComparatorChooser.svelte";
	import { range } from "d3";

  let { 
    step = 1, 
    offset = 10,
    width = 8,
    buttonRadius = 8, 
    stroke = "black", 
    fill = "none",
    selectedFill = "steelblue",
    buttonFill = "black", 
    buttonStroke = "black", 
    threshStroke = "black",
    textColour = "black",
    whichComparators = {gt: true, ge: true, eq: true, le: true, lt: true, between: true},
    children
  } = $props()
	    
  const { x, y } = getContext("data")
  const { updateThresh, updateComparator, getComparator } = getContext("probs")

  const xScale = $derived(x())
  const yScale = $derived(y())
  let selectedComparator = $derived(getComparator())
  let rangeSlider = $derived(selectedComparator === "between")

  let sliderDomainX = $derived([xScale.range()[1] + offset, xScale.range()[1] + offset + width])
  let sliderDomainY = $derived([yScale.range()[1], yScale.range()[0]])

  let buttonX = $derived(sliderDomainX[0] + (sliderDomainX[1] - sliderDomainX[0]) / 2)
  let buttonY = $derived(
    ["lt", "le"].includes(selectedComparator) ? sliderDomainY[0] : sliderDomainY[1]
  )
  let buttonY1 = $derived(rangeSlider ? sliderDomainY[0] : null)

  let buttonYpos = $state()
  let screenYpos = $state()
  let buttonY1pos = $state()

  let steps = $derived.by(() => {
    const start = yScale.domain()[0]
    const end = yScale.domain()[1]
    let currentStep = start
    const steps = []
    while (currentStep <= end) {
      steps.push(currentStep)
      currentStep += step
    }
    return steps
  })

  let thresh = $derived(yScale.invert(buttonYpos))
  let thresh1 = $derived(yScale.invert(buttonY1pos))
  let threshLabel = $derived.by(() => {
    if (!steps) return
    const diff = steps.map(d => Math.abs(d - thresh))
    return steps[diff.indexOf(Math.min(...diff))]
  })
  let thresh1Label = $derived.by(() => {
    const diff = steps.map(d => Math.abs(d - thresh1))
    return steps[diff.indexOf(Math.min(...diff))]
  })

  let threshLinePos = $derived(yScale(threshLabel)) 
  let thresh1LinePos = $derived(yScale(thresh1Label)) 

  // reset slider when new data come in 
  $effect(() => {
    yScale
    buttonYpos = buttonY
    buttonY1pos = buttonY1
  }) 


  // update the threshold used to compute the probabilities
  $effect(() => {
    updateThresh(rangeSlider ? [threshLabel, thresh1Label] : threshLabel)
  })
    
  let buttonPressed = false
  let buttonPressed1 = false
  let origin

  let buttonInUse = $state("#button")

  function handleMouseDown(e) {
    buttonPressed = true
    buttonInUse = "#button"
    let buttonPos = e.clientY
    if (!origin) {
      origin = buttonPos - buttonY
    }
    buttonYpos = buttonPos - origin
  }

  function handleMouseDown1(e) {
    buttonPressed1 = true
    buttonInUse = "#button1"
    let buttonPos = e.clientY
    if (!origin) {
      origin = buttonPos - buttonY1
    }
    buttonY1pos = buttonPos - origin
  }


  function handleMouseMove(e) {
    if (buttonPressed) {
      buttonYpos = e.clientY - origin
      let posLimit = rangeSlider ? buttonY1pos + buttonRadius * 2 : sliderDomainY[0]
      if (buttonYpos <= posLimit) {
        buttonYpos = posLimit
      }
      if (buttonYpos > sliderDomainY[1]) {
        buttonYpos = sliderDomainY[1]
      }
    }
  }

   function handleMouseMove1(e) {
    if (buttonPressed1) {
      buttonY1pos = e.clientY - origin
      if (buttonY1pos <= sliderDomainY[0]) {
        buttonY1pos = sliderDomainY[0]
      }
      let posLimit = rangeSlider ? buttonYpos - buttonRadius * 2 : sliderDomainY[1]
      if (buttonY1pos >= posLimit) {
        buttonY1pos = posLimit
      }
    }
  }


  function handleMouseUp(e) {
    buttonPressed = false
    buttonPressed1 = false
  }

</script>

<svelte:window onmouseup={handleMouseUp} />

<g onmouseleave={handleMouseUp}>
  <rect
    x = {sliderDomainX[0]} 
    y = {sliderDomainY[0]} 
    width = {sliderDomainX[1] - sliderDomainX[0]} 
    height = {sliderDomainY[1]} 
    rx = {(sliderDomainX[1] - sliderDomainX[0]) / 2}
    {stroke} 
    {fill}
    stroke-width = "1"
  />
  <rect
    x = {sliderDomainX[0] + 1} 
    y = {
      selectedComparator === "gt" || selectedComparator === "ge" 
      ? sliderDomainY[0]
      : selectedComparator === "lt" || selectedComparator === "le"
        ? buttonYpos
        : buttonY1pos
    }
    width = {sliderDomainX[1] - sliderDomainX[0] - 2} 
    height = {
      selectedComparator === "gt" || selectedComparator === "ge" 
        ? buttonYpos
        : selectedComparator === "lt" || selectedComparator === "le"
          ? sliderDomainY[1] - buttonYpos
          : buttonYpos - buttonY1pos
    } 
    rx = {(sliderDomainX[1] - sliderDomainX[0]) / 2}
    fill = {selectedFill}
  />

  <!-- Invisbile button to take account of sliding out of small slider button -->

  <circle onmousemove={handleMouseMove} onmouseup={handleMouseUp}
    cy = {buttonYpos} 
    cx = {buttonX} 
    r = {buttonRadius * 4}
    fill-opacity="0"
    id = "button"
  />

  <circle onmousemove={handleMouseMove1} onmouseup={handleMouseUp}
    cy = {buttonY1pos} 
    cx = {buttonX} 
    r = {buttonRadius * 4}
    fill = {rangeSlider ? "white" : "none"}
    fill-opacity="0"
    id = "button1"
  />


  <circle onmousedown={handleMouseDown} onmousemove={handleMouseMove} onmouseup={handleMouseUp}
    cy = {buttonYpos} 
    cx = {buttonX} 
    r = {buttonRadius}
    fill = {buttonFill} 
    stroke = {buttonStroke}
  />

  <circle onmousedown={handleMouseDown1} onmousemove={handleMouseMove1} onmouseup={handleMouseUp}
    cy = {buttonY1pos} 
    cx = {buttonX} 
    r = {buttonRadius}
    fill = {rangeSlider ? buttonFill : "none"}
    stroke = {rangeSlider ? buttonStroke : "none"}
  />


  <text 
    x={buttonX + buttonRadius + 3} 
    y={buttonYpos} 
    fill={textColour} 
    alignment-baseline="middle"
    pointer-events="none"
  >
    {Number.isInteger(step) ? threshLabel : Number.parseFloat(threshLabel).toFixed(1)}
  </text>

  <text 
    x={buttonX + buttonRadius + 3} 
    y={buttonY1pos} 
    fill={rangeSlider ? textColour : "none"} 
    alignment-baseline="middle"
    pointer-events="none"
  >
  {Number.isInteger(step) ? thresh1Label : Number.parseFloat(thresh1Label).toFixed(1)}
  </text>

</g>
<use xlink:href="buttonInUse" />

<ComparatorChooser {whichComparators} offsetHorizontal={25} insertFromLeft={false} offsetVertical={-33} fontWeight="bold"/>

{@render children?.()}


  <g>
    {#if thresh}
      <line 
        x1 = {xScale.range()[0]} 
        x2 = {xScale.range()[1]}
        y1= {threshLinePos} 
        y2= {threshLinePos} 
        stroke={threshStroke} 
        stroke-dasharray="3 6"
      />  
    {/if}

    {#if thresh1}
      <line 
        x1 = {xScale.range()[0]} 
        x2 = {xScale.range()[1]}
        y1= {thresh1LinePos} 
        y2= {thresh1LinePos} 
        stroke={rangeSlider ? threshStroke : "none"} 
        stroke-dasharray="3 6"
      />        
    {/if}
        
  </g>

