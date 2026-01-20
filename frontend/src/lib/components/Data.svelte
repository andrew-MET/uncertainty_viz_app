<script>

  import { getScaleFunc } from "$lib/utils";
  import { setContext, getContext } from "svelte";
  import { extent, scaleUtc } from "d3"

  let { 
    data, 
    xAccessor, 
    yAccessor,
    xScale = "linear",
    yScale = "linear",
    xFixedLower = false,
    xFixedUpper = false,
    yFixedLower = false,
    yFixedUpper = false,
    children
  } = $props()

  // w() from context (maybe h too... ) and data from props are 
  // state variables so anything computed from them needs to have 
  // the $derived() rune  
  let { w, h } = getContext("svgDims")

  const xRange = $derived([0, w()])
  const yRange = $derived([h(), 0])

  const xDomain = $derived(extent(data.map(d => xAccessor(d)).flat()))
  const yDomain = $derived(extent(data.map(d => yAccessor(d)).flat()))

  const xScaleFun = $derived(getScaleFunc(xScale)().domain(xDomain).range(xRange).nice())
  const yScaleFun = $derived(getScaleFunc(yScale)().domain(yDomain).range(yRange).nice())

  const xNiceDomain = $derived(xScaleFun.domain())
  const yNiceDomain = $derived(yScaleFun.domain())

  const xPlotScale = $derived.by(() => {
    const xDom = []
    if (xFixedLower) {
      xDom[0] = xDomain[0]
    } else {
      xDom[0] = xNiceDomain[0]
    }
    if (xFixedUpper) {
      xDom[1] = xDomain[1]
    } else {
      xDom[1] = xNiceDomain[1]
    }
    return xScaleFun.domain(xDom).range(xRange)
  })

  const yPlotScale = $derived.by(() => {
    const yDom = []
    if (yFixedLower) {
      yDom[0] = yDomain[0]
    } else {
      yDom[0] = yNiceDomain[0]
    }
    if (yFixedUpper) {
      yDom[1] = yDomain[1]
    } else {
      yDom[1] = yNiceDomain[1]
    }
    return yScaleFun.domain(yDom).range(yRange)
  })
  
  setContext("data", {
    data() { return data },
    x() { return xPlotScale },
    y() { return yPlotScale }
  })

</script>



{@render children?.()}