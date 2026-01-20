<script>

  import { getContext } from "svelte";

  let { children } = $props()
  let overlay;
  let x = $state()
  let y = $state()

  let { setMousePos } = getContext("tooltip")
  $effect(() => setMousePos(x, y))

  $effect(() => {
    let container = document.getElementById('overlay-container');
    if (!container) {
      container = document.body.appendChild(document.createElement('div'));
      container.id = 'overlay-container';
    }
    container.appendChild(overlay)

    return () => {
      while (container.firstChild){
        container.removeChild(container.firstChild)
      }
    }
  });
</script>

<svelte:body onmousemove={(e) => {x = e.clientX; y = e.clientY}} />

<div bind:this={overlay} class="overlay">
  {@render children?.()}
</div>
