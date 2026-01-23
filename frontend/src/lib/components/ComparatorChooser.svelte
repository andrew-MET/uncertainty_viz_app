<script>

  import { getContext } from "svelte";

  let { 
    offsetHorizontal = 0, 
    offsetVertical = 0,
    insertFromLeft = true,
    insertFromTop = true, 
    vertical = false, 
    size = 22, 
    gap = 3,
    fontSize = "1.2em",
    fontWeight = "normal",
    comparatorChosenFill = "#CCC",
    comparatorFill = "#EEE",
    comparatorChosenText = "#333",
    comparatorText = "#111",
    comparatorStroke = "#333",
    comparatorChosenStroke = "#EEE",
    whichComparators 
  } = $props()

  const { getComparator, updateComparator } = getContext("probs")
  const { x, y } = getContext("data")

  let xRange = $derived(x().range())
  let yRange = $derived(y().range())

  let horizontalEdge = $derived(
    insertFromLeft
      ? xRange[0] + offsetHorizontal
      : xRange[1] + offsetHorizontal - size
  )

  let verticalEdge = $derived(
    insertFromTop
      ? yRange[1] + offsetVertical
      : yRange[0] + offsetVertical - size
  )

  const comparatorsToUse = []
  if (typeof gt !== "undefined" && gt === true) {
    comparatorsToUse.push("gt")
  }
  if (typeof ge !== "undefined" && ge === true) {
    comparatorsToUse.push("ge")
  }
  if (typeof eq !== "undefined" && eq === true) {
    comparatorsToUse.push("eq")
  }
  if (typeof le !== "undefined" && le === true) {
    comparatorsToUse.push("le")
  }
  if (typeof lt !== "undefined" && lt === true) {
    comparatorsToUse.push("lt")
  }
  if (typeof between !== "undefined" && between === true) {
    comparatorsToUse.push("between")
  }

  let comparators = $state([
    {label: "gt", symbol: "&gt;"},
    {label: "ge", symbol: "&ge;"},
    {label: "eq", symbol: "&equals;"},
    {label: "le", symbol: "&le;"},
    {label: "lt", symbol: "&lt;"},
    {label: "between", symbol: "[ ]"}
  ])

  const reversePosition = ((vertical && !insertFromTop) || (!vertical && !insertFromLeft))
    ? true
    : false

  let selectedComparator = $state(getComparator())

  comparators.forEach((comparator, i) => {
    comparators[i] = {
      ...comparators[i],
      position: reversePosition ? i : comparators.length - i - 1,
      chosen: comparator.label === selectedComparator, 
      use: comparatorsToUse.filter(d => d === comparator.label).length > 0
    }
  })

  // update the comparator used to compute the probabilities
  $effect(() => {
    updateComparator(selectedComparator)
  })

  function handleComparatorClick(e) {
    comparators.forEach((element, i) => {
      comparators[i].chosen = element.label === e.target.id ? true : false      
    });
    selectedComparator = e.target.id
  }

</script>

<g>
  {#each comparators as comparator}
    <rect 
      x = {
        vertical
          ? insertFromLeft ? horizontalEdge : horizontalEdge
          : insertFromLeft
            ? horizontalEdge + comparator.position * (size + gap)
            : horizontalEdge - comparator.position * (size + gap)
      }
      y = {
        vertical
          ? insertFromTop >= 0 
            ? verticalEdge + comparator.position * (size + gap)
            : verticalEdge - comparator.position * (size + gap)
          : insertFromTop >= 0 ? verticalEdge : verticalEdge 
      }
      id = {comparator.label} 
      width = {size} 
      height = {size} 
      fill = {comparator.chosen ? comparatorChosenFill : comparatorFill} 
      stroke = {comparator.chosen ? comparatorChosenStroke : comparatorStroke}
      rx = "4"
      onclick={handleComparatorClick}
    /> 

    <text 
      x = {
      vertical 
        ? horizontalEdge + size / 2 
        : insertFromLeft 
          ? horizontalEdge + size / 2 + comparator.position * (size + gap)
          : horizontalEdge + size / 2 - comparator.position * (size + gap)
      }
      y = {
        vertical
          ? insertFromTop 
            ? verticalEdge + size / 2 + comparator.position * (size + gap) + 1
            : verticalEdge + size / 2 - comparator.position * (size + gap) + 1
          : verticalEdge + size / 2 + 1
      }
      fill={comparator.chosen ? comparatorChosenText : comparatorText} 
      text-anchor="middle" 
      alignment-baseline="middle"
      pointer-events="none"
      font-size={fontSize}
      font-weight={fontWeight}
    >
      {@html comparator.symbol}
    </text>
  {/each}
</g>
