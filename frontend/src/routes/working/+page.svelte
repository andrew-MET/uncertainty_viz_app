<script>
  import { MapLibre, Marker } from 'svelte-maplibre-gl'
  import maplibregl from 'maplibre-gl'
  import { utcParse } from 'd3';

  import { getTimeseries } from './timeseries.remote';
	import QuantilePlumes from '$lib/components/QuantilePlumes.svelte';
	import { resolveRoute } from '$app/paths';
	import { isHttpError } from '@sveltejs/kit';


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
    // temp: ["#F4AC90", "#E96245", "#A62700"],
    temp: ["#FCC", "#F88", "#F22"],
    wind: ["#EFEDF5", "#BCBDDC", "#756BB1"],
    cloud: ["#CCC", "#999", "#666"],
    press: ["#FFFDD0", "#FFFF8F", "#FF0"],
    precip: ["#DEEBF7", "#9ECAE1", "#3182BD"]
  }
  
  let colourPalette = $derived(colours[selectedParam.name])

  let queryData = $derived({
    lon: lnglat.lng,
    lat: lnglat.lat,
    dttm: dttm,
    param: selectedParam.name,
    model: model,
    accum: selectedParam.accum
  })

  const data = $derived(await getTimeseries(queryData))

  const xAccessor = d => utcParse("%Y-%-m-%d %H:%M:%S")(d.dttm)
  


</script>

<div class="container">

  <div>
    <div>
      <select bind:value={selectedParam}>
        {#each params as param}
          <option value={param}>{param.text}</option>
        {/each}
      </select>
    </div>
    <h1>Lon: {lnglat.lng.toFixed(2)}, Lat: {lnglat.lat.toFixed(2)}</h1>
    {#if data}
      <QuantilePlumes
        {data}  
        {xAccessor}
        xScale = "utc"
        marginRight = {50}
        marginLeft = {50}
        quantileFill = {colourPalette}
        quantileStroke = {["#CCC", "#CCC", "#CCC"]}
        tooltip = "dotplot"
      />
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
      <Marker { lnglat }/>
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
