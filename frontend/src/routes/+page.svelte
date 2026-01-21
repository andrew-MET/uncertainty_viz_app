<script>
  import { MapLibre, Marker } from 'svelte-maplibre-gl'
  import maplibregl from 'maplibre-gl'
  import { utcParse } from 'd3';

  import { getTimeseries } from './timeseries.remote';
	import QuantilePlumes from '$lib/components/QuantilePlumes.svelte';
	import { resolveRoute } from '$app/paths';
	import { isHttpError } from '@sveltejs/kit';
	import StackedProb from '$lib/components/StackedProb.svelte';
	import MultLineWithHighlight from '$lib/components/MultLineWithHighlight.svelte';


  let lnglat = $state(new maplibregl.LngLat(0, 0));
  let dttm = $state("2025120100")
  let model = $state("chunked")

  const params = [
    {text: "2m Temperature", name: "temp"},
    {text: "10m Wind Speed", name: "wind"},
    {text: "Cloud Fraction", name: "cloud"},
    {text: "Sea Level Pressure", name: "press"},
    {text: "Total Precipitation", name: "precip"},
    {text: "1h Precipitation", name: "precip", accum: 1},
    {text: "3h Precipitation", name: "precip", accum: 3},
    {text: "6h Precipitation", name: "precip", accum: 6},
    {text: "12h Precipitation", name: "precip", accum: 12}
  ]

  let selectedParam = $state(params[0])

  const colours = {
    temp: {plume: ["#FCC", "#F88", "#F22"], stack: ["#F22", "#F55", "#F88", "#FBB", "#FDD"] },
    wind: {plume: ["#EFEDF5", "#BCBDDC", "#756BB1"], stack: ["#54278F","#756BB1","#9E9AC8","#BCBDDC","#DADAEB","#F2F0F7"]},
    cloud: {plume: ["#CCC", "#999", "#666"], stack: ["#252525","#636363","#969696","#BDBDBD","#D9D9D9","#F7F7F7"] },
    press: {plume: ["#FFFDD0", "#FFFF8F", "#FF0"], stack: ["#BD0026","#F03B20","#FD8D3C","#FECC5C","#FFFFB2"] },
    precip: {plume: ["#DEEBF7", "#9ECAE1", "#3182BD"], stack: ["#08519C","#3182BD","#6BAED6","#9ECAE1","#C6DBEF","#EFF3FF"] }
  }
  
  let colourPalette = $derived(colours[selectedParam.name])

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
    {name: "stack", text: "Stacked Probability"}//,
    //{name: "spag", text: "All members"}
  ]

  let selectedPlot = $state(plotTypes[0])

</script>

<div class="container">

  <div>
    <div>
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
    <h1>Lon: {lnglat.lng.toFixed(2)}, Lat: {lnglat.lat.toFixed(2)}</h1>
    
    {#if data}

      {#if selectedPlot.name === "plume"}
        <QuantilePlumes
          {data}  
          {xAccessor}
          xScale = "utc"
          marginRight = {50}
          marginLeft = {50}
          quantileFill = {colourPalette.plume}
          quantileStroke = {["#CCC", "#CCC", "#CCC"]}
        />
      {:else if selectedPlot.name === "box"}
        <StackedProb
          {data}
          {xAccessor}
          xScale = "utc"
          marginRight = {50}
          marginLeft = {50}
          quantilePairs = { [ [ 0, 1 ], [ 0.1, 0.9 ], [ 0.25, 0.75 ] ] }
          quantileFill = { colourPalette.plume }
          extendToZero = { false }
          colWidth = { [0.1, 0.6, 0.9] }
          yAxisProps = { { xOffset: -15 } }
        />
      {:else if selectedPlot.name === "stack"}
        <StackedProb
          {data}
          {xAccessor}
          xScale = "utc"
          marginRight = {50}
          marginLeft = {50}
          yAxisProps = { { xOffset: -15 } }
          extendToZero = { colourPalette.stack.length > 5}
          quantileFill = { colourPalette.stack.length > 5 ? colourPalette.stack.slice() : colourPalette.stack }
          toZeroFill = {colourPalette.stack[0]}
          median = { false }
        />
      <!-- {:else}
        <p>{selectedPlot}</p> -->
      {/if}

    {:else}
      <p>No Data!</p>
    {/if}
  </div>

  <div>
    <MapLibre 
      class="map-container" 
      style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
      zoom={4}
      center={{ lng: 10.75, lat: 64.5}}
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
    grid-template-columns: 1.5fr 2fr;
    margin: 5% 5%;
  }

  :global(.map-container) {
    height: 800px;
    padding: auto 50px auto;
  }


</style>
