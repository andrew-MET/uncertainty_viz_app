<script>
  import { MapLibre, Marker } from 'svelte-maplibre-gl'
  import maplibregl from 'maplibre-gl'
  import { utcParse, interpolateTurbo } from 'd3';

  import { getTimeseries } from './timeseries.remote';
	import QuantilePlumes from '$lib/components/QuantilePlumes.svelte';
	import { resolveRoute } from '$app/paths';
	import { isHttpError } from '@sveltejs/kit';
	import StackedProb from '$lib/components/StackedProb.svelte';
	import MultLineWithHighlight from '$lib/components/MultLineWithHighlight.svelte';
	import Spaghetti from '$lib/components/Spaghetti.svelte';


  let lnglat = $state(new maplibregl.LngLat(0, 0));
  let dttm = $state("2025120100")
  let model = $state("chunked")

  const params = [
    {text: "2m Temperature", name: "temp"},
    {text: "10m Wind Speed", name: "wind"},
    {text: "100m Wind Speed", name: "wind100"},
    {text: "Cloud Percent", name: "cloud"},
    {text: "Sea Level Pressure", name: "press"},
    {text: "Total Precipitation", name: "precip"},
    {text: "1h Precipitation", name: "precip", accum: 1},
    {text: "3h Precipitation", name: "precip", accum: 3},
    {text: "6h Precipitation", name: "precip", accum: 6},
    {text: "12h Precipitation", name: "precip", accum: 12}
  ]

  let selectedParam = $state(params[0])

  const paramStyles = {
    temp: {
      plume: ["#FCC", "#F88", "#F22"], 
      stack: ["#F22", "#F55", "#F88", "#FBB", "#FDD"], 
      spag: {colour: "#F88", highlight: "#F22", noHighlight: "#FCC"},
      step: 0.1 
    },
    wind: {
      plume: ["#EFEDF5", "#BCBDDC", "#756BB1"], 
      stack: ["#54278F","#756BB1","#9E9AC8","#BCBDDC","#DADAEB","#F2F0F7"], 
      spag: {colour: "#BCBDDC", highlight: "#756BB1", noHighlight: "#EFEDF5"},
      step: 0.1
    },
    wind100: {
      plume: ["#EFEDF5", "#BCBDDC", "#756BB1"], 
      stack: ["#54278F","#756BB1","#9E9AC8","#BCBDDC","#DADAEB","#F2F0F7"], 
      spag: {colour: "#BCBDDC", highlight: "#756BB1", noHighlight: "#EFEDF5"},
      step: 0.1
    },
    cloud: {
      plume: ["#CCC", "#999", "#666"], 
      stack: ["#252525","#636363","#969696","#BDBDBD","#D9D9D9","#F7F7F7"], 
      spag: {colour: "#999", highlight: "#666", noHighlight: "#CCC"},
      step: 1 
    },
    press: {
      plume: ["#FFFFB2", "#FD8D3C", "#BD0026"], 
      stack: ["#BD0026","#F03B20","#FD8D3C","#FECC5C","#FFFFB2"], 
      spag: {colour: "#FD8D3C", highlight: "#BD0026", noHighlight: "#FFFFB2"},
      step: 1 
    },
    precip: {
      plume: ["#DEEBF7", "#9ECAE1", "#3182BD"], 
      stack: ["#08519C","#3182BD","#6BAED6","#9ECAE1","#C6DBEF","#EFF3FF"], 
      spag: {colour: "#9ECAE1", highlight: "#3182BD", noHighlight: "#DEEBF7"},
      step: 0.1 
    }
  }
  
  let paramStyle = $derived(paramStyles[selectedParam.name])

  let queryData = $derived({
    lon: lnglat.lng,
    lat: lnglat.lat,
    dttm: dttm,
    param: selectedParam.name,
    //model: model,
    accum: selectedParam.accum
  })

  const data = $derived(await getTimeseries(queryData))

  const xAccessor = d => utcParse("%Y-%-m-%d %H:%M:%S")(d.dttm)

  const plotTypes = [
    {name: "plume", text: "Plume"}, 
    {name: "box", text: "Box plot"}, 
    {name: "stack", text: "Stacked Probability"},
    {name: "spag", text: "All members"}
  ]

  let selectedPlot = $state(plotTypes[0])

</script>

<div class="container">

  <div class="panel">
    <div style="margin-left: 50px;">
      <select bind:value={selectedParam}>
        {#each params as param}
          <option value={param}>{param.text}</option>
        {/each}
      </select>
      <select bind:value={selectedPlot}>
        {#each plotTypes as plotType}
          <option value={plotType}>{plotType.text}</option>
        {/each}
      </select>
    </div>
    <h1 style="margin-left: 50px;">Lon: {lnglat.lng.toFixed(2)}, Lat: {lnglat.lat.toFixed(2)}</h1>
    
    {#if data}

      {#if selectedPlot.name === "plume"}
        <QuantilePlumes
          {data}  
          {xAccessor}
          h = {300}
          xScale = "utc"
          marginRight = {70}
          marginLeft = {50}
          marginTop = {40}
          marginBottom = {10}
          quantileFill = {paramStyle.plume}
          quantileStroke = {["#CCC", "#CCC", "#CCC"]}
          xAxisProps = {{labels: false}}
          tooltip = "dotplot"
          threshSlider={true}
          threshSliderProps={
            {
              threshStroke: "#666", buttonFill: "steelblue", offset: 15, textColour: "#333", stroke: "#333", 
              step: paramStyle.step 
            }
          }
          probColsH=100
          probColsMarginRight=70
          probColsMarginLeft=50
          probColsMarginTop=5
          probColsYaxisProps={{xOffset: -8, numTicks: 3, colour: "#333"}}
          probColsXaxisProps={{colour: "#333"}}
          probColsProps={{fillPalette: interpolateTurbo}}
        />
      {:else if selectedPlot.name === "box"}
        <StackedProb
          {data}
          {xAccessor}
          h = {300}
          xScale = "utc"
          marginRight = {70}
          marginLeft = {50}
          marginTop = {40}
          marginBottom = {10}
          quantilePairs = { [ [ 0, 1 ], [ 0.1, 0.9 ], [ 0.25, 0.75 ] ] }
          quantileFill = { paramStyle.plume }
          extendToZero = { false }
          colWidth = { [0.1, 0.6, 0.9] }
          yAxisProps = { { xOffset: -15 } }
          xAxisProps = {{labels: false}}
          tooltip = "dotplot"
          threshSlider={true}
          threshSliderProps={
            {
              threshStroke: "#666", buttonFill: "steelblue", offset: 15, textColour: "#333", stroke: "#333", 
              step: paramStyle.step
            }
          }
          probColsH=100
          probColsMarginRight=70
          probColsMarginLeft=50
          probColsMarginTop=5
          probColsYaxisProps={{xOffset: -15, numTicks: 3, colour: "#333"}}
          probColsXaxisProps={{colour: "#333"}}
          probColsProps={{fillPalette: interpolateTurbo}}
        />
      {:else if selectedPlot.name === "stack"}
        <StackedProb
          {data}
          {xAccessor}
          h = {300}
          xScale = "utc"
          marginRight = {70}
          marginLeft = {50}
          marginTop = {40}
          marginBottom = {10}
          yAxisProps = { { xOffset: -15 } }
          extendToZero = { paramStyle.stack.length > 5}
          quantileFill = { paramStyle.stack.length > 5 ? paramStyle.stack.slice() : paramStyle.stack }
          toZeroFill = {paramStyle.stack[0]}
          median = { false }
          xAxisProps = {{labels: false}}
          tooltip = "dotplot"
          threshSlider={true}
          threshSliderProps={
            {
              threshStroke: "#666", buttonFill: "steelblue", offset: 15, textColour: "#333", stroke: "#333", 
              step: paramStyle.step
            }
          }
          probColsH=100
          probColsMarginRight=70
          probColsMarginLeft=50
          probColsMarginTop=5
          probColsYaxisProps={{xOffset: -15, numTicks: 3, colour: "#333"}}
          probColsXaxisProps={{colour: "#333"}}
          probColsProps={{fillPalette: interpolateTurbo}}
        />
      {:else if selectedPlot.name === "spag"}
        <Spaghetti
          {data}
          {xAccessor}
          h = {300}
          xScale = "utc"
          marginRight = {70}
          marginLeft = {50}
          marginTop = {40}
          marginBottom = {10}
          yAxisProps = { { xOffset: -8 } }
          xAxisProps = {{labels: false}}
          colour = {paramStyle.spag.colour}
          highlightColour = {paramStyle.spag.highlight}
          noHighlightColour = {paramStyle.spag.noHighlight}
          threshSlider={true}
          threshSliderProps={
            {
              threshStroke: "#666", buttonFill: "steelblue", offset: 15, textColour: "#333", stroke: "#333", 
              step: paramStyle.step
            }
          }
          probColsH=100
          probColsMarginRight=70
          probColsMarginLeft=50
          probColsMarginTop=5
          probColsYaxisProps={{xOffset: -15, numTicks: 3, colour: "#333"}}
          probColsXaxisProps={{colour: "#333"}}
          probColsProps={{fillPalette: interpolateTurbo}}
        />
      {/if}

    {:else}
      <p style="margin-left: 50px;">No Data!</p>
    {/if}
  </div>

  <div class="panel">
    <MapLibre 
      class="map-container" 
      style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
      zoom={4}
      center={{ lng: 10, lat: 50}}
      onmousedown={(ev) => {        
        lnglat = ev.lngLat; // cursor location
      }}
    >
      <Marker lnglat={ lnglat }/>
    </MapLibre>
  </div>

</div>

<style>
  .container {
    display: grid;
    grid-template-columns: 2fr 1fr;
    margin: 5% 5%;
    gap: 10px;
  }

  .panel {
    border: 1px solid #CCC;
    border-radius: 10px;
    padding: 10px;
  }

  :global(.map-container) {
    height: 800px;
    padding: auto 50px auto;
  }


</style>
