<script>
  import { setContext } from "svelte";

  let { children } = $props()

  let i = $state(-1)
  let x = $state(0)
  let y = $state(0)

  setContext("tooltip", {
    getIndex() { return i },
    getMousePos() { return {x: x, y: y}},

    setIndex(idx) { i = idx },
    setMousePos(mouseX, mouseY) { x = mouseX; y = mouseY}
  })
</script>

{@render children?.()}