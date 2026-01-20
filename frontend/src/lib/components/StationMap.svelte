<script>

  import { getContext } from "svelte";
  import { MapLibre, Marker, Popup } from "svelte-maplibre";
  import stations from "$lib/data/stn_lonlat.json"

  const mapCentre = stations.filter(d => d.name === "GAVLE")[0]

  let selected = $state(-1)
  
  const stationContext = getContext("stationContext")

  $effect(() => {
    stationContext.updateStation(selected >= 0 ? stations[selected].name : undefined)
  })

</script>

<MapLibre
  center={[mapCentre.lon - 0.25, (mapCentre.lat - 0.3)]}
  zoom={7}
  minZoom={5}
  class="map"
  style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
>
  {#each stations as { lon, lat, name }, i (name)}
    <Marker lngLat={[lon, lat]} onclick={() => selected = i} class="marker">
      <Popup openOn="hover" offset={[0, -10]}>
        <div class="popup">
          <h4>{name}</h4>
        </div>
      </Popup>
    </Marker>
  {/each}

</MapLibre>

<style>
  
  :global(.map) {
    height: 100%;
  }

  .popup {
    display: flex;
    flex-direction: column;
  }

  .popup h4 {
    align-self: center;
    margin-top: 1px;
    margin-bottom: 2px;
    color: #111
  }

  :global(.marker) {
    height: 20px; 
    width: 20px;
    background-color: #438710;
    border-radius: 10px;
  }
</style>